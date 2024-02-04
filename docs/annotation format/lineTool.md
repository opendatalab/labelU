# 线条(lineTool)

## 格式说明

```json
{
  "width": 1024,
  "height": 681,
  "rotate": 0,
  "valid": true,
  "annotations": [
  {
    "toolName": "lineTool",
    "result": [
      {
        "points": [
          {
            "x": 341.95147928994083,
            "y": 138.61775147928998,
            "id": "TlfF2xY4"
          },
          {
            "x": 263.7775147928994,
            "y": 292.54792899408284,
            "id": "eKivOQt6"
          },
          {
            "x": 428.9905325443787,
            "y": 409.4059171597633,
            "id": "5L6zZWRM"
          },
          {
            "x": 763.4461538461538,
            "y": 384.42248520710064,
            "id": "IXuGhnQw"
          },
          {
            "x": 781.9822485207101,
            "y": 349.7680473372781,
            "id": "Oiy6pk9d"
          }
        ],
        "id": "rI89mHsg",
        "valid": true,
        "order": 1,
        "label": "class-6U",
        "textAttribute": "xxxxxd"
      }
    ]
  }
 ] 
}
```

<table class=""><colgroup><col style="width: 200px; min-width: 200px;"><col style="width: 100px; min-width: 100px;"><col style="width: 80px; min-width: 80px;"><col style="width: 80px; min-width: 80px;"><col><col style="width: 180px; min-width: 180px;"></colgroup><thead class="ant-table-thead"><tr><th class=""><span>名称</span></th><th class=""><span>类型</span></th><th class=""><span>是否必须</span></th><th class=""><span>默认值</span></th><th class=""><span>备注</span></th><th class=""><span>其他信息</span></th></tr></thead><tbody class="ant-table-tbody"><tr class="ant-table-row  ant-table-row-level-0"><td class=""><span class="ant-table-row-indent indent-level-0" style="padding-left: 0px;"></span><span class="ant-table-row-expand-icon ant-table-row-expanded"></span>result</td><td class=""><span>object []</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">线条列表，数量应与标注对象一致</span></td><td class=""><p><span style="font-weight: 700;">item 类型: </span><span>object</span></p></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-collapsed"></span>points</td><td class=""><span>object []</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">点列表</span></td><td class=""><p><span style="font-weight: 700;">item 类型: </span><span>object</span></p></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>id</td><td class=""><span>string</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">线条ID</span></td><td class=""><p><span style="font-weight: 700;">mock: </span><span>@string</span></p></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>valid</td><td class=""><span>boolean</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">是否有效</span></td><td class=""><p><span style="font-weight: 700;">mock: </span><span>@boolean</span></p></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>order</td><td class=""><span>number</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">序号</span></td><td class=""><p><span style="font-weight: 700;">mock: </span><span>@natural</span></p></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>label</td><td class=""><span>string</span></td><td class=""><div>非必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">标签</span></td><td class=""><p><span style="font-weight: 700;">mock: </span><span>@string</span></p></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>textAttribute</td><td class=""><span>string</span></td><td class=""><div>非必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">文本</span></td><td class=""><p><span style="font-weight: 700;">mock: </span><span>@string</span></p>
