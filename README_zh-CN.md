<div align="center">
<article style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
    <p align="center"><img width="300" src="https://user-images.githubusercontent.com/25022954/209616423-9ab056be-5d62-4eeb-b91d-3b20f64cfcf8.svg" /></p>
    <h1 style="width: 100%; text-align: center;"></h1>
    <p align="center">
        简体中文 | <a href="./README.md" >English</a>
    </p>
</article>
    
   
</div>

## 产品介绍

LabelU是一款综合性的数据标注平台，专为处理多模态数据而设计。该平台旨在通过提供丰富的标注工具和高效的工作流程，帮助用户更轻松地处理图像、视频和音频数据的标注任务，满足各种复杂的数据分析和模型训练需求。

## 特色功能

### 多功能图像标注工具
LabelU为图像标注提供了全面的工具集，包括2D框、语义分割、多段线、关键点等多种标注方式。这些工具能够灵活应对各种图像处理任务，帮助用户高效完成图像的标识、注释和分析。

### 强大的视频标注功能
视频标注方面，LabelU展现了强大的处理能力，支持视频分割、视频分类以及视频信息提取等功能。用户能够轻松处理长时段视频，并提取关键信息，为后续的模型训练提供高质量的标注数据。

### 高效的音频标注工具
音频标注工具是LabelU的另一大特色。该工具具备高效、精准的音频分析能力，支持音频分割、音频分类和音频信息提取。通过将复杂的声音信息直观化展示，LabelU简化了音频数据的处理流程，助力更准确的模型开发。
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

### 图像

- **标签分类**：通过标签分类功能，用户可以快速对图像中的物体进行分类。这一功能不仅支持图像检索，还能用于目标检测等任务，使物体识别过程更加高效。

- **文本描述**：文本转写功能能够从图像中提取文字信息。这对于需要进行文本检索或机器翻译的任务来说非常实用，帮助用户快速获取图像中的关键信息。

- **拉框**：拉框工具让用户能够快速选择图像中的对象，适用于图像识别和目标跟踪等任务。这一功能简化了对象的标注过程，提高了工作效率。

- **标点**：标点工具帮助用户精确标注图像中的关键信息点，适用于对象识别和场景分析等任务。这种精确度对于复杂图像的分析尤为重要。

- **多边形**：多边形工具专为标注不规则形状的对象而设计，非常适用于物体识别和场景分析，确保用户能够准确标注各种复杂的形状。

- **标线**：标线工具用于精确标注图像中的边缘和轮廓，是对象识别和场景分析的重要辅助工具，帮助用户捕捉图像的细微特征。

- **立体框**：立体框工具能够帮助用户准确标注图像中的物体三维形状、位置等信息，适用于需要精确定位和形状分析的任务。

### 视频

- **标签分类**：对视频进行分类和标签化，可用于视频检索、推荐和分类任务，帮助用户有效管理和组织视频内容。

- **文本描述**：将视频中的语音内容转化为文字，支持语音识别、语音转写和语音翻译等任务，方便用户处理和理解视频中的音频信息。

- **片段分割**：从视频中截取特定的片段或场景进行标注，非常适合视频中的目标检测、行为识别和视频摘要等任务，提升视频分析的精度。

- **时间戳**：时间戳功能允许用户标记视频的特定部分，点击时间戳即可快速跳转到相应的片段，提高了视频内容浏览和处理的便捷性。

### 音频

- **标签分类**：通过音频标签分类功能，用户可以听取音频并选择合适的分类，适用于音频检索、推荐和分类任务，帮助有效组织音频数据。

- **文本描述**：将音频中的语音内容转化为文字，便于进一步的文本分析和处理。此功能对语音识别和转写任务特别有用，帮助用户更好地理解和处理音频内容。

- **片段分割**：从音频中截取特定片段进行标注，对音频事件检测、语音识别和音频编辑等任务非常有用，增强了音频处理的灵活性。

- **时间戳**：时间戳功能用于标记音频中的特定部分，用户点击时间戳即可直接跳转到音频的那个部分，极大地提高了音频内容的导航和处理效率。

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

- [LabelU-kit](https://github.com/opendatalab/labelU-Kit) Web 前端标注套件（LabelU基于此套件开发）
- [LabelLLM](https://github.com/opendatalab/LabelLLM) 开源LLM对话标注平台
- [Miner U](https://github.com/opendatalab/MinerU) 一站式高质量数据提取工具

## 开源许可证

该项目使用 [Apache 2.0 license](./LICENSE).
