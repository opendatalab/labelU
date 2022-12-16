# 标注格式说明

## 通用格式

```json
{
  "width": 4368, //图像宽度
  "height": 2912, //图像高度
  "valid": true, //是否有效
  "rotate": 0, //旋转角度
  "rectTool": {
    "toolName": "rectTool", // 工具名称
    "result": [ 
      {
        "x": 530.7826086956522,
        "y": 1149.217391304348,
        "width": 1314.7826086956522,
        "height": 1655.6521739130435,
        "attribute": "",
        "valid": true,
        "id": "Rp1x6bZs",
        "sourceID": "",
        "textAttribute": "",
        "order": 1
      }
    ]
  }
}
```

## 工具类型

- [通用配置](./common.md)
- [目标检测](./rectTool.md)
- [目标分类](./tagTool.md)
- [实例分割](./polygonTool.md)
- [文本转写](./textTool.md)
- [轮廓线检测](./lineTool.md)
- [关键点检测](./pointTool.md)

## COCO 数据类型
 
COCO(Common Object in Context) 是一个大规模的对象检测、分割和字幕数据集。具体定义请前往[官网](https://cocodataset.org/#home)查看
仅物体检测（拉框）、实例分割（多边形）支持导出COCO

## Mask 格式导出说明

仅分割任务（多边形）可导出 Mask。

- 背景色默认为黑色：  0 `（rgb(0,0,0))`
- 语义的唯一性：语义分割的属性标注配置
- 导出内容:
  - JSON 文件： 表示当前语义与颜色的索引关系
  - Mask
    - 彩色图（xx_segmentation.png)：用于结果校验
    - 灰度图（xx_labelTrainIds.png)
 

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
