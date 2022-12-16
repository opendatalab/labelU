# 文本(textTool)

## 格式说明

```json
{
  "width": 1024,
  "height": 681,
  "rotate": 0,
  "valid": true,
  "textTool": {
    "toolName": "textTool",
    "result": [
      {
        "id": "ULNah0Wf",
        "text": "textValue",
        "value": {
          "text": "textValue"
        }
      }
    ]
  }
}
```

<table class=""><colgroup><col style="width: 200px; min-width: 200px;"><col style="width: 100px; min-width: 100px;"><col style="width: 80px; min-width: 80px;"><col style="width: 80px; min-width: 80px;"><col><col style="width: 180px; min-width: 180px;"></colgroup><thead class="ant-table-thead"><tr><th class=""><span>名称</span></th><th class=""><span>类型</span></th><th class=""><span>是否必须</span></th><th class=""><span>默认值</span></th><th class=""><span>备注</span></th><th class=""><span>其他信息</span></th></tr></thead><tbody class="ant-table-tbody"><tr class="ant-table-row  ant-table-row-level-0"><td class=""><span class="ant-table-row-indent indent-level-0" style="padding-left: 0px;"></span><span class="ant-table-row-expand-icon ant-table-row-expanded"></span>result</td><td class=""><span>object []</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">图片上的结果列表，数量应与标注对象一致</span></td><td class=""><p><span style="font-weight: 700;">item 类型: </span><span>object</span></p></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>id</td><td class=""><span>string</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">文本内容的id</span></td><td class=""><p><span style="font-weight: 700;">mock: </span><span>@string</span></p></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>sourceID</td><td class=""><span>string</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">文本标注依赖对象的id</span></td><td class=""><p><span style="font-weight: 700;">mock: </span><span>@string</span></p></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>text</td><td class=""><span>string</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">文本内容</span></td><td class=""><p><span style="font-weight: 700;">mock: </span><span>@string</span></p></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-collapsed"></span>value</td><td class=""><span>object</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">文本内容（sincev2.4，支持多行文本，默认以这个结果为准）</span></td><td class=""><p><span style="font-weight: 700;">备注: </span><span>文本内容（sincev2.4，支持多行文本，默认以这个结果为准）</span></p></td></tr></tbody></table>
