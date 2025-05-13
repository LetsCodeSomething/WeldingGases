## Описание

Модели **qwen2.5**, **phi4**, **gemma3** и **deepseek-R1** можно запустить с помощью инструмента **Ollama** и веб-интерфейса **Open WebUI**.


## Установка

Развертывание осуществляется в Docker-мультиконтейнере с использованием файла `docker-compose.yml` следующего содержания:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ollama:/root/.ollama        # модели и кеш
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
    tty: true
    restart: unless-stopped

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    depends_on:
      - ollama
    ports:
      - "3001:8080"
    volumes:
      - open-webui:/app/backend/data   # сохранение истории чатов
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY:-}  # можно задать в .env
      # - WEBUI_AUTH=True                       # включить страницу логина
    restart: unless-stopped

volumes:
  ollama: {}
```

### Предварительные требования

На сервере обязательно должна быть установлена видеокарта Nvidia с поддержкой CUDA и драйвер **nvidia-smi**.

### Первичная настройка

После запуска контейнеров перейдите по адресу: `http://<ip сервера>:3001`.

* Создайте учётную запись администратора.
* В интерфейсе чата (верхний левый угол) скачайте необходимые модели (список моделей доступен [здесь](https://ollama.com/search)).
* Затем перейдите в раздел **Панель администратора → Настройки → Модели** и укажите системные промпты для каждой модели из файла `prompt.txt`.

После этих шагов модели будут готовы к использованию.

## Проверка работоспособности

Вы можете протестировать работу по следующему адресу:

* URL: [http://194.247.182.32:3001](http://194.247.182.32:3001)
* Логин: `frenirus125@yandex.ru`
* Пароль: `demo`

Там уже настроены четыре чата, каждый для своей модели.

## Использование

Отправляйте в чат неструктурированную информацию о смесях газов. Модель в ответ должна присылать данные в формате JSON.

Полученный JSON необходимо сохранить в файл, после чего использовать скрипт `convert_data_from_ollama.py`:

```bash
python convert_data_from_ollama.py <путь_к_входному_файлу> [имя_выходного_файла]
```

* Если второй аргумент не указан, результат будет сохранён в файл с именем `<имя_входного_файла>_converted.json`.

Пример запуска:

```bash
python convert_data_from_ollama.py input1.json
```

Файл-пример `input1.json` находится в репозитории.

Полученный файл можно использовать в качестве входных данных для скрипта `json_converter.py`.
