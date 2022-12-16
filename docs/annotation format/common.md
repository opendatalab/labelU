# 通用工具字段概念详解

## 格式说明

```json
{
  "width": 1024,
  "height": 681,
  "rotate": 0,
  "valid": true,
  "recTool": {
    "toolName": "rectTool",
    "result": [
      {
        "x": 200.91597,
        "y": 157.15384,
        "width": 174.88402,
        "height": 227.26863,
        "order": 1,
        "valid": true,
        "id": "omd8QAY7",
        "attribute": "attribute_1",
        "textAttribute": "我是文本"
      }
    ]
  }
}
```

<table style="table-layout: auto;"><colgroup><col style="width: 200px;"><col style="width: 100px;"><col style="width: 80px;"><col style="width: 80px;"><col><col style="width: 180px;"></colgroup><thead class="ant-table-thead"><tr><th class="ant-table-cell">名称</th><th class="ant-table-cell">类型</th><th class="ant-table-cell">是否必须</th><th class="ant-table-cell">默认值</th><th class="ant-table-cell">备注</th><th class="ant-table-cell">其他信息</th></tr></thead><tr data-row-key="0-2" class="ant-table-row ant-table-row-level-0"><td class="ant-table-cell">id</td><td class="ant-table-cell"><span>string</span></td><td class="ant-table-cell"><div>必须</div></td><td class="ant-table-cell"></td><td class="ant-table-cell"><span class="table-desc">结果对象 ID （例如矩形/多边形） 。全局唯一，可用于查找

预标注结果的"id"字段，请使用随机8位字符串，以免出现兼容性问题。</span></td><td class="ant-table-cell"></td></tr><tr data-row-key="0-3" class="ant-table-row ant-table-row-level-0"><td class="ant-table-cell">valid</td><td class="ant-table-cell"><span>boolean</span></td><td class="ant-table-cell"><div>必须</div></td><td class="ant-table-cell"><div></div></td><td class="ant-table-cell"><span class="table-desc">图片 / 结果的有效性（看valid 的位置）</span></td><td class="ant-table-cell"></td></tr><tr data-row-key="0-4" class="ant-table-row ant-table-row-level-0"><td class="ant-table-cell">order</td><td class="ant-table-cell"><span>string</span></td><td class="ant-table-cell"><div>必须</div></td><td class="ant-table-cell"><div></div></td><td class="ant-table-cell"><span class="table-desc">标注结果属性，用于表示当前对象的顺序号（并不一定连续）</span></td><td class="ant-table-cell"></td></tr></tbody></table>
