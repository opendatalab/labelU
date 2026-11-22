import json
from zipfile import ZipFile

from PIL import Image

from labelu.internal.common.config import settings
from labelu.internal.common.converter import converter


def test_convert_to_labelme_uses_label_value_and_utf8(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "MEDIA_ROOT", tmp_path)

    for name in ("sample_中文.png", "empty.png"):
        image_path = tmp_path / "upload" / "1" / name
        image_path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (100, 80), (128, 128, 128)).save(image_path)

    rect_result = {
        "width": 100,
        "height": 80,
        "valid": True,
        "rotate": 0,
        "rectTool": {
            "toolName": "rectTool",
            "result": [
                {
                    "x": 10,
                    "y": 20,
                    "width": 30,
                    "height": 40,
                    "label": "person",
                    "attributes": {"description": "中文描述"},
                    "order": 1,
                }
            ],
        },
    }

    input_data = [
        {
            "id": 1,
            "state": "DONE",
            "data": json.dumps({"result": json.dumps(rect_result)}),
            "file": {
                "filename": "sample_中文.png",
                "path": "/upload/1/sample_中文.png",
                "url": "/sample_中文.png",
            },
        },
        {
            "id": 2,
            "state": "NEW",
            "data": json.dumps({"result": ""}),
            "file": {
                "filename": "empty.png",
                "path": "/upload/1/empty.png",
                "url": "/empty.png",
            },
        },
    ]

    zip_path = converter.convert(
        config={
            "attributes": [],
            "tools": [
                {
                    "tool": "rectTool",
                    "config": {
                        "attributes": [{"key": "人", "value": "person"}]
                    },
                }
            ],
        },
        input_data=input_data,
        out_data_dir=tmp_path / "out",
        out_data_file_name_prefix="task",
        format="LABEL_ME",
    )

    with ZipFile(zip_path) as zipf:
        raw_bytes = zipf.read("sample_中文.json")
        exported = json.loads(raw_bytes.decode("utf-8"))
        assert exported["shapes"][0]["label"] == "person"
        assert exported["shapes"][0]["description"] == "中文描述"

        empty_exported = json.loads(zipf.read("empty.json").decode("utf-8"))
        assert empty_exported["shapes"] == []
