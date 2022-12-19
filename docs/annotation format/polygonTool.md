# 物体分割(polygonTool)

## 格式说明

```json
{
  "width": 1024,
  "height": 681,
  "rotate": 0,
  "valid": true,
  "polygonTool": {
    "toolName": "polygonTool",
    "result": [
      {
        "id": "j91grNMP",
        "pointList": [
          {
            "x": 298.4319526627219,
            "y": 155.54201183431957
          },
          {
            "x": 246.85325443786985,
            "y": 203.09112426035506
          },
          {
            "x": 248.46508875739647,
            "y": 289.3242603550296
          },
          {
            "x": 320.9976331360947,
            "y": 345.73846153846154
          }
        ],
        "valid": true,
        "attribute": "class-BX",
        "order": 1,
        "textAttribute": "",
        "isRect": true
      }
    ]
  }
}
```

<table class=""><colgroup><col style="width: 200px; min-width: 200px;"><col style="width: 100px; min-width: 100px;"><col style="width: 80px; min-width: 80px;"><col style="width: 80px; min-width: 80px;"><col><col style="width: 180px; min-width: 180px;"></colgroup><thead class="ant-table-thead"><tr><th class=""><span>名称</span></th><th class=""><span>类型</span></th><th class=""><span>是否必须</span></th><th class=""><span>默认值</span></th><th class=""><span>备注</span></th><th class=""><span>其他信息</span></th></tr></thead><tbody class="ant-table-tbody"><tr class="ant-table-row  ant-table-row-level-0"><td class=""><span class="ant-table-row-indent indent-level-0" style="padding-left: 0px;"></span><span class="ant-table-row-expand-icon ant-table-row-expanded"></span>result</td><td class=""><span>object []</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc"></span></td><td class=""><p><span style="font-weight: 700;">item 类型: </span><span>object</span></p></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>sourceID</td><td class=""><span>number</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">依赖框体</span></td><td class=""></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>id</td><td class=""><span>string</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">当前id</span></td><td class=""></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-expanded"></span>pointList</td><td class=""><span>object []</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">多边形点集</span></td><td class=""><p><span style="font-weight: 700;">item 类型: </span><span>object</span></p></td></tr><tr class="ant-table-row  ant-table-row-level-2"><td class=""><span class="ant-table-row-indent indent-level-2" style="padding-left: 40px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>x</td><td class=""><span>number</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">点的 x 坐标</span></td><td class=""></td></tr><tr class="ant-table-row  ant-table-row-level-2"><td class=""><span class="ant-table-row-indent indent-level-2" style="padding-left: 40px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>y</td><td class=""><span>number</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">点的 y 坐标</span></td><td class=""></td></tr><tr class="ant-table-row  ant-table-row-level-2"><td class=""><span class="ant-table-row-indent indent-level-2" style="padding-left: 40px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>specialPoint</td><td class=""><span>boolean</span></td><td class=""><div>非必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">是否为特殊点</span></td><td class=""></td></tr><tr class="ant-table-row  ant-table-row-level-2"><td class=""><span class="ant-table-row-indent indent-level-2" style="padding-left: 40px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>specialEdge</td><td class=""><span>boolean</span></td><td class=""><div>非必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">顶点与其下一个顶点连成的边是否为特殊边</span></td><td class=""></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>valid</td><td class=""><span>boolean</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">当前多边形有无效性</span></td><td class=""></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>order</td><td class=""><span>number</span></td><td class=""><div>必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">当前多边形的序号</span></td><td class=""></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>textAttribute</td><td class=""><span>string</span></td><td class=""><div>非必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">多边形的文本属性</span></td><td class=""></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>attribute</td><td class=""><span>string</span></td><td class=""><div>非必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">多边形配置的属性</span></td><td class=""></td></tr><tr class="ant-table-row  ant-table-row-level-1"><td class=""><span class="ant-table-row-indent indent-level-1" style="padding-left: 20px;"></span><span class="ant-table-row-expand-icon ant-table-row-spaced"></span>isRect</td><td class=""><span>boolean</span></td><td class=""><div>非必须</div></td><td class=""><div></div></td><td class=""><span class="table-desc">当前多边形是否通过矩形模式创建</span></td><td class=""></td></tr></tbody></table>
