# dendroscan-ml
Репозиторий с ML сервисом.
## Инструкции по сборке и запуску

## Требования
- OS Linux (Ubuntu 22.04 LTS)
- Docker
- Docker Compose
- Внешнее S3 совместимое хранилище.

## Установка
1. Скопируйте файл `.env.example`
    ```bash
    cp .env.example .env
    ```
2. Скачайте веса для моделей по ссылке: https://disk.yandex.ru/d/CZrT-Wws1XJNqw
   - Это 2 файла - `best.pt` и `mobileclip_s1.pt`
   - Скопируйте эти файлы в папку `models`

3. Заполните файл актуальными данными
4. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/dendroscan/dendroscan-ml.git
   ```
## Инструкция по запуску сервиса

Для запуска сервиса из репозитория `dendroscan-ml` выполните следующие шаги:
1. Убедитесь, что на вашем компьютере установлен Docker и Docker Compose.
2. Склонируйте данный репозиторий на свой компьютер.
3. Перейдите в корневую директорию репозитория `dendroscan-ml`.
4. Выполните команду для загрузки Docker образа из репозитория DockerHub:
   ```bash
   docker compose pull
   ```
5. Выполните команду для запуска всех сервисов, описанных в файле `docker-compose.yml`:

   ```bash
   docker compose up -d
   ```
   Эта команда запустит следующие сервисы:
   - `backend`: API-сервис на порту 8000.
   - `ml-service`: ML-сервис на порту 8080.
   - `db`: База данных PostgreSQL.
   - `nginx`: Веб-сервер Nginx на портах 80 и 443.
   - `minio`: S3 совместимое Хранилище

6. После запуска сервисов вы можете проверить их статус с помощью команды:
   ```bash
   docker compose ps
   ```

7. Для остановки сервисов выполните команду:
   ```bash
   docker compose down
   ```
## Работа с DVC репозиторием (Только для мантейнеров):
- После обучения/дообучения модели `best.pt` необходимо выполнить следующие 
команды:

    ```bash
    export AWS_ACCESS_KEY_ID=<your-key>  
    ```
    ```bash
    export AWS_SECRET_ACCESS_KEY=<your-secret>
    ```
    ```bash
    dvc add models/best.pt
    ```
    ```bash
    git add models/best.pt.dvc
    ```
    ```bash
    git commit -m "Update model"
    ```
    ```bash
    dvc push
    ```
    ```bash
    git push
    ```