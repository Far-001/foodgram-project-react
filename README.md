# Foodgram — социальная сеть для обмена рецептами.

### Описание проекта
Пользователи могут регистрироваться, загружать новые рецепты, добавлять их в избранное, в список покупок, а так же подписываться на авторов.

### Установка
<i>Примечание: Все примеры указаны для Linux</i><br>
1. Склонируйте репозиторий на свой компьютер:
    ```
    git clone git@github.com:Far-001/foodgram-project-react.git
    ```
2. Создайте файл `.env` и заполните его своими данными. Все необходимые переменные перечислены в файле `.env.example`, находящемся в корневой директории проекта.

### Создание Docker-образов

1. Замените `USERNAME` на свой логин на DockerHub:

    ```
    cd frontend
    docker build -t USERNAME/kittygram_frontend .
    cd ../backend
    docker build -t USERNAME/kittygram_backend . 
    ```

2. Загрузите образы на DockerHub:

    ```
    docker push USERNAME/kittygram_frontend
    docker push USERNAME/kittygram_backend
    ```

### Деплой на сервере

1. Подключитесь к удаленному серверу

    ```
    ssh -i PATH_TO_SSH_KEY/SSH_KEY_NAME USERNAME@SERVER_IP_ADDRESS 
    ```

2. Создайте на сервере директорию `foodgram`:

    ```
    mkdir foodgram
    ```

3. Установите Docker Compose на сервер:

    ```
    sudo apt update
    sudo apt install curl
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo apt install docker-compose
    ```

4. Скопируйте файлы `docker-compose.yml` и `.env` в директорию `foodgram/infra` на сервере:

    ```
    scp -i PATH_TO_SSH_KEY/SSH_KEY_NAME infra/docker-compose.yml USERNAME@SERVER_IP_ADDRESS:/home/USERNAME/foodgram/infra/docker-compose.yml
    ```
    
    Где:
    - `PATH_TO_SSH_KEY` - путь к файлу с вашим SSH-ключом
    - `SSH_KEY_NAME` - имя файла с вашим SSH-ключом
    - `USERNAME` - ваше имя пользователя на сервере
    - `SERVER_IP_ADDRESS` - IP-адрес вашего сервера

5. Запустите Docker Compose в режиме демона:

    ```
    sudo docker-compose -f /home/YOUR_USERNAME/foodgram/infra/docker-compose.yml up -d
    ```

6. Выполните миграции, соберите статические файлы бэкенда и скопируйте их в `/backend_static/static/`:

    ```
    sudo docker-compose exec backend python manage.py migrate
    sudo docker-compose exec backend python manage.py collectstatic
    sudo docker-compose exec backend cp -r /app/collected_static/. /backend_static/static/
    ```

7. Откройте конфигурационный файл Nginx в редакторе nano:

    ```
    sudo nano /etc/nginx/sites-enabled/default
    ```

8. Измените настройки `location` в секции `server`:

    ```
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1;
    }
    ```

9. Проверьте правильность конфигурации Nginx:

    ```
    sudo nginx -t
    ```

    Если вы получаете следующий ответ, значит, ошибок нет:

    ```
    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful
    ```

10. Перезапустите Nginx:

    ```
    sudo service nginx reload
    ```

### Настройка CI/CD

1. Файл workflow уже написан и находится в директории:

    ```
    foodgram/.github/workflows/main.yml
    ```

2. Для адаптации его к вашему серверу добавьте секреты в GitHub Actions:

    ```
    DOCKER_USERNAME                # имя пользователя в DockerHub
    DOCKER_PASSWORD                # пароль пользователя в DockerHub
    HOST                           # IP-адрес сервера
    USER                           # имя пользователя
    SSH_KEY                        # содержимое приватного SSH-ключа (cat ~/.ssh/id_rsa)
    SSH_PASSPHRASE                 # пароль для SSH-ключа

    TELEGRAM_TO                    # ID вашего телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
    TELEGRAM_TOKEN                 # токен вашего бота (получить токен можно у @BotFather, команда /token, имя бота)
    ```

### Технологии
Python 3.10.12,
Django 3.2.3,
djangorestframework==3.12.4, 
PostgreSQL 13.10

### Автор
Антон Корчагин - [Far-001](https://github.com/Far-001)

[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=Python+developer+and+student)](https://git.io/typing-svg)
