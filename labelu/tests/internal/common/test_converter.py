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
            "data": '{"result": "{\\"width\\":1256,\\"height\\":647,\\"valid\\":true,\\"rotate\\":0,\\"pointTool\\":{\\"toolName\\":\\"pointTool\\",\\"result\\":[{\\"x\\":435.58159028341424,\\"y\\":91.4164934517351,\\"isVisible\\":true,\\"attribute\\":\\"RT\\",\\"valid\\":true,\\"id\\":\\"0zuEcvvn\\",\\"textAttribute\\":\\"\\",\\"order\\":4},{\\"x\\":424.19947646227604,\\"y\\":149.74982678506842,\\"isVisible\\":true,\\"attribute\\":\\"RT\\",\\"valid\\":true,\\"id\\":\\"ZfJq48vz\\",\\"textAttribute\\":\\"\\",\\"order\\":5},{\\"x\\":337.4108585760972,\\"y\\":115.60348532165379,\\"isVisible\\":true,\\"attribute\\":\\"RT\\",\\"valid\\":true,\\"id\\":\\"gWWOuSIK\\",\\"textAttribute\\":\\"\\",\\"order\\":6},{\\"x\\":358.75232199073133,\\"y\\":65.80673735417413,\\"isVisible\\":true,\\"attribute\\":\\"pointTool\\",\\"valid\\":true,\\"id\\":\\"rqpHzgbg\\",\\"textAttribute\\":\\"\\",\\"order\\":7},{\\"x\\":525.2157366248776,\\"y\\":114.18072109401152,\\"isVisible\\":true,\\"attribute\\":\\"pointTool\\",\\"valid\\":true,\\"id\\":\\"HXIcRuRi\\",\\"textAttribute\\":\\"\\",\\"order\\":8},{\\"x\\":520.9474439419508,\\"y\\":68.65226580945868,\\"isVisible\\":true,\\"attribute\\":\\"pointTool\\",\\"valid\\":true,\\"id\\":\\"IvgQ7857\\",\\"textAttribute\\":\\"\\",\\"order\\":9}]},\\"rectTool\\":{\\"toolName\\":\\"rectTool\\",\\"result\\":[{\\"x\\":57.126305730568845,\\"y\\":60.11568044360503,\\"width\\":194.9186991869918,\\"height\\":125.20325203252028,\\"attribute\\":\\"RT\\",\\"valid\\":true,\\"isVisible\\":true,\\"id\\":\\"9nVICXfp\\",\\"textAttribute\\":\\"\\",\\"order\\":1},{\\"x\\":59.971834185853396,\\"y\\":243.65226580945864,\\"width\\":190.650406504065,\\"height\\":85.36585365853657,\\"attribute\\":\\"RT\\",\\"valid\\":true,\\"isVisible\\":true,\\"id\\":\\"ZTvmjRw7\\",\\"textAttribute\\":\\"\\",\\"order\\":2},{\\"x\\":121.15069597447126,\\"y\\":385.92868857368626,\\"width\\":229.06504065040644,\\"height\\":95.3252032520325,\\"attribute\\":\\"RT\\",\\"valid\\":true,\\"isVisible\\":true,\\"id\\":\\"tGTN8ZnE\\",\\"textAttribute\\":\\"\\",\\"order\\":3}]},\\"polygonTool\\":{\\"toolName\\":\\"polygonTool\\",\\"result\\":[{\\"id\\":\\"ahuCrbqm\\",\\"valid\\":true,\\"isVisible\\":true,\\"textAttribute\\":\\"\\",\\"pointList\\":[{\\"x\\":419.9311837793492,\\"y\\":220.88803816718223},{\\"x\\":424.1994764622761,\\"y\\":299.14007068750743},{\\"x\\":580.7035415029264,\\"y\\":292.02624954929604},{\\"x\\":583.549069958211,\\"y\\":219.46527393953994},{\\"x\\":401.43524881999963,\\"y\\":208.08316011840174},{\\"x\\":418.508419551707,\\"y\\":225.15633085010904},{\\"x\\":424.1994764622761,\\"y\\":225.15633085010904},{\\"x\\":418.508419551707,\\"y\\":225.15633085010904},{\\"x\\":418.508419551707,\\"y\\":225.15633085010904},{\\"x\\":424.1994764622761,\\"y\\":216.6197454842554},{\\"x\\":421.3539480069915,\\"y\\":225.15633085010904},{\\"x\\":421.3539480069915,\\"y\\":225.15633085010904}],\\"attribute\\":\\"polygonTool\\",\\"order\\":10},{\\"id\\":\\"VGF9qaBd\\",\\"valid\\":true,\\"isVisible\\":true,\\"textAttribute\\":\\"\\",\\"pointList\\":[{\\"x\\":438.4271187386988,\\"y\\":378.81486743547487},{\\"x\\":647.5734602021134,\\"y\\":397.31080239482446},{\\"x\\":565.0531349988614,\\"y\\":489.7904771915724},{\\"x\\":454.07752524276384,\\"y\\":472.7173064598651}],\\"attribute\\":\\"polygonTool\\",\\"order\\":11}]},\\"lineTool\\":{\\"toolName\\":\\"lineTool\\",\\"result\\":[{\\"pointList\\":[{\\"x\\":777.0450049175605,\\"y\\":77.18885117531234,\\"id\\":\\"pt8VnCYU\\"},{\\"x\\":1119.931183779349,\\"y\\":108.48966418344241,\\"id\\":\\"NGtAVtcy\\"},{\\"x\\":1102.8580130476416,\\"y\\":142.63600564685703,\\"id\\":\\"CvCZI5Ry\\"}],\\"id\\":\\"cO7suSFU\\",\\"valid\\":true,\\"order\\":12,\\"isVisible\\":true,\\"attribute\\":\\"lineTool\\"},{\\"pointList\\":[{\\"x\\":788.4271187386987,\\"y\\":236.53844467124725,\\"id\\":\\"0V7NNh2u\\"},{\\"x\\":1074.4027284947963,\\"y\\":205.23763166311718,\\"id\\":\\"VhtJi8sb\\"}],\\"id\\":\\"tges10Nc\\",\\"valid\\":true,\\"order\\":13,\\"isVisible\\":true,\\"attribute\\":\\"lineTool\\"}]},\\"tagTool\\":{\\"toolName\\":\\"tagTool\\",\\"result\\":[{\\"sourceID\\":\\"\\",\\"id\\":\\"707SMLxw\\",\\"result\\":{\\"class1\\":\\"option1\\"}}]},\\"textTool\\":[{\\"id\\":\\"JCwP2jrr\\",\\"sourceID\\":\\"\\",\\"value\\":{\\"\\u63cf\\u8ff0\\u7684\\u5173\\u952e\\":\\"ffefef\\"}},{\\"id\\":\\"nsk53z40\\",\\"sourceID\\":\\"\\",\\"value\\":{\\"\\u63cf\\u8ff0\\u7684\\u5173\\u952e1\\":\\"fefefef\\"}}]}", "urls": {"5": "http://localhost:8000/api/v1/tasks/attachment/upload/2/Pictures/5dc34027-screen.png"}, "fileNames": {"5": ""}}',
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
                        "copyBackwardResult": True,
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
                        "copyBackwardResult": True,
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
                        "copyBackwardResult": True,
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
                        "copyBackwardResult": True,
                        "attributeConfigurable": True,
                        "textConfigurable": True,
                        "textCheckType": 4,
                        "customFormat": "^[\\\\s\\\\S]{1,3}$",
                        "lowerLimitPointNum": "2",
                        "upperLimitPointNum": 100,
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
            "attribute": [{"key": "RT", "value": "RT"}],
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
        },
        input_data=input_data,
        out_data_dir=out_data_dir,
        out_data_file_name_prefix="task",
        format="JSON",
    )

    # check
    assert file_full_path
