FROM python:3.7-slim

WORKDIR /labelu

RUN pip3 install -i https://test.pypi.org/pypi/ --extra-index-url https://pypi.org/simple labelu
ENV HOME=/labelu

EXPOSE 8000

CMD ["labelu"]