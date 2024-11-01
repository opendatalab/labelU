import base64
import csv
import json
import os
from zipfile import ZipFile
from PIL import Image, ImageDraw
from enum import Enum

import xml.etree.ElementTree as ET
from typing import List
from loguru import logger

from labelu.internal.common.color import colors
from labelu.internal.common.config import settings


class Format(str, Enum):
    JSON = "JSON"
    COCO = "COCO"
    MASK = "MASK"
    YOLO = "YOLO"
    CSV = "CSV"
    XML = "XML"
    VOC = "VOC"
    TFRECORD = "TFRECORD"
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
        elif format == Format.YOLO.value:
            return self.convert_to_yolo(
                config=config,
                input_data=input_data,
                out_data_file_name_prefix=out_data_file_name_prefix,
                out_data_dir=out_data_dir,
            )
        elif format == Format.CSV.value:
            return self.convert_to_csv(
                config=config,
                input_data=input_data,
                out_data_file_name_prefix=out_data_file_name_prefix,
                out_data_dir=out_data_dir,
            )
        elif format == Format.XML.value:
            return self.convert_to_xml(
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
    
    def convert_to_yolo(self, config: dict, input_data: List[dict], out_data_file_name_prefix: str, out_data_dir: str):
        out_data_dir.mkdir(parents=True, exist_ok=True)
        export_files = []
        classes = []
        
        # make classes
        for tool in config.get("tools", []):
            for attr in tool.get("config", {}).get("attributes", []):
                classes.append(attr.get("value"))

        for attr in config.get("attributes", []):
            classes.append(attr.get("value"))
        
        # make classes.txt
        classes_file = out_data_dir.joinpath("classes.txt")
        with classes_file.open("w") as outfile:
            for c in classes:
                outfile.write(f"{c}\n")
        export_files.append(classes_file)
        
        for sample in input_data:
            data = json.loads(sample.get("data"))
            file = sample.get("file", {})
            
            # skip invalid data
            annotated_result = json.loads(data.get("result"))
            if sample.get("state") == "SKIPPED" or not annotated_result:
                continue
            
            image_width = annotated_result.get("width", 0)
            image_height = annotated_result.get("height", 0)
            
            for tool in annotated_result.copy().keys():
                if tool == 'rectTool':
                    tool_results = annotated_result.pop(tool)
                    for tool_result in tool_results.get("result", []):
                        x = tool_result.get("x", 0)
                        y = tool_result.get("y", 0)
                        width = tool_result.get("width", 0)
                        height = tool_result.get("height", 0)
                        label = tool_result.get("label", "")
                        x_center = x + width / 2
                        y_center = y + height / 2
                        x_center /= image_width
                        y_center /= image_height
                        width /= image_width
                        height /= image_height
                        file_basename = os.path.splitext(file.get("filename", "")[9:])[0]
                        file_name = out_data_dir.joinpath(f"{file_basename}.txt")
                        with file_name.open("a") as outfile:
                            outfile.write(f"{classes.index(label)} {x_center} {y_center} {width} {height}\n")
                        export_files.append(file_name)
            
            
        file_relative_path_zip = f"task-{out_data_file_name_prefix}-yolo.zip"
        file_full_path_zip = out_data_dir.joinpath(file_relative_path_zip)
        with ZipFile(file_full_path_zip, "w") as zipf:
            for f in export_files:
                zipf.write(str(f), arcname=f.name)
        logger.info("Export file path: {}", file_full_path_zip)
        return file_full_path_zip

    def convert_to_csv(self, config: dict, input_data: List[dict], out_data_file_name_prefix: str, out_data_dir: str):
        out_data_dir.mkdir(parents=True, exist_ok=True)
        export_files = []
        
        label_text_dict = {}
        common_attributes = { attr.get("value"): attr.get("key") for attr in config.get("attributes", [])}
        
        def get_label(_tool: str, _input_label: str):
            _label = label_text_dict.get(_tool, {}).get(_input_label, "")
            
            if not _label:
                _label = common_attributes.get(_input_label, "")
                
            return _label
        
        def get_attributes(attributes: dict):
            result = []
            
            for value in attributes.values():
                result.append(", ".join(value) if isinstance(value, list) else value)
                 
            return ", ".join(result)
        
        def get_points(direction: dict):
            return [
                (
                    direction.get("tl").get("x"),
                    direction.get("tl").get("y"),
                ),
                (
                    direction.get("tr").get("x"),
                    direction.get("tr").get("y"),
                ),
                (
                    direction.get("br").get("x"),
                    direction.get("br").get("y"),
                ),
                (
                    direction.get("bl").get("x"),
                    direction.get("bl").get("y"),
                ),
            ]
                
        
        for tool in config.get("tools", []):
            label_text_dict[tool.get("tool")] = { attr.get("value"): attr.get("key") for attr in tool.get("config", {}).get("attributes", [])}
            
        for sample in input_data:
            data = json.loads(sample.get("data"))
            file = sample.get("file", {})
            # tool_name, label, x, y, width, height etc.
            rows = []
            
            # skip invalid data
            annotated_result = json.loads(data.get("result"))
            if sample.get("state") == "SKIPPED" or not annotated_result:
                continue
            
            for tool in annotated_result.copy().keys():
                if tool == 'rectTool':
                    tool_results = annotated_result.pop(tool)
                    rows.append(["tool_name", "label", "label_text", "x", "y", "width", "height", "attributes", "order"])
                    for tool_result in tool_results.get("result", []):
                        x = tool_result.get("x", 0)
                        y = tool_result.get("y", 0)
                        width = tool_result.get("width", 0)
                        height = tool_result.get("height", 0)
                        label = tool_result.get("label", "")
                        order = tool_result.get("order", 0)
                        label_text = get_label(tool, label)
                        rows.append([tool, label, label_text, x, y, width, height, get_attributes(tool_result.get('attributes', {})), order])
                        
                if tool == 'lineTool':
                    tool_results = annotated_result.pop(tool)
                    rows.append(["tool_name", "label", "label_text", "points", "control_points", "attributes", "order"])
                    for tool_result in tool_results.get("result", []):
                        points = tool_result.get("points", [])
                        control_points = tool_result.get("controlPoints", [])
                        label = tool_result.get("label", "")
                        order = tool_result.get("order", 0)
                        label_text = get_label(tool, label)
                        rows.append([tool, label, label_text, points, control_points, get_attributes(tool_result.get('attributes', {})), order])
                        
                if tool == 'pointTool':
                    tool_results = annotated_result.pop(tool)
                    rows.append(["tool_name", "label", "label_text", "x", "y", "order"])
                    for tool_result in tool_results.get("result", []):
                        x = tool_result.get("x", 0)
                        y = tool_result.get("y", 0)
                        label = tool_result.get("label", "")
                        order = tool_result.get("order", 0)
                        label_text = get_label(tool, label)
                        rows.append([tool, label, label_text, x, y, order])
                        
                if tool == 'polygonTool':
                    tool_results = annotated_result.pop(tool)
                    rows.append(["tool_name", "label", "label_text", "points", "attributes", "order"])
                    for tool_result in tool_results.get("result", []):
                        points = tool_result.get("points", [])
                        control_points = tool_result.get("controlPoints", [])
                        label = tool_result.get("label", "")
                        order = tool_result.get("order", 0)
                        label_text = get_label(tool, label)
                        rows.append([tool, label, label_text, points, control_points, get_attributes(tool_result.get('attributes', {})), order])
                
                if tool == 'cuboidTool':
                    tool_results = annotated_result.pop(tool)
                    rows.append(["tool_name", "label", "label_text", "direction", "front", "back", "attributes", "order"])
                    for tool_result in tool_results.get("result", []):
                        direction = tool_result.get("direction")
                        # [[x,y], ...]
                        front = get_points(tool_result.get("front"))
                        back = get_points(tool_result.get("back"))
                        width = tool_result.get("width", 0)
                        height = tool_result.get("height", 0)
                        label = tool_result.get("label", "")
                        order = tool_result.get("order", 0)
                        label_text = get_label(tool, label)
                        rows.append([tool, label, label_text, direction, front, back, get_attributes(tool_result.get('attributes', {})), order])
                        
            file_basename = os.path.splitext(file.get("filename", "")[9:])[0]
            file_name = out_data_dir.joinpath(f"{file_basename}.csv")
            with file_name.open("w") as outfile:
                writer = csv.writer(outfile)
                writer.writerows(rows)
            export_files.append(file_name)
            
        file_relative_path_zip = f"task-{out_data_file_name_prefix}-csv.zip"
        file_full_path_zip = out_data_dir.joinpath(file_relative_path_zip)
        with ZipFile(file_full_path_zip, "w") as zipf:
            for f in export_files:
                zipf.write(str(f), arcname=f.name)
        logger.info("Export file path: {}", file_full_path_zip)
        return file_full_path_zip


    def convert_to_xml(self, config: dict, input_data: List[dict], out_data_file_name_prefix: str, out_data_dir: str):
        out_data_dir.mkdir(parents=True, exist_ok=True)
        file_full_path = out_data_dir.joinpath("result.xml")
        
        # result struct
        xml_converter = XML_converter()
        root = xml_converter.create_root("root")
        sample_item = ET.Element("sample")
        
        for sample in input_data:
            data = json.loads(sample.get("data"))
            file = sample.get("file", {})
            
            # skip invalid data
            annotated_result = json.loads(data.get("result"))
            result = ET.Element("result")
            if annotated_result and sample.get("state") == "SKIPPED":
                ET.SubElement(result, "valid").text = "False"

            ET.SubElement(sample_item, "id").text = str(sample.get("id"))
            ET.SubElement(sample_item, "fileName").text = file.get("filename", "")[9:]
            ET.SubElement(sample_item, "url").text = file.get("url")
            
            ET.SubElement(result, "width").text = str(annotated_result.get("width", 0))
            ET.SubElement(result, "height").text = str(annotated_result.get("height", 0))
            ET.SubElement(result, "rotate").text = str(annotated_result.get("rotate", 0))
            
            # change result struct
            if annotated_result:
                annotations = ET.Element("annotations")
                for tool in annotated_result.copy().keys():
                    tool_results = annotated_result.pop(tool)
                    if tool.endswith("Tool"):
                        tool_annotations = xml_converter.convert_tool_results(tool, tool_results)
                
                        for annotation in tool_annotations:
                            annotations.append(annotation)
                    
                result.append(annotations)
            
            sample_item.append(result)
            
        root.append(sample_item)    
        tree = ET.ElementTree(root)
        tree.write(file_full_path, encoding="utf-8", xml_declaration=True)
        logger.info("Export file path: {}", file_full_path)
        return file_full_path
        
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

class XML_converter:
    def create_root(self, root_name: str):
        root = ET.Element(root_name)
        
        return root

    def convert_tool_results(self, tool_name, tool_results):
        annotations = []
        for tool_result in tool_results.get("result", []):
            if tool_name == 'rectTool':
                annotation = self.create_rect(tool_result)
            elif tool_name == 'polygonTool':
                annotation = self.create_polygon(tool_result)
            elif tool_name == 'pointTool':
                annotation = self.create_point(tool_result)
            elif tool_name == 'lineTool':
                annotation = self.create_line(tool_result)
            elif tool_name == 'cuboidTool':
                annotation = self.create_cuboid(tool_result)
            elif tool_name == 'tagTool':
                annotation = self.create_tag(tool_result)
            elif tool_name == 'textTool':
                annotation = self.create_text(tool_result)
            else:
                continue
            annotations.append(annotation)
        return annotations

    def create_attributes(self, attributes: dict):
        result = ET.Element("attributes")
        
        for key, value in attributes.items():
            attribute = ET.Element("attribute")
            ET.SubElement(attribute, "key").text = key
            ET.SubElement(attribute, "value").text = value
            result.append(attribute)
        
        return result
    
    def create_rect(self, anno: dict):
        annotation = ET.Element("rect")
        
        ET.SubElement(annotation, "toolName").text = "rectTool"
        
        result = ET.Element("result")
        
        ET.SubElement(result, "x").text = str(anno.get("x", 0))
        ET.SubElement(result, "y").text = str(anno.get("y", 0))
        ET.SubElement(result, "width").text = str(anno.get("width", 0))
        ET.SubElement(result, "height").text = str(anno.get("height", 0))
        ET.SubElement(result, "label").text = anno.get("label", "")
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        
        result.append(self.create_attributes(anno.get("attributes", {})))
        
        annotation.append(result)
        
        return annotation
    
    def create_polygon(self, anno: dict):
        annotation = ET.Element("polygon")
        
        ET.SubElement(annotation, "toolName").text = "polygonTool"
        
        result = ET.Element("result")
        
        ET.SubElement(result, "label").text = anno.get("label", "")
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        ET.SubElement(result, "type").text = str(anno.get("type", "line"))
        
        points = ET.Element("points")
        for point in anno.get("points", []):
            p = ET.Element("point")
            
            ET.SubElement(p, "x").text = str(point.get("x", 0))
            ET.SubElement(p, "y").text = str(point.get("y", 0))
            
            points.append(p)
        
        if anno.get("controlPoints"):
            control_points = ET.Element("controlPoints")
            
            for cp in anno.get("controlPoints", []):
                item = ET.Element("controlPoint")
                
                ET.SubElement(item, "x").text = str(cp.get("x", 0))
                ET.SubElement(item, "y").text = str(cp.get("y", 0))
                
                control_points.append(item)
                
            result.append(control_points)
        
        result.append(self.create_attributes(anno.get("attributes", {})))
        result.append(points)
        annotation.append(result)
        
        return annotation
    
    def create_point(self, anno: dict):
        annotation = ET.Element("point")
        
        ET.SubElement(annotation, "toolName").text = "pointTool"
        
        result = ET.Element("result")
        
        ET.SubElement(result, "x").text = str(anno.get("x", 0))
        ET.SubElement(result, "y").text = str(anno.get("y", 0))
        ET.SubElement(result, "label").text = anno.get("label", "")
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        
        result.append(self.create_attributes(anno.get("attributes", {})))
        annotation.append(result)
        
        return annotation
    
    def create_line(self, anno: dict):
        annotation = ET.Element("line")
        
        ET.SubElement(annotation, "toolName").text = "lineTool"
        
        result = ET.Element("result")
        
        ET.SubElement(result, "label").text = anno.get("label", "")
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        ET.SubElement(result, "type").text = str(anno.get("type", "line"))
        
        points = ET.Element("points")
        for point in anno.get("points", []):
            p = ET.Element("point")
            
            ET.SubElement(p, "x").text = str(point.get("x", 0))
            ET.SubElement(p, "y").text = str(point.get("y", 0))
            
            points.append(p)
        
        if anno.get("controlPoints"):
            control_points = ET.Element("controlPoints")
            
            for cp in anno.get("controlPoints", []):
                item = ET.Element("controlPoint")
                
                ET.SubElement(item, "x").text = str(cp.get("x", 0))
                ET.SubElement(item, "y").text = str(cp.get("y", 0))
                
                control_points.append(item)
                
            result.append(control_points)
            
        result.append(self.create_attributes(anno.get("attributes", {})))
        result.append(points)
        annotation.append(result)
        
        return annotation
    
    def create_cuboid(self, anno: dict):
        annotation = ET.Element("cuboid")
        
        ET.SubElement(annotation, "toolName").text = "cuboidTool"
        
        result = ET.Element("result")
        
        ET.SubElement(result, "label").text = str(anno.get("label", ""))
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        ET.SubElement(result, "direction").text = str(anno.get("direction", "front"))
        
        front = ET.Element("front")
        
        for pos, point in anno.get("front", {}).items():
            position = ET.Element(pos)
            ET.SubElement(position, "x").text = str(point.get("x", 0))
            ET.SubElement(position, "y").text = str(point.get("y", 0))
            front.append(position)
        
        back = ET.Element("back")
        for pos, point in anno.get("back", {}).items():
            position = ET.Element(pos)
            ET.SubElement(position, "x").text = str(point.get("x", 0))
            ET.SubElement(position, "y").text = str(point.get("y", 0))
            back.append(position)
            
        result.append(self.create_attributes(anno.get("attributes", {})))
        result.append(front)
        result.append(back)
        
        annotation.append(result)
        
        return annotation
    
    def create_tag(self, anno: dict):
        annotation = ET.Element("tag")
        
        ET.SubElement(annotation, "toolName").text = "tagTool"
        
        result = ET.Element("result")
        
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        
        ET.SubElement(result, "id").text = anno.get("id", "")
        
        values = ET.Element("values")
        for key, value in anno.get("value", {}).items():
            ET.SubElement(values, key).text = ", ".join(value) if value else ""
        
            
        result.append(values)
        annotation.append(result)
        
        return annotation
    
    def create_text(self, anno: dict):
        annotation = ET.Element("text")
        
        ET.SubElement(annotation, "toolName").text = "textTool"
        
        result = ET.Element("result")
        
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        ET.SubElement(result, "id").text = anno.get("id", "")
        
        values = ET.Element("values")
        for key, value in anno.get("value", {}).items():
            ET.SubElement(values, key).text = value
        
        result.append(values)
        annotation.append(result)
        
        return annotation
    
converter = Converter()
