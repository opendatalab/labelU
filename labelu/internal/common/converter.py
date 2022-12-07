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

    def convert_to_json(
        self,
        input_data: List[dict],
        out_data_dir: str,
        out_data_file_name_prefix: str,
    ) -> str:
        out_data_dir.mkdir(parents=True, exist_ok=True)
        file_relative_path = f"task-{out_data_file_name_prefix}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{str(uuid.uuid4())[0:8]}.json"
        file_full_path = out_data_dir.joinpath(file_relative_path)
        data = [
            {
                "id": item.get("id"),
                "result": item.get("data").get("result"),
                "urls": item.get("data").get("urls"),
                "fileNames": item.get("data").get("fileNames"),
            }
            for item in input_data
        ]

        # Serializing json
        json_object = json.dumps(data, default=str)
        with file_full_path.open("w") as outfile:
            outfile.write(json_object)

        logger.info("Export file path: {}", file_full_path)
        return file_full_path


converter = Converter()
