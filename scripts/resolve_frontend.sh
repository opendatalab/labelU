#!/bin/bash

# 详细协同方案见：https://aicarrier.feishu.cn/wiki/wikcnEUfLmZc8rA378UuhHWC6Yt

# 参数顺序：branch version url
alpha_version=$(grep "alpha_version: " .VERSION | awk -F " " '{print $2}')
release_version=$(grep "release_version: " .VERSION | awk -F " " '{print $2}')
release_assets_url=$(grep "release_assets_url: " .VERSION | awk -F " " '{print $2}')
alpha_assets_url=$(grep "alpha_assets_url: " .VERSION | awk -F " " '{print $2}')

echo "alpha_version: $alpha_version"
echo "alpha_assets_url: $alpha_assets_url"
echo "release_version: $release_version"
echo "release_assets_url: $release_assets_url"

url=""
version=""

echo "branch: $CURRENT_BRANCH"

echo "args: $@"
echo "args len: $#"

if [ $# -gt 1 ]; then
  url=$3
  version=$2

  # 生成版本信息
  # 下次labelu迭代可使用对应分支上次下载的版本
  if [ "$1" = "alpha" ]; then
    echo "alpha_assets_url: $url" > .VERSION
    echo "alpha_version: $version" >> .VERSION
    echo "release_assets_url: $release_assets_url" >> .VERSION
    echo "release_version: $release_version" >> .VERSION
  elif [ "$1" = "release" ]; then
    echo "release_assets_url: $url" > .VERSION
    echo "release_version: $version" >> .VERSION
    echo "alpha_assets_url: $alpha_assets_url" >> .VERSION
    echo "alpha_version: $alpha_version" >> .VERSION
  fi
else
  if [ "$CURRENT_BRANCH" = "main" ]; then
    url=$release_assets_url
  else
    url=$alpha_assets_url
  fi
fi

echo "url: $url"

filename=$(basename $url)

echo "final url: $url"
echo "filename: $filename"

# 下载zip文件
wget $url

# 解压zip文件
unzip -o $filename

# 删除下载的zip文件
rm $filename

# 移动到指定目录
mv dist/* labelu/internal/statics

# 删除空目录
rm -rf dist