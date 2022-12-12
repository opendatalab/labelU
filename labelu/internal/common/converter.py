import json
import uuid
from enum import Enum
from datetime import datetime

from typing import List
from loguru import logger


class Format(str, Enum):
    JSON = "JSON"
    COCO = "COCO"
    MASK = "MASK"


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

    def convert_to_json(
        self,
        input_data: List[dict],
        out_data_dir: str,
        out_data_file_name_prefix: str,
    ) -> str:
        out_data_dir.mkdir(parents=True, exist_ok=True)
        file_relative_path = f"task-{out_data_file_name_prefix}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{str(uuid.uuid4())[0:8]}.json"
        file_full_path = out_data_dir.joinpath(file_relative_path)
        results = []
        for item in input_data:
            data = json.loads(item.get("data"))
            results.append(
                {
                    "id": item.get("id"),
                    "result": data.get("result"),
                    "urls": data.get("urls"),
                    "fileNames": data.get("fileNames"),
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
        file_relative_path = f"task-{out_data_file_name_prefix}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{str(uuid.uuid4())[0:8]}.json"
        file_full_path = out_data_dir.joinpath(file_relative_path)

        # result struct
        result = {
            "images": [],
            "annotations": [],
            "categories": [],
        }

        # result catetory
        category_id = 0
        for attr in config.get("attribute", []):
            category = {
                "id": category_id,
                "name": attr.get("value", ""),
                "supercategory": "",
            }
            result["categories"].append(category)
            category_id += 1
        tools_category = config.get("tools", [])
        for tool in tools_category:
            for attr in tool.get("config", {}).get("attributeList", []):
                category = {
                    "id": category_id,
                    "name": attr.get("value", ""),
                    "supercategory": "",
                }
                result["categories"].append(category)
                category_id += 1

        category_name_map_id = {}
        for category in result["categories"]:
            category_name_map_id[category.get("name")] = category.get("id")

        # annotation index
        annotation_id = 0

        # for every annotation media
        for element in input_data:
            data = json.loads(element.get("data"))

            # annotation result
            annotation_info = json.loads(data.get("result"))

            # coco image
            image = {
                "id": element.get("id"),
                "fileNames": ",".join(data.get("fileNames", []).values()).rstrip(","),
                "width": annotation_info.get("width"),
                "height": annotation_info.get("height"),
                "valid": annotation_info.get("valid"),
                "rotate": annotation_info.get("rotate"),
            }
            result["images"].append(image)

            # every image may have multi tools
            tools = []
            if annotation_info.get("polygonTool", {}):
                tools.append(annotation_info.get("polygonTool"))
            if annotation_info.get("rectTool", {}):
                tools.append(annotation_info.get("rectTool"))
            if annotation_info.get("pointTool", {}):
                tools.append(annotation_info.get("pointTool"))
            if annotation_info.get("lineTool", {}):
                tools.append(annotation_info.get("lineTool"))
            if annotation_info.get("tagTool", {}):
                tools.append(annotation_info.get("tagTool"))
            # if annotation_info.get("textTool", {}):
            #     tools.append(annotation_info.get("textTool"))

            for tool in tools:
                for tool_result in tool.get("result"):

                    # polygon tool
                    segmentation = []
                    if annotation_info.get("polygonTool", {}):
                        for point in tool_result.get("pointList", []):
                            segmentation.append(point.get("x"))
                            segmentation.append(point.get("y"))

                    # polygon or rect
                    bbox = []
                    if (
                        tool_result.get("x")
                        and tool_result.get("y")
                        and tool_result.get("width")
                        and tool_result.get("height")
                    ):
                        bbox.append(tool_result.get("x"))
                        bbox.append(tool_result.get("y"))
                        bbox.append(tool_result.get("width"))
                        bbox.append(tool_result.get("height"))

                    annotation = {
                        "image_id": element.get("id"),
                        "id": annotation_id,
                        "bbox": bbox,
                        "iscrowd": tool_result.get("iscrowd", 0),
                        "segmentation": segmentation,
                        "category_id": category_name_map_id.get(
                            tool_result.get("attribute", ""), -1
                        ),
                        "area": tool_result.get("width", 0)
                        * tool_result.get("height", 0),
                        "textAttribute": tool_result.get("textAttribute", ""),
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


converter = Converter()
