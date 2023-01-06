<div align="center">
<article style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
    <p align="center"><img width="300" src="https://user-images.githubusercontent.com/25022954/209616423-9ab056be-5d62-4eeb-b91d-3b20f64cfcf8.svg" /></p>
    <h1 style="width: 100%; text-align: center;"></h1>
    </p>
</article>

<a href="./README_zh-CN.md" >简体中文</a> | English


</div>

## Introduction

LabelU is an open source data annotation tool that supports Chinese. At present, it has image annotation capabilities such as rectangle, polygon, point, line, classification, description. It can support detection, classification, segmentation, text transcription, Line detection, key point detection and other computer vision task scenarios. You can customize the annotation task by freely combining tools, and support COCO and MASK format data export.

## Getting started

### Download and Install miniconda

https://docs.conda.io/en/latest/miniconda.html

### Create virtual environment(python = 3.10)

```bash
conda create -n labelu python=3.10
```

### Activate virtual environment

```bash
conda activate labelu
```

### Install labelu

```bash
pip install labelu
```

### Start labelu，server：http://localhost:8000

```bash
labelu
```

## feature

- Uniform，Six image annotation tools are provided, which can be configured through simple visualization or Yaml
- Unlimited，Multiple tools can be freely combined to meet most image annotation requirements

<p align="center">
<img style="width: 600px" src="https://user-images.githubusercontent.com/25022954/209318236-79d3a5c3-2700-46c3-b59a-62d9c132a6c3.gif">
</p>

- Universal，Support multiple data export formats, including LabelU, COCO, Mask

## Scenes

### Computer Vision

- Detection: Detection scenes for vehicles, license plates, pedestrians, faces, industrial parts, etc.
- Classification: Detection of object classification, target characteristics, right and wrong judgments, and other classification scenarios
- Semantic segmentation: Human body segmentation, panoramic segmentation, drivable area segmentation, vehicle segmentation, etc.
- Text transcription: Text detection and recognition of license plates, invoices, insurance policies, signs, etc.
- Contour detection: positioning line scenes such as human contour lines, lane lines, etc.
- Key point detection: positioning scenes such as human face key points, vehicle key points, road edge key points, etc.

## Usage

-  [Guide](./docs/GUIDE.md) 

## Annotation Format

-  [LabelU Annotation Format](./docs/annotation%20format/README.md)

## Communication

Welcome to the Opendatalab Wechat group！

<p align="center">
<img style="width: 400px" src="https://user-images.githubusercontent.com/25022954/208374419-2dffb701-321a-4091-944d-5d913de79a15.jpg">
</p>



## Links

- [labelU-Kit](https://github.com/opendatalab/labelU-Kit)（Powered by labelU-Kit）

## LICENSE

This project is released under the [Apache 2.0 license](./LICENSE).
