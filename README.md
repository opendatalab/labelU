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
LabelU provides a comprehensive set of tools for image annotation, including 2D bounding boxes, semantic segmentation, polylines, and keypoints. These tools can flexibly address a variety of image processing tasks, such as object detection, scene analysis, image recognition, and machine translation, helping users efficiently identify, annotate, and analyze images.

### Powerful Video Annotation Capabilities
In the realm of video annotation, LabelU showcases impressive processing capabilities, supporting video segmentation, video classification, and video information extraction. It is highly suitable for applications such as video retrieval, video summarization, and action recognition, enabling users to easily handle long-duration videos, accurately extract key information, and support complex scene analysis, providing high-quality annotated data for subsequent model training.

### Efficient Audio Annotation Tools
Audio annotation tools are another key feature of LabelU. These tools possess efficient and precise audio analysis capabilities, supporting audio segmentation, audio classification, and audio information extraction. By visualizing complex sound information, LabelU simplifies the audio data processing workflow, aiding in the development of more accurate models.

### Artificial Intelligence Assisted Labelling
LabelU supports one-click loading of pre-annotated data, which can be refined and adjusted according to actual needs. This feature improves the efficiency and accuracy of annotation.


https://github.com/user-attachments/assets/0fa5bc39-20ba-46b6-9839-379a49f692cf




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

> **Note：** If your system is MacOS with an Intel chip, please install [Miniconda of intel x86_64](https://repo.anaconda.com/miniconda/).

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

> To install the test version：`pip install labelu==<test revision>`

Install labelu with MySQL support：

```bash
pip install labelu[mysql]

# Or install labelu and mysqlclient separately
# pip install labelu mysqlclient
```

5. Run LabelU：

```bash
labelu
```

> If you need to use MySQL database after upgrading from version 1.x, run the following command to migrate data from the built-in SQLite database to the MySQL database:

```bash
DATABASE_URL=mysql://<username>:<password>@<host>/<your dbname> labelu migrate_to_mysql
```

1. Visit [http://localhost:8000/](http://localhost:8000/) and ready to go.

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

# Download the frontend statics from labelu-kit repo
sh ./scripts/resolve_frontend.sh true

# Start labelu, server: http://localhost:8000
uvicorn labelu.main:app --reload
```


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
