# 标注格式说明

## 通用格式

```json
{
  "width": 4368, 
  "height": 2912, 
  "valid": true, 
  "rotate": 0, 
  "annotations": [
  {
    "toolName": "rectTool", 
    "result": [ 
      {
        "x": 530.7826086956522, 
        "y": 1149.217391304348,
        "width": 1314.7826086956522,
        "height": 1655.6521739130435,
        "label": "cat",
        "valid": true,
        "id": "Rp1x6bZs",
        "textAttribute": "",
        "order": 1
      }
    ]
  },
   {
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
        "label": "cat",
        "order": 1,
        "textAttribute": "",
      }
    ]
}
```

## 各工具导出格式说明

- [目标检测](./rectTool.md)
- [目标分类](./tagTool.md)
- [物体分割](./polygonTool.md)
- [文本转写](./textTool.md)
- [轮廓线检测](./lineTool.md)
- [关键点检测](./pointTool.md)


## Mask 格式导出说明

仅分割任务（多边形）可导出 Mask。

- 背景色默认为黑色：  0 `（rgb(0,0,0))`
- 语义的唯一性：语义分割的属性标注配置
- 导出内容:
  - Mask
    - 彩色图（xx_segmentation.png)：用于结果校验
    - 灰度图（xx_labelTrainIds.png)：用于训练
  - JSON 文件： 表示当前语义与颜色的索引关系

```json
[
  {
    "attribute": "cat",
    "color": "rgb(128,0,0)",
    "trainIds": 1 
  },
  {
    "attribute": "dog",
    "color": "rgb(0,128,0)",
    "trainIds": 2
  },
  {
    "attribute": "bird",
    "color": "rgb(128,128,0)",
    "trainIds": 3
  },
]
```

| 名称      | 描述                                       |
| --------- | ------------------------------------------ |
| attribute | 当前语义                                   |
| color     | 当前语义颜色                               |
| trainIds  | 训练使用的 ID （灰度值 1 - N，0 表示背景） |
