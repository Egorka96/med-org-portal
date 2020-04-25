FROM python:3.8-slim-buster

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get clean && apt-get update && apt-get install -y \
        vim curl supervisor locales tzdata libpq-dev postgresql-client \
        libjpeg-dev zlib1g-dev python3-dev python3-lxml npm \
    && rm -rf /var/lib/apt/lists/*

RUN locale-gen ru_RU.UTF-8
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU:ru
ENV LC_ALL ru_RU.UTF-8

RUN ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime
RUN dpkg-reconfigure --frontend noninteractive tzdata

ENV PYTHONUNBUFFERED 1

COPY . /opt/app
WORKDIR /opt/app

ADD requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt
RUN npm install

RUN cp project/local_settings.sample.py project/local_settings.py

COPY supervisor/supervisord.conf /etc/supervisor/supervisord.conf
COPY supervisor/prod.conf /etc/supervisor/conf.d/app.conf

EXPOSE 80
VOLUME /data/
VOLUME /conf/
VOLUME /static/
VOLUME /media/


CMD test "$(ls /conf/local_settings.py)" || cp project/local_settings.sample.py /conf/local_settings.py; \
    rm project/local_settings.py;  ln -s /conf/local_settings.py project/local_settings.py; \
    rm -rf static; ln -s /static static; \
    rm -rf media; ln -s /media media; \
    python3 ./manage.py migrate; \
    python3 ./manage.py collectstatic --noinput; \
    npm install; rm -rf static/node_modules; mv node_modules static/; \
    /usr/bin/supervisord -c /etc/supervisor/supervisord.conf --nodaemon
