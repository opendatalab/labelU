# 图像分类(tagTool)

## 格式说明



```json
{
  "width": 1024,
  "height": 576,
  "rotate": 0,
  "valid": true,
  "tagTool": {
    "toolName": "tagTool",
    "result": [
      {
        "id": "CXHF5QUM",
        "result": {
          "class1": "option1-2;option1",
          "class-Xn": "option2-1"
        }
      }
    ]
  }
}
```

<table class=""><colgroup><col style="width: 200px; min-width: 200px;"><col style="width: 100px; min-width: 100px;"><col style="width: 80px; min-width: 80px;"><col style="width: 80px; min-width: 80px;"><col><col style="width: 180px; min-width: 180px;"></colgroup><thead class="ant-table-thead"><tr><th class=""><span>名称</span></th><th class=""><span>类型</span></th><th class=""><span>是否必须</span></th><th class=""><span>默认值</span></th><th class=""><span>备注</span></th><th class=""><span>其他信息</span></th></tr></thead><tbody class="ant-table-tbody"><tr class="ant-table-row  ant-table-row-level-0"><td class=""><span class="ant-table-row-indent indent-level-0" style="padding-left: 0px;"></span><span class="ant-table-row-expand-icon ant-table-row-expanded"></span>result</td><td class=""><span>object []</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc"></span></td><td class=""><p><span style="font-weight: 700;">item 类型: </span><span>object</span></p></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>id</td><td class=""><span>string</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">标签结果id（随机生成）</span></td><td class=""></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>sourceID</td><td class=""><span>string</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">依赖图形 ID </span></td><td class=""></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-expanded"></span>result</td><td class=""><span>object</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">标签工具结果</span></td><td class=""><p><span style="font-weight: 700;">备注: </span><span>标签工具结果</span></p></td></tr><tr class="ant-table-row  ant-table-row-level-2"><td class=""><span class="ant-table-row-indent indent-level-2" style="padding-left: 40px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>步骤配置中key</td><td class=""><span>string</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">value为标签值，多个value时使用英文分号做分割。</span></td><td class=""></td></tr><tr class="ant-table-row  ant-table-row-level-2"><td class=""><span class="ant-table-row-indent indent-level-2" style="padding-left: 40px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>key1(例子）</td><td class=""><span>string</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">多值： value1;value2;value3</span></td><td class=""></td></tr></tbody></table>
