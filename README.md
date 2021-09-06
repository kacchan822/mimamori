# MIMAMORI

**MIMAMORI** is a simple website checker based on checksum.

## How to Use?

```console
$ mkdir mimamori
$ touch mimamori.db
$ touch mimamori.config.ini
$ docker run --rm -v $PWD/mimamori.db:/usr/src/app/mimamori/mimamori.db:rw -v $PWD/mimamori.config.ini:/usr/src/app/mimamori/mimamori.config.ini kacchan822/mimamori
```

## mimamori.config.ini

```
[Site1]
url = https://example.com/

[Site2]
url = https://example.net/

[Site3]
url = https://example.org/
```
