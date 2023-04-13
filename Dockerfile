FROM python:3.7-slim

WORKDIR /labelu

RUN pip3 install -i https://test.pypi.org/pypi/ --extra-index-url https://pypi.org/simple -U labelu
ENV MEDIA_HOST http://labelu.shlab.tech

EXPOSE 8000

CMD ["sh", "-c", "labelu --host=0.0.0.0 --media-host=$MEDIA_HOST"]