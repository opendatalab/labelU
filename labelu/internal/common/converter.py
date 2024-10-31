import base64
import json
import os
from zipfile import ZipFile
from PIL import Image, ImageDraw
from enum import Enum

from typing import List
from loguru import logger

from labelu.internal.common.color import colors
from labelu.internal.common.config import settings


class Format(str, Enum):
    JSON = "JSON"
    COCO = "COCO"
    MASK = "MASK"
    LABEL_ME = "LABEL_ME"


class Converter:
    def convert(
        self,
        config: dict,
        input_data: List[dict],
        out_data_dir: str,
        out_data_file_name_prefix: str,
        format: str,
    ) -> str:
        if format == Format.JSON.value:
            return self.convert_to_json(
                input_data=input_data,
                out_data_dir=out_data_dir,
                out_data_file_name_prefix=out_data_file_name_prefix,
            )
        elif format == Format.COCO.value:
            return self.convert_to_coco(
                config=config,
                input_data=input_data,
                out_data_dir=out_data_dir,
                out_data_file_name_prefix=out_data_file_name_prefix,
            )
        elif format == Format.MASK.value:
            return self.convert_to_mask(
                input_data=input_data,
                out_data_dir=out_data_dir,
                out_data_file_name_prefix=out_data_file_name_prefix,
            )
        elif format == Format.LABEL_ME.value:
            return self.convert_to_labelme(
                config=config,
                input_data=input_data,
                out_data_file_name_prefix=out_data_file_name_prefix,
                out_data_dir=out_data_dir,
            )

    def convert_to_json(
        self,
        input_data: List[dict],
        out_data_dir: str,
        out_data_file_name_prefix: str,
    ) -> str:
        out_data_dir.mkdir(parents=True, exist_ok=True)
        file_full_path = out_data_dir.joinpath("result.json")

        # every file result
        results = []
        for sample in input_data:
            data = json.loads(sample.get("data"))
            file = sample.get("file", {})
            
            # change skipped result is invalid
            annotated_result = json.loads(data.get("result"))
            if annotated_result and sample.get("state") == "SKIPPED":
                annotated_result["valid"] = False

            # change result struct
            if annotated_result:
                annotations = []
                for tool in annotated_result.copy().keys():
                    if tool.endswith("Tool"):
                        tool_results = annotated_result.pop(tool)
                        for tool_result in tool_results.get("result", []):
                            # 视频文件的标注结果已经保存了 label 键的值，不需要再做转换
                            if "label" not in tool_result:
                                tool_result["label"] = tool_result.pop("attribute", "")

                            tool_result.pop("sourceID", None)

                            if tool == "tagTool" or tool == "textTool":
                                tool_result.pop("label")

                            if "attribute" in tool_result:
                                tool_result.pop("attribute")

                        annotations.append(tool_results)

                annotated_result["annotations"] = annotations

            annotated_result_str = json.dumps(annotated_result, ensure_ascii=False)
            results.append(
                {
                    "id": sample.get("id"),
                    "result": annotated_result_str,
                    "url": file.get("url"),
                    "fileName": file.get("filename", "")[9:],
                }
            )

        # Serializing json
        json_object = json.dumps(results, default=str)
        with file_full_path.open("w") as outfile:
            outfile.write(json_object)

        logger.info("Export file path: {}", file_full_path)
        return file_full_path

    def convert_to_coco(
        self,
        config: dict,
        input_data: List[dict],
        out_data_dir: str,
        out_data_file_name_prefix: str,
    ) -> str:

        # result output file
        out_data_dir.mkdir(parents=True, exist_ok=True)
        file_full_path = out_data_dir.joinpath("result.json")

        # result struct
        result = {
            "images": [],
            "annotations": [],
            "categories": [],
        }

        # result catetory
        category_id = 0
        logger.info("get categories")
        for attr in config.get("attributes", []):
            category = {
                "id": category_id,
                "name": attr.get("value", ""),
                "supercategory": "",
            }
            result["categories"].append(category)
            category_id += 1
        tools_category = config.get("tools", [])
        for tool in tools_category:
            for attr in tool.get("config", {}).get("attributes", []):
                category = {
                    "id": category_id,
                    "name": attr.get("value", ""),
                    "supercategory": "",
                }
                result["categories"].append(category)
                category_id += 1

        logger.info("get categories map with id")
        category_name_map_id = {}
        for category in result["categories"]:
            category_name_map_id[category.get("name")] = category.get("id")

        # annotation index
        annotation_id = 0

        # for every annotation media
        for sample in input_data:
            annotation_data = json.loads(sample.get("data"))
            file = sample.get("file", {})
            logger.info("data is: {}", sample)

            # annotation result
            annotation_result = json.loads(annotation_data.get("result", {}))

            # coco image
            image = {
                "id": sample.get("id"),
                "fileName": file.get("filename", "")[9:],
                "width": annotation_result.get("width", 0),
                "height": annotation_result.get("height", 0),
                "valid": False
                if sample.get("state", "") == "SKIPPED"
                else annotation_result.get("valid", True),
                "rotate": annotation_result.get("rotate", 0),
            }
            result["images"].append(image)

            # every image may have multi tools
            tools = []
            if annotation_result.get("polygonTool", {}):
                tools.append(annotation_result.get("polygonTool"))
            if annotation_result.get("rectTool", {}):
                tools.append(annotation_result.get("rectTool"))

            for tool in tools:
                for tool_result in tool.get("result"):

                    bbox = []
                    segmentation = []
                    polygon_area = 0.0
                    # polygon tool
                    if tool.get("toolName") == "polygonTool":
                        x_coordinates = []
                        y_coordinates = []
                        for point in tool_result.get("points", []):
                            segmentation.append(point.get("x"))
                            segmentation.append(point.get("y"))
                            x_coordinates.append(point.get("x"))
                            y_coordinates.append(point.get("y"))

                        bbox = [
                            min(x_coordinates),
                            max(y_coordinates),
                            max(x_coordinates) - min(x_coordinates),
                            max(y_coordinates) - min(y_coordinates),
                        ]
                        polygon_area = _polygonArea(x_coordinates, y_coordinates)
                    elif tool.get("toolName") == "rectTool":
                        # rect
                        x = tool_result.get("x")
                        y = tool_result.get("y")
                        width = tool_result.get("width")
                        height = tool_result.get("height")
                        
                        if x is not None and y is not None and width is not None and height is not None:
                            bbox.extend([x, y, width, height])
                        polygon_area = tool_result.get("width", 0) * tool_result.get(
                            "height", 0
                        )

                    annotation = {
                        "image_id": sample.get("id"),
                        "id": annotation_id,
                        "iscrowd": tool_result.get("iscrowd", 0),
                        "segmentation": segmentation,
                        "area": polygon_area,
                        "bbox": bbox,
                        "category_id": category_name_map_id.get(
                            tool_result.get("label", ""), -1
                        ),
                        "order": tool_result.get("order", 0),
                    }

                    annotation_id += 1
                    result["annotations"].append(annotation)

        # Serializing json
        json_object = json.dumps(result, default=str)
        with file_full_path.open("w") as outfile:
            outfile.write(json_object)
        logger.info("Export file path: {}", file_full_path)
        return file_full_path

    def convert_to_mask(
        self,
        input_data: List[dict],
        out_data_dir: str,
        out_data_file_name_prefix: str,
    ) -> str:

        # result output file
        out_data_dir.mkdir(parents=True, exist_ok=True)

        polygon = []
        export_files = []
        color_list = []
        for sample in input_data:
            file = sample.get("file", {})
            if sample.get("state") != "DONE":
                continue
            annotation_data = json.loads(sample.get("data"))
            logger.info("data is: {}", sample)
            filename = file.get("filename")
            if filename and filename.split("/")[-1]:
                file_relative_path_base_name = filename.split("/")[-1].split(".")[0][9:]
            else:
                file_relative_path_base_name = "result"

            # annotation result
            annotation_result = json.loads(annotation_data.get("result", {}))
            if not annotation_result or not annotation_result.get("polygonTool", {}):
                continue

            # polygon tool
            polygons = []
            polygon_attribute = []
            for tool_result in annotation_result.get("polygonTool", {}).get(
                "result", []
            ):
                polygon = []
                for point in tool_result.get("points", []):
                    polygon.append(point.get("x"))
                    polygon.append(point.get("y"))
                polygons.append(polygon)
                polygon_attribute.append(tool_result.get("label", ""))

            width = annotation_result.get("width")
            height = annotation_result.get("height")

            # generate single change
            file_relative_path_model_l = f"{file_relative_path_base_name}-trainIds.png"
            file_full_path_model_l = out_data_dir.joinpath(file_relative_path_model_l)
            img_model_l = Image.new("L", (width, height), 0)
            for p in polygons:
                ImageDraw.Draw(img_model_l).polygon(p, outline=1, fill=1)
            img_model_l.save(file_full_path_model_l, "PNG")
            export_files.append(file_full_path_model_l)

            # generate RGB
            file_relative_path_model_rgb = (
                f"{file_relative_path_base_name}-segmentation.png"
            )
            file_full_path_model_rgb = out_data_dir.joinpath(
                file_relative_path_model_rgb
            )
            img_model_rgb = Image.new("RGB", (width, height), 0)
            for index, p in enumerate(polygons):
                color = colors[index % 255 + 1]
                ImageDraw.Draw(img_model_rgb).polygon(p, fill=color.get("hexString"))

                rgb = color.get("rgb")
                color_list.append(
                    {
                        "color": f'rgb({rgb.get("r")},{rgb.get("g")},{rgb.get("b")})',
                        "colorList": [rgb.get("r"), rgb.get("g"), rgb.get("b"), 255],
                        "trainIds": index + 1,
                        "attribute": polygon_attribute[index],
                    }
                )
            img_model_rgb.save(file_full_path_model_rgb, "PNG")
            export_files.append(file_full_path_model_rgb)

        # color list
        file_full_path_colors = out_data_dir.joinpath("colors.json")
        json_object = json.dumps(color_list, default=str)
        with file_full_path_colors.open("w") as outfile:
            outfile.write(json_object)
        export_files.append(file_full_path_colors)

        file_relative_path_zip = f"task-{out_data_file_name_prefix}-mask.zip"
        file_full_path_zip = out_data_dir.joinpath(file_relative_path_zip)
        with ZipFile(file_full_path_zip, "w") as zipf:
            for f in export_files:
                zipf.write(str(f), arcname=f.name)
        logger.info("Export file path: {}", file_full_path_zip)
        return file_full_path_zip

    def convert_to_labelme(self, config: dict, input_data: List[dict], out_data_file_name_prefix: str, out_data_dir: str):
        out_data_dir.mkdir(parents=True, exist_ok=True)
        export_files = []
        result = []
        # does not support cuboid / spline
        shape_dict = {
            "polygonTool": "polygon",
            "rectTool": "rectangle",
            "lineTool": "linestrip",
            "pointTool": "point",
        }
        
        label_text_dict = {}
        common_attributes = { attr.get("value"): attr.get("key") for attr in config.get("attributes", [])}
        
        for tool in config.get("tools", []):
            label_text_dict[tool.get("tool")] = { attr.get("value"): attr.get("key") for attr in tool.get("config", {}).get("attributes", [])}
        
        def get_label(_tool: str, _input_label: str):
            _label = label_text_dict.get(_tool, {}).get(_input_label, "")
            
            if not _label:
                _label = common_attributes.get(_input_label, "")
                
            return _label
        
        def convert_points(points: List[dict]):
            return [[point.get("x"), point.get("y")] for point in points]
        
        def image_to_base64(file_path: str):
            file_full_path = settings.MEDIA_ROOT.joinpath(file_path.lstrip("/"))
            with open(file_full_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        
        for sample in input_data:
            labelme_item = {
                "version": "5.5.0",
                "flags": {},
                "shapes": [],
                "imagePath": "",
                "imageData": "",
                "imageHeight": 0,
                "imageWidth": 0,
            }
            data = json.loads(sample.get("data"))
            file = sample.get("file", {})
            
            # skip invalid data
            annotated_result = json.loads(data.get("result"))
            if sample.get("state") == "SKIPPED":
                continue
            
            labelme_item["imagePath"] = file.get("filename", "")[9:]
            labelme_item["imageData"] = image_to_base64(file.get("path"))
            
            if annotated_result:
                labelme_item["imageWidth"] = annotated_result.get("width", 0)
                labelme_item["imageHeight"] = annotated_result.get("height", 0)
                
                for tool in annotated_result.copy().keys():
                    if tool.endswith("Tool") and tool in shape_dict:
                        # polygon
                        if tool == "polygonTool":
                            tool_results = annotated_result.pop(tool)
                            for tool_result in tool_results.get("result", []):
                                attributes = tool_result.get("attributes", {})
                                shape = {
                                    "label": get_label(tool, tool_result.get("label", "")),
                                    "points": convert_points(tool_result.get("points", [])),
                                    "group_id": "",
                                    # Get description from attributes
                                    "description": attributes.get("description", ""),
                                    "shape_type": shape_dict.get(tool, "polygon"),
                                    "flags": {},
                                    "mask": "",
                                }
                                labelme_item["shapes"].append(shape)
                                
                        # rect
                        if tool == "rectTool":
                            tool_results = annotated_result.pop(tool)
                            for tool_result in tool_results.get("result", []):
                                attributes = tool_result.get("attributes", {})
                                x = tool_result.get("x", 0)
                                y = tool_result.get("y", 0)
                                width = tool_result.get("width", 0)
                                height = tool_result.get("height", 0)
                                shape = {
                                    "label": get_label(tool, tool_result.get("label", "")),
                                    "points": [[x, y], [x + width, y + height]],
                                    "group_id": "",
                                    "description": attributes.get("description", ""),
                                    "shape_type": shape_dict.get(tool, "rectangle"),
                                    "flags": {},
                                    "mask": "",
                                }
                                labelme_item["shapes"].append(shape)
                        
                        if tool == "lineTool":
                            tool_results = annotated_result.pop(tool)
                            for tool_result in tool_results.get("result", []):
                                attributes = tool_result.get("attributes", {})
                                shape = {
                                    "label": get_label(tool, tool_result.get("label", "")),
                                    "points": convert_points(tool_result.get("points", [])),
                                    "group_id": "",
                                    "description": attributes.get("description", ""),
                                    "shape_type": shape_dict.get(tool, "linestrip"),
                                    "flags": {},
                                    "mask": "",
                                }
                                labelme_item["shapes"].append(shape)
                                
                        if tool == "pointTool":
                            tool_results = annotated_result.pop(tool)
                            for tool_result in tool_results.get("result", []):
                                attributes = tool_result.get("attributes", {})
                                shape = {
                                    "label": get_label(tool, tool_result.get("label", "")),
                                    "points": [[tool_result.get("x", 0), tool_result.get("y", 0)]],
                                    "group_id": "",
                                    "description": attributes.get("description", ""),
                                    "shape_type": shape_dict.get(tool, "point"),
                                    "flags": {},
                                    "mask": "",
                                }
                                labelme_item["shapes"].append(shape)
            result.append(labelme_item)
            file_basename = os.path.splitext(file.get("filename", "")[9:])[0]
            file_name = out_data_dir.joinpath(f"{file_basename}.json")
            with file_name.open("w") as outfile:
                # 格式化json，两个空格缩进
                json.dump(labelme_item, outfile, indent=2, ensure_ascii=False)
                
            export_files.append(file_name)
        
        
        file_relative_path_zip = f"task-{out_data_file_name_prefix}-label-me.zip"
        file_full_path_zip = out_data_dir.joinpath(file_relative_path_zip)
        with ZipFile(file_full_path_zip, "w") as zipf:
            for f in export_files:
                zipf.write(str(f), arcname=f.name)
        logger.info("Export file path: {}", file_full_path_zip)
        return file_full_path_zip
    
def _polygonArea(X, Y):

    # Initialize area
    area = 0.0
    n = len(X)

    # Calculate value of shoelace formula
    j = n - 1
    for i in range(0, n):
        area += (X[j] + X[i]) * (Y[j] - Y[i])
        j = i  # j is previous vertex to i

    # Return absolute value
    return abs(area) / 2.0


converter = Converter()
