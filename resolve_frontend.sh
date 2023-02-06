#!/bin/bash

# 详细协同方案见：https://aicarrier.feishu.cn/wiki/wikcnEUfLmZc8rA378UuhHWC6Yt

# 参数顺序：branch version url
if [ $# -eq 0 ]; then
  # 如果是labelu自己触发的ci，从版本文件中读取版本信息
  branch=$(grep "branch: " .VERSION | awk -F " " '{print $2}')
  version=$(grep "version: " .VERSION | awk -F " " '{print $2}')
  url=$(grep "assets_url: " .VERSION | awk -F " " '{print $2}')
else
  if [ $# -ne 3 ]; then
    echo "Error: Incorrect number of arguments."
    exit 1
  fi

  branch="$1"
  version="$2"
  url="$3"

  # 生成版本信息
  #下次labelu迭代可使用对应分支上次下载的版本
  echo "version: $version" > .VERSION
  echo "branch: $branch" > .VERSION
  echo "assets_url: $url" >> .VERSION

fi

filename=$(basename $url)

# 下载zip文件
wget $url

# 解压zip文件
unzip -o $filename

# 删除下载的zip文件
rm $filename

# 移动到指定目录
mv dist/* labelu/internal/statics