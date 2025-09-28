# dendroscan-ml
Репозиторий с ML сервисом.

## Работа с DVC репозиторием:
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
  