FROM ubuntu:20.04

WORKDIR /labelu

RUN set -eux \
 && apt-get update \
 && apt-get install --no-install-recommends --no-install-suggests -y \
    python3-pip python3-dev

RUN pip3 install -i https://test.pypi.org/pypi/ --extra-index-url https://pypi.org/simple labelu
ENV HOME=/labelu

EXPOSE 8000

CMD ["labelu"]