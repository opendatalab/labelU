from pathlib import Path
from tempfile import gettempdir

from labelu.internal.common.converter import converter


def test_convert_to_json():
    # prepare data
    input_data = [
        {
            "id": 56,
            "state": "DONE",
            "data": '{"result": "{\\"width\\":1256,\\"height\\":647,\\"valid\\":true,\\"rotate\\":0,\\"rectTool\\":{\\"toolName\\":\\"rectTool\\",\\"result\\":[{\\"x\\":76.7636304422194,\\"y\\":86.75077939093666,\\"width\\":156.47058823529457,\\"height\\":86.47058823529437,\\"label\\":\\"RT\\",\\"valid\\":true,\\"isVisible\\":true,\\"id\\":\\"J3eK0yr6\\",\\"sourceID\\":\\"\\",\\"textAttribute\\":\\"\\",\\"order\\":1},{\\"x\\":68.52833632457231,\\"y\\":288.5154852732902,\\"width\\":185.29411764705938,\\"height\\":115.29411764705917,\\"label\\":\\"rectTool\\",\\"valid\\":true,\\"isVisible\\":true,\\"id\\":\\"wDIMAnat\\",\\"sourceID\\":\\"\\",\\"textAttribute\\":\\"\\",\\"order\\":2}]},\\"pointTool\\":{\\"toolName\\":\\"pointTool\\",\\"result\\":[{\\"x\\":64.41068926574877,\\"y\\":543.8096029203498,\\"isVisible\\":true,\\"label\\":\\"无标签\\",\\"valid\\":true,\\"id\\":\\"FRejHry3\\",\\"textAttribute\\":\\"\\",\\"order\\":3},{\\"x\\":257.94010103045525,\\"y\\":552.0448970379969,\\"isVisible\\":true,\\"label\\":\\"pointTool\\",\\"valid\\":true,\\"id\\":\\"Hzj1lxHB\\",\\"textAttribute\\":\\"\\",\\"order\\":4}]},\\"polygonTool\\":{\\"toolName\\":\\"polygonTool\\",\\"result\\":[{\\"id\\":\\"YBVRgJYy\\",\\"valid\\":true,\\"isVisible\\":true,\\"textAttribute\\":\\"\\",\\"points\\":[{\\"x\\":517.3518657363384,\\"y\\":78.51548527328956},{\\"x\\":472.05774808927936,\\"y\\":247.33901468505476},{\\"x\\":859.1165716186923,\\"y\\":284.3978382144666},{\\"x\\":978.528336324575,\\"y\\":144.39783821446622},{\\"x\\":686.1753951481036,\\"y\\":49.691955861524775}],\\"label\\":\\"RT\\",\\"order\\":5},{\\"id\\":\\"miH6P16a\\",\\"valid\\":true,\\"isVisible\\":true,\\"textAttribute\\":\\"\\",\\"points\\":[{\\"x\\":550.2930422069267,\\"y\\":399.6919558615258},{\\"x\\":521.4695127951619,\\"y\\":556.1625440968204},{\\"x\\":735.587159853986,\\"y\\":552.0448970379969},{\\"x\\":842.6459833833981,\\"y\\":440.8684264497612},{\\"x\\":764.4106892657508,\\"y\\":395.57430880270226},{\\"x\\":616.1753951481033,\\"y\\":374.9860735085845}],\\"label\\":\\"polygonTool\\",\\"order\\":6}]},\\"lineTool\\":{\\"toolName\\":\\"lineTool\\",\\"result\\":[{\\"points\\":[{\\"x\\":970.2930422069279,\\"y\\":57.92724997917186,\\"id\\":\\"OIuogYeu\\"},{\\"x\\":1163.8224539716343,\\"y\\":107.33901468505437,\\"id\\":\\"ZpkyExOs\\"},{\\"x\\":1097.9401010304578,\\"y\\":144.39783821446625,\\"id\\":\\"A5pOdHao\\"},{\\"x\\":970.2930422069279,\\"y\\":132.0448970379956,\\"id\\":\\"20Lx7GQZ\\"}],\\"id\\":\\"3U3VY93T\\",\\"valid\\":true,\\"order\\":7,\\"isVisible\\":true,\\"label\\":\\"RT\\"},{\\"points\\":[{\\"x\\":1040.2930422069282,\\"y\\":284.3978382144667,\\"id\\":\\"1zdkvfsO\\"},{\\"x\\":1229.7048069128111,\\"y\\":284.3978382144667,\\"id\\":\\"L7E6NIDx\\"},{\\"x\\":1213.234218677517,\\"y\\":383.22136762623165,\\"id\\":\\"maDtUPWR\\"},{\\"x\\":1023.822453971634,\\"y\\":403.80960292034933,\\"id\\":\\"xCuDp9g0\\"}],\\"id\\":\\"VvfLXlii\\",\\"valid\\":true,\\"order\\":8,\\"isVisible\\":true,\\"label\\":\\"lineTool\\"}]},\\"tagTool\\":{\\"toolName\\":\\"tagTool\\",\\"result\\":[{\\"sourceID\\":\\"\\",\\"id\\":\\"5939weRA\\",\\"result\\":{\\"class1\\":\\"option1\\",\\"class2\\":\\"aoption1\\"}}]},\\"textTool\\":{\\"toolName\\":\\"textTool\\",\\"result\\":[{\\"id\\":\\"OhdGIhFX\\",\\"sourceID\\":\\"\\",\\"value\\":{\\"描述的关键\\":\\"我的描述\\"}},{\\"id\\":\\"1TN5jPTb\\",\\"sourceID\\":\\"\\",\\"value\\":{\\"描述的关键1\\":\\"我的描述1\\"}}]}}","urls": {"42": "http://localhost:8000/api/v1/tasks/attachment/upload/6/1/d9c34a05-screen.png"},"fileNames": {"42": ""}}',
            "annotated_count": 4,
        }
    ]
    out_data_dir = Path(gettempdir())

    # run
    file_full_path = converter.convert(
        config={
            "tools": [
                {
                    "tool": "rectTool",
                    "config": {
                        "isShowCursor": False,
                        "showConfirm": False,
                        "skipWhileNoDependencies": False,
                        "drawOutsideTarget": False,
                        "copyBackwardResult": False,
                        "minWidth": 1,
                        "attributeConfigurable": True,
                        "textConfigurable": True,
                        "textCheckType": 4,
                        "customFormat": "",
                        "attributeList": [{"key": "rectTool", "value": "rectTool"}],
                    },
                },
                {
                    "tool": "pointTool",
                    "config": {
                        "upperLimit": 10,
                        "isShowCursor": False,
                        "attributeConfigurable": True,
                        "copyBackwardResult": False,
                        "textConfigurable": True,
                        "textCheckType": 0,
                        "customFormat": "",
                        "attributeList": [{"key": "pointTool", "value": "pointTool"}],
                    },
                },
                {
                    "tool": "polygonTool",
                    "config": {
                        "isShowCursor": False,
                        "lineType": 0,
                        "lineColor": 0,
                        "drawOutsideTarget": False,
                        "edgeAdsorption": True,
                        "copyBackwardResult": False,
                        "attributeConfigurable": True,
                        "textConfigurable": True,
                        "textCheckType": 0,
                        "customFormat": "",
                        "attributeList": [
                            {"key": "polygonTool", "value": "polygonTool"}
                        ],
                        "lowerLimitPointNum": "4",
                        "upperLimitPointNum": 100,
                    },
                },
                {
                    "tool": "lineTool",
                    "config": {
                        "isShowCursor": False,
                        "lineType": 0,
                        "lineColor": 1,
                        "edgeAdsorption": True,
                        "outOfTarget": True,
                        "copyBackwardResult": False,
                        "attributeConfigurable": True,
                        "textConfigurable": True,
                        "textCheckType": 4,
                        "customFormat": "^[\\s\\S]{1,3}$",
                        "lowerLimitPointNum": 4,
                        "upperLimitPointNum": "",
                        "attributeList": [{"key": "lineTool", "value": "lineTool"}],
                    },
                },
                {"tool": "tagTool"},
                {"tool": "textTool"},
            ],
            "tagList": [
                {
                    "key": "类别1",
                    "value": "class1",
                    "isMulti": True,
                    "subSelected": [
                        {"key": "选项1", "value": "option1", "isDefault": True},
                        {"key": "选项2", "value": "option2", "isDefault": False},
                    ],
                },
                {
                    "key": "类别2",
                    "value": "class2",
                    "isMulti": True,
                    "subSelected": [
                        {"key": "a选项1", "value": "aoption1", "isDefault": True},
                        {"key": "a选项2", "value": "aoption2", "isDefault": False},
                    ],
                },
            ],
            "attributes": [{"key": "RT", "value": "RT"}],
            "textConfig": [
                {
                    "label": "我的描述",
                    "key": "描述的关键",
                    "required": True,
                    "default": "",
                    "maxLength": 200,
                },
                {
                    "label": "我的描述1",
                    "key": "描述的关键1",
                    "required": True,
                    "default": "",
                    "maxLength": 200,
                },
            ],
            "fileInfo": {
                "type": "img",
                "list": [
                    {"id": 1, "url": "/src/img/example/bear6.webp", "result": "[]"}
                ],
            },
            "commonAttributeConfigurable": True,
        },
        input_data=input_data,
        out_data_dir=out_data_dir,
        out_data_file_name_prefix="task",
        format="JSON",
    )

    # check
    assert file_full_path
