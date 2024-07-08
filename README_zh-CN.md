<div align="center">
<article style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
    <p align="center"><img width="300" src="https://user-images.githubusercontent.com/25022954/209616423-9ab056be-5d62-4eeb-b91d-3b20f64cfcf8.svg" /></p>
    <h1 style="width: 100%; text-align: center;"></h1>
    <p align="center">
        简体中文 | <a href="./README.md" >English</a>
    </p>
</article>
    
   
</div>

## 简介

LabelU 提供了多种标注工具和功能，支持图像、视频、音频标注。

- 图像类的多功能图像处理工具，涵盖 2D 框、语义分割、多段线、关键点等多种标注工具，协助完成图像的标识、注释和分析。
- 视频类标注具备强大视频处理能力，可实现视频分割、视频分类、视频信息提取等功能，为模型训练提供优质标注数据。
- 音频类高效精准的音频分析工具，可实现音频分割、音频分类、音频信息提取等功能，将复杂的声音信息直观可视化。

<p align="center">
<img style="width: 600px" src="https://user-images.githubusercontent.com/25022954/209318236-79d3a5c3-2700-46c3-b59a-62d9c132a6c3.gif">
</p>

## 特性

- 简易，提供多种图像标注工具，通过简单可视化配置即可标注
- 灵活，多种工具可自由组合使用，满足大部分图像，视频，音频的标注需求
- 通用，支持导出多种数据格式，包括 JSON，COCO，MASK

## 快速开始

- <a href="https://opendatalab.github.io/labelU-Kit/">
    <button>体验标注工具</button>
</a>

- <a href="https://labelu.shlab.tech/">
    <button>体验在线版</button>
</a>

### 本地部署

1. 安装 [Miniconda](https://docs.conda.io/en/latest/miniconda.html)，选择对应的操作系统类型并下载安装。

> **注：** 如果你的系统是 MacOS intel 芯片，请安装 [intel x86_64 版本的 Miniconda](https://repo.anaconda.com/miniconda/)。

2. 安装完毕后，在终端运行以下命令（过程中的提示选择默认 `y` 即可）：

```bash
conda create -n labelu python=3.11
```

> **注：** Windows 平台可在 Anaconda Prompt 程序中运行以上命令。

3. 激活环境：

```bash
conda activate labelu
```

4. 安装 LabelU：

```bash
pip install labelu
```

> 安装[测试版本](https://test.pypi.org/project/labelu/)：`pip install --extra-index-url https://test.pypi.org/simple/ labelu==<测试版本号>`

5. 运行：

```bash
labelu
```

6. 打开浏览器，访问 [http://localhost:8000/](http://localhost:8000/) 。

### 本地开发

```bash
# 安装miniconda
# https://docs.conda.io/en/latest/miniconda.html

# 创建虚拟环境(python = 3.11)
conda create -n labelu python=3.11

# 激活虚拟环境
conda activate labelu

# 安装 peotry
# https://python-poetry.org/docs/#installing-with-the-official-installer

# 安装所有依赖包
poetry install

# 启动labelu, 默认访问地址: http://localhost:8000
uvicorn labelu.main:app --reload

# 更新submodule
git submodule update --remote --merge
```

## 支持场景

### 图片

- 标签分类：标签分类可以帮助用户快速将图像中的物体进行分类，并且可以用于图像检索、目标检测等任务。
- 文本描述：文本转写可以帮助用户快速提取图像中的文字信息，并且可以用于文本检索、机器翻译等任务。
- 拉框：拉框可以帮助用户快速选择图像中的物体，并且可以用于图像识别、目标跟踪等任务。
- 标点：点可以帮助用户准确地标注图像中的关键信息，并且可以用于物体识别、场景分析等任务。
- 多边形：多边形可以帮助用户准确地标注不规则形状，并且可以用于物体识别、场景分析等任务。
- 标线：线可以帮助用户准确地标注图像中的边缘和轮廓，并且可以用于物体识别、场景分析等任务。
- 立体框：立体框可以帮助用户准确地标注图像中的物体大小、形状、位置等信息，并且可以用于物体识别、场景分析等任务。

### 视频

- 标签分类：对视频进行分类和标签化，可运用于视频检索、推荐和分类等任务。
- 文本描述：将视频中的语音内容转化为文字，可用于语音识别、语音转写和语音翻译等任务。
- 片段分割：从视频中截取特定的片段或场景进行标注，对于视频目标检测、行为识别和视频摘要等任务非常有用。
- 时间戳：指向或标记视频中的特定部分，用户可以点击时间戳即可直接跳转到视频的那个部分。

### 音频

- 标签分类：通过听取音频并选择合适的分类来进行标注，适用于音频检索、音频推荐和音频分类等任务。
- 文本描述：将音频中的语音内容转化为文字，便于用户进行文本分析和处理。对于语音识别、语音转写等任务非常有用，可以帮助用户更好地理解和处理语音内容。
- 片段分割：从音频中截取特定的片段进行标注，对于音频事件检测、语音识别和音频编辑等任务非常有用。
- 时间戳：用于指向或标记音频中的特定部分，用户可以点击时间戳即可直接跳转到音频的那个部分。

## 快速上手

- [使用说明](https://opendatalab.github.io/labelU)

## 标注格式

- [格式说明](https://opendatalab.github.io/labelU/#/schema)

## 技术交流

欢迎加入 Opendatalab 官方微信群！

<p align="center">
<img style="width: 400px" src="https://user-images.githubusercontent.com/25022954/208374419-2dffb701-321a-4091-944d-5d913de79a15.jpg">
</p>

## 友情链接

- [LabelU-kit](https://github.com/opendatalab/labelU-Kit)（本工具都是通过 LabelU-kit 进行开发）

## 开源许可证

该项目使用 [Apache 2.0 license](./LICENSE).
