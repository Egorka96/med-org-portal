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
   python3.8 -m venv venv
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
    
## Добавление изменений в репозиторий
В терминале, в папке с проектом, необходимо выполнить следующие действия:

1. Создать локально новую ветку (если изменения соответствуют какой-либо задаче из списка https://github.com/Egorka96/med-org-portal/issues, название ветки должно соответствовать номеру задачи)
    ```shell script
    git branch <название_ветки>
    ```
2. Перейти в ветку 
    ```shell script
    git checkout <название_ветки>
    ```
3. Вносите необходимые дополнения/измненеия
4. Добавляете изменения в git 
    ```shell script
    git add .
    ```
5. Коммитите изменения в ветку. Если изменения связаны с определенной задачей, формат сообщения должен быть такой: "#номер_задачи краткое_описание_изменений"
    ```shell script
    git commit . -m 'краткое_описание_изменений'
    ```
6. Отправляете изменения на сервер
    ```shell script
    git push origin <название_ветки>
    ```
