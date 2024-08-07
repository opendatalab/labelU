<div align="center">
<article style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
    <p align="center"><img width="300" src="https://user-images.githubusercontent.com/25022954/209616423-9ab056be-5d62-4eeb-b91d-3b20f64cfcf8.svg" /></p>
    <h1 style="width: 100%; text-align: center;"></h1>
    <p align="center">
        English | <a href="./README_zh-CN.md" >简体中文</a>
    </p>
</article>
    
   
</div>

## Product Introduction

LabelU is a comprehensive data annotation platform designed for handling multimodal data. It offers a range of advanced annotation tools and efficient workflows, making it easier for users to tackle annotation tasks involving images, videos, and audio. LabelU is tailored to meet the demands of complex data analysis and model training.

## Key Features

### Versatile Image Annotation Tools
LabelU provides a robust set of image annotation tools, including 2D bounding boxes, semantic segmentation, polylines, and keypoints. These tools are adaptable to a wide range of image processing tasks, enabling users to efficiently complete image labeling, annotation, and analysis.

### Powerful Video Annotation Capabilities
For video annotation, LabelU offers strong processing capabilities, supporting video segmentation, video classification, and video information extraction. Users can easily manage long-duration videos and extract key information, providing high-quality annotated data for subsequent model training.

### Efficient Audio Annotation Tools
LabelU also features powerful audio annotation tools with efficient and precise audio analysis capabilities. These tools support audio segmentation, audio classification, and audio information extraction. By visualizing complex sound information, LabelU simplifies the audio data processing workflow, facilitating more accurate model development.

<div align="center">
  <a href="https://www.youtube.com/watch?v=4oeehP-rqtU">
    <img src="https://img.youtube.com/vi/4oeehP-rqtU/0.jpg" alt="Watch the video" width="700">
  </a>
</div>



## Features

- Simplicity: Provides a variety of image annotation tools that can be annotated through simple visual configuration.
- Flexibility: A variety of tools can be freely combined to meet most image, video, and audio annotation needs.
- Universality: Supports exporting to various data formats, including JSON, COCO, MASK.

## Getting started

- <a href="https://opendatalab.github.io/labelU-Kit/">
    <button>Try LabelU annotation toolkit</button>
</a>

- <a href="https://labelu.shlab.tech/">
    <button>Try LabelU online</button>
</a>

### Local deployment

1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html), Choose the corresponding operating system type and download it for installation.

> **Note：** If your system is MacOS with an Intel chip, please install [Miniconda of intel x86_64](https://repo.anaconda.com/miniconda/)。

2. After the installation is complete, run the following command in the terminal (you can choose the default 'y' for prompts during the process):

```bash
conda create -n labelu python=3.11
```

> **Note：** For Windows platform, you can run the above command in Anaconda Prompt.

3. Activate the environment：

```bash
conda activate labelu
```

4. Install LabelU：

```bash
pip install labelu
```

> To install the test version：`pip install --extra-index-url https://test.pypi.org/simple/ labelu==<test revision>`

5. Run LabelU：

```bash
labelu
```

6. Visit [http://localhost:8000/](http://localhost:8000/) and ready to go.

### Local development

```bash
# Download and Install miniconda
# https://docs.conda.io/en/latest/miniconda.html

# Create virtual environment(python = 3.11)
conda create -n labelu python=3.11

# Activate virtual environment
conda activate labelu

# Install peotry
# https://python-poetry.org/docs/#installing-with-the-official-installer

# Install all package dependencies
poetry install

# Start labelu, server: http://localhost:8000
uvicorn labelu.main:app --reload

# Update submodule
git submodule update --remote --merge
```

## Supported Scenarios

### Image 

- **Label Classification**: The label classification feature enables users to quickly categorize objects within images. This functionality supports image retrieval and object detection tasks, making the identification process more efficient.

- **Text Transcription**: The text transcription tool extracts textual information from images. This is particularly useful for tasks requiring text retrieval or machine translation, helping users quickly access critical information within images.

- **Bounding Box**: The bounding box tool allows users to quickly select objects within images, ideal for image recognition and object tracking tasks. This feature simplifies the annotation process, boosting workflow efficiency.

- **Point Annotation**: Point annotation helps users accurately mark key points within an image, useful for object recognition and scene analysis. This precision is especially important for analyzing complex images.

- **Polygon Annotation**: The polygon tool is designed to annotate irregularly shaped objects, making it ideal for object recognition and scene analysis. It ensures accurate annotation of various complex shapes.

- **Line Annotation**: The line annotation tool is used to precisely mark edges and contours within images, aiding in object recognition and scene analysis. It helps users capture fine details in images.

- **3D Bounding Box**: The 3D bounding box tool allows users to accurately annotate the three-dimensional shape, position, and size of objects within images, which is essential for tasks requiring precise localization and shape analysis.

### Video

- **Label Classification**: Classify and label video content, which can be used for video retrieval, recommendation, and categorization tasks, helping users manage and organize video content effectively.

- **Text Transcription**: Convert spoken content within videos into text, supporting speech recognition, transcription, and translation tasks, facilitating the processing and understanding of audio information within videos.

- **Segment Splitting**: Extract specific segments or scenes from videos for annotation, making it ideal for tasks such as object detection, behavior recognition, and video summarization, enhancing the precision of video analysis.

- **Timestamping**: The timestamping feature allows users to mark specific parts of a video, enabling quick navigation to the relevant segment by clicking on the timestamp, improving the ease of browsing and processing video content.

### Audio

- **Label Classification**: Through the label classification feature, users can listen to audio and choose appropriate categories, useful for audio retrieval, recommendation, and classification tasks, helping to organize audio data effectively.

- **Text Transcription**: Convert speech content in audio files into text for easier analysis and processing. This feature is particularly useful for speech recognition and transcription tasks, helping users better understand and handle audio content.

- **Segment Splitting**: Extract specific segments from audio for annotation, ideal for tasks like audio event detection, speech recognition, and audio editing, enhancing flexibility in audio processing.

- **Timestamping**: The timestamping feature marks specific sections within audio, allowing users to jump directly to those parts by clicking on the timestamp, greatly improving the efficiency of navigating and processing audio content.


## Quick start

- [Guidance](https://opendatalab.github.io/labelU)

## Annotation format

- [Documentation](https://opendatalab.github.io/labelU/#/schema)

## Citation

```bibtex
@article{he2024opendatalab,
  title={Opendatalab: Empowering general artificial intelligence with open datasets},
  author={He, Conghui and Li, Wei and Jin, Zhenjiang and Xu, Chao and Wang, Bin and Lin, Dahua},
  journal={arXiv preprint arXiv:2407.13773},
  year={2024}
}
```

## Communication

Welcome to the OpenDataLab official WeChat group！

<p align="center">
<img style="width: 400px" src="https://user-images.githubusercontent.com/25022954/208374419-2dffb701-321a-4091-944d-5d913de79a15.jpg">
</p>


## Links

- [LabelU-kit](https://github.com/opendatalab/labelU-Kit) Web front-end annotation kit (LabelU is based on this JavaScript kit)
- [LabelLLM](https://github.com/opendatalab/LabelLLM) An Open-source LLM Dialogue Annotation Platform
- [Miner U](https://github.com/opendatalab/MinerU) A One-stop Open-source High-quality Data Extraction Tool

## License

This project is released under the [Apache 2.0 license](./LICENSE).
