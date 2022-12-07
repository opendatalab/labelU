from datetime import datetime, timedelta

from pathlib import Path
from tempfile import gettempdir

from labelu.internal.common.config import settings
from labelu.internal.common.converter import converter
from labelu.internal.common.security import AccessToken
from labelu.internal.common.security import create_access_token


def test_convert_to_json():
    # prepare data
    input_data = [
        {
            "id": 56,
            "state": "DONE",
            "data": {
                "result": '{"width":1210,"height":296,"valid":true,"rotate":0,"rectTool":{"toolName":"rectTool","result":[{"x":372.478738303954,"y":111.91652869560964,"width":380.9414466130997,"height":106.08495981630625,"attribute":"无标签","valid":true,"isVisible":true,"id":"qlo1pY3G","sourceID":"","textAttribute":"","order":1},{"x":955.9460172936383,"y":99.86141962557484,"width":89.20780711825752,"height":91.61882893226449,"attribute":"无标签","valid":true,"isVisible":true,"id":"bhF5OZsB","sourceID":"","textAttribute":"","order":2},{"x":150.66473141531364,"y":99.86141962557484,"width":113.31802525832713,"height":113.31802525832713,"attribute":"无标签","valid":true,"isVisible":true,"id":"6mzRUlu1","sourceID":"","textAttribute":"","order":3}]}}',
                "urls": {
                    "65": "http://localhost:8000/api/v1/tasks/attachment/upload/1/37d36994-Screenshot from 2022-03-07 19-30-26.png"
                },
                "fileNames": {"65": ""},
            },
            "annotated_count": 0,
            "created_by": {"id": 1, "username": "1@qq.com"},
            "updated_by": {"id": 1, "username": "1@qq.com"},
        }
    ]
    out_data_dir = Path(gettempdir())

    # run
    file_full_path = converter.convert(
        input_data=input_data,
        out_data_dir=out_data_dir,
        out_data_file_name_prefix="task",
        format="JSON",
    )

    # check
    assert file_full_path
