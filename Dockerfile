FROM python:3.9-slim

RUN groupadd -r mimamori -g 1000 && useradd -r -g mimamori -u 1000 mimamori

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY . /usr/src/app

RUN chown -R mimamori:mimamori /usr/src/app

USER mimamori

CMD [ "python", "./mimamori/mimamori.py" ]