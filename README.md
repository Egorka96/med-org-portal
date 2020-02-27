# Портал для организаций-заказчиков медицинских организаций

## Настройка среды разработки
1. Склонировать код из репозитория
    ```shell script
    git clone git@github.com:Egorka96/med-org-portal.git
    ```

1. Скачать интерпретатор python с официального сайта
   ```shell script
    mkdir /tmp/Python38; \
    cd /tmp/Python38; \
    wget https://www.python.org/ftp/python/3.8.1/Python-3.8.1.tar.xz; \
    tar xvf Python-3.8.1.tar.xz; \
    cd /tmp/Python38/Python-3.8.1; \
    ./configure; \
    make install; \
    cd /; \
    rm -rf /tmp/Python38
    ```

1. Перейти в папку с проектом и активировать виртуальное окружение
   ```shell script
   cd med-org-portal
   python -m venv venv
   source venv/bin/activate
   ```
   
1. Установить зависимости проекта
    ```shell script
    pip install -r requirements.txt
    ```
   
1. Прогнать миграции и создать суперпользователя
    ```shell script
    python manage.py migrate
    python manage.py createsuperuser
    ```
   
1. Установить статику из package.json
    ```shell script
    npm install
    ```
   
1. Запустить django-проект
    ```shell script
    python manage.py runserver 
    ```
