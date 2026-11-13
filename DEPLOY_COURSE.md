# 🚀 Курс: выкладываем ToDo-сайт в интернет с помощью Docker

## 🗺️ План

| Этап | Что делаем | Статус |
|---|---|---|
| 1 | Что такое Docker + установка | ✅ |
| 2 | Готовим Django к продакшену (секреты, DEBUG, gunicorn, статика) | ✅ |
| 3 | Пишем Dockerfile и запускаем сайт в контейнере у себя | ✅ |
| 4 | docker-compose + PostgreSQL | ✅ |
| 5 | Заливаем код на GitHub | ✅ https://github.com/crstalk/todo-django |
| 6 | Арендуем сервер и запускаем там | ✅ http://51.250.40.90:8000 |
| 7 | Домен + HTTPS | |

---

## 📦 Урок 1. Что такое Docker

**Проблема:** у меня на компьютере сайт работает (Windows, Python, Django в .venv), а на сервере (Linux) ничего этого нет. Отсюда вечное «а у меня работало!».

**Решение — контейнер.** Как транспортный контейнер: внутри что угодно, а снаружи стандартная коробка, которая едет на любом корабле. Docker упаковывает **код + Python + библиотеки + настройки** в одну коробку, и она одинаково запускается где угодно.

| Слово | Что это | Аналогия |
|---|---|---|
| **Dockerfile** | Текстовая инструкция по сборке | Рецепт торта |
| **Image (образ)** | Собранный неизменяемый «слепок» | Испечённый торт в морозилке |
| **Container (контейнер)** | Запущенный экземпляр образа | Кусок торта на тарелке |

```
Dockerfile  --(docker build)-->  Image  --(docker run)-->  Container
```

### Задание
- [ ] Закоммитить работу: `git add .` → `git commit -m "Рабочая версия перед деплоем"`
- [ ] В папке `ToDo` (где manage.py), с активированным .venv: `pip freeze > requirements.txt`
- [ ] Установить Docker Desktop (с галочкой «Use WSL 2»)
- [ ] Проверить: `docker --version` и `docker run hello-world`
- [ ] Ответить себе: чем образ отличается от контейнера?

### Проблема при установке: «Virtual Machine Platform is not enabled»
Docker работает на **WSL** (Linux внутри Windows), а WSL нужна функция Windows для виртуальных машин. Она выключена, а включать её может только администратор.

Как исправить:
1. Пуск → `PowerShell` → правой кнопкой → **Запуск от имени администратора**
2. Выполнить `wsl --install`
3. **Перезагрузить** компьютер
4. Если откроется Ubuntu, придумать логин и пароль (пароль при вводе не видно, это нормально)
5. Снова запустить установщик Docker Desktop

Если появится ошибка про **BIOS / virtualization**, нужно включить виртуализацию в BIOS (спросить Claude и назвать модель ноутбука).

### Заметки после установки
- В Docker две части: **клиент** (`docker` в терминале, «пульт») и **движок** Docker Engine («телевизор»). Если пишет `failed to connect to the docker API`, значит не запущен Docker Desktop.
- После установки открой **новый** терминал, чтобы он увидел команду `docker`.
- PowerShell при `>` сохраняет файлы в UTF-16. Для requirements.txt используй:
  `pip freeze | Set-Content -Encoding ascii requirements.txt`

---

## 🔒 Урок 2. Готовим Django к жизни в интернете

| Проблема | Почему опасно | Решение |
|---|---|---|
| `SECRET_KEY` в коде | Им подписываются сессии; зная его, можно войти под чужим аккаунтом. Код будет на GitHub | Брать из **переменной окружения** |
| `DEBUG = True` | При ошибке показывает код и настройки всему миру | В продакшене `DEBUG = False` |
| `ALLOWED_HOSTS = []` | При DEBUG=False Django отвечает ошибкой 400 | Список разрешённых адресов сайта |
| `runserver` | Игрушечный сервер для разработки | **gunicorn** (работает только на Linux, поэтому Docker) |
| Статика при DEBUG=False | Django перестаёт отдавать CSS/JS | **WhiteNoise** + `collectstatic` |

**Переменные окружения** — «записки», которые ОС передаёт программе при запуске. Код один, а записки (секреты) на каждом компьютере свои. Значения всегда **строки**.

**Gunicorn** — ресторан с несколькими официантами (workers), а `runserver` — ты сам разносишь чай.

### Задание
- [ ] `pip install gunicorn whitenoise` + пересоздать requirements.txt
- [ ] `import os` в начале settings.py
- [ ] Заменить настройки:
```python
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-только-для-разработки')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```
- [ ] В MIDDLEWARE сразу после SecurityMiddleware: `'whitenoise.middleware.WhiteNoiseMiddleware',`
- [ ] `STATIC_ROOT = BASE_DIR / 'staticfiles'`
- [ ] `python manage.py collectstatic`, потом `runserver`: сайт работает как раньше
- [ ] `staticfiles/` в .gitignore
- [ ] Вопросы себе: что делает второй аргумент `os.environ.get`? Зачем `== '1'`?

### Шпаргалка: зачем каждое изменение
| Что поменяли | Зачем |
|---|---|
| `SECRET_KEY` из окружения | Секрет не должен лежать в коде на GitHub |
| `DEBUG` из окружения | В интернете не показывать код при ошибках |
| `ALLOWED_HOSTS` | Отвечать только на разрешённые адреса |
| WhiteNoise | Отдаёт CSS/JS при DEBUG=False |
| `STATIC_ROOT` + `collectstatic` | Собирает всю статику в одну папку |

### Уроки из ошибок
- **Порядок MIDDLEWARE важен.** Это цепочка охранников, запрос идёт сверху вниз. WhiteNoise ставим **вторым**, сразу после SecurityMiddleware.
- **Файлы создаются в текущей папке терминала.** Смотри на путь слева в строке `PS C:\...>`.

---

## 🐳 Урок 3. Первый Dockerfile

Файлы `Dockerfile` и `.dockerignore` лежат в `ToDo/ToDo/` (рядом с manage.py).

```dockerfile
FROM python:3.12-slim                 # готовая заготовка: Linux + Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1                # логи сразу, без задержки
WORKDIR /app                          # рабочая папка в контейнере
COPY requirements.txt .               # сначала только зависимости (кэш!)
RUN pip install --no-cache-dir -r requirements.txt
COPY . .                              # потом весь код
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate && gunicorn ToDo.wsgi:application --bind 0.0.0.0:8000"]
```

- **Кэш слоёв:** requirements.txt копируем отдельно, чтобы при изменении кода не переустанавливать библиотеки.
- **RUN** выполняется при сборке (испекли торт), **CMD** при запуске (подали на стол).
- **0.0.0.0** = слушать запросы отовсюду, а не только изнутри контейнера.
- **.dockerignore** работает как .gitignore для Docker. db.sqlite3 в образ не кладём: там личные данные.

### Команды
```powershell
docker build -t todo-app .
docker run --name todo -p 8000:8000 -e DJANGO_DEBUG=0 -e DJANGO_SECRET_KEY=длинная-строка todo-app
docker exec -it todo python manage.py createsuperuser
docker stop todo ; docker rm todo
```
- `-p 8000:8000` — проброс порта: дверь с моего компьютера в «квартиру»-контейнер
- `-e` — переменная окружения
- `exec` — выполнить команду внутри работающего контейнера

| Команда | Что делает |
|---|---|
| `docker ps` / `docker ps -a` | Работающие / все контейнеры |
| `docker images` | Образы |
| `docker logs todo` | Логи (смотреть при ошибках!) |

### Задание
- [x] Вернуть WhiteNoise в MIDDLEWARE (второй строкой)
- [x] Создать Dockerfile и .dockerignore
- [x] Собрать образ и запустить, открыть http://localhost:8000 🎉 Сайт работает в Linux на gunicorn с DEBUG=False!
- [ ] Создать суперпользователя через `docker exec`
- [ ] Эксперимент: stop + rm + run заново. Куда делись данные и почему?

### Ошибки урока 3 и как их чинили
- **`'docker buildx build' requires 1 argument`** — забыл точку в конце `docker build -t todo-app .` Точка означает «текущая папка», где лежит Dockerfile.
- **`The container name "/todo" is already in use`** — упавший контейнер не удаляется сам. Лечится `docker rm todo`.
- **`SessionMiddleware must be in MIDDLEWARE`** — пропущена запятая после WhiteNoise. Python **склеивает** соседние строки без запятой: `'abc' 'def'` → `'abcdef'`. Ставь запятую после каждого элемента списка, даже последнего.
- **После изменения кода образ нужно пересобрать**: образ — замороженный слепок.

### 🔧 Алгоритм отладки контейнера
1. `docker ps -a` — статус (`Exited (1)` = упал с ошибкой)
2. `docker logs todo` — **почему** упал
3. Исправить → `docker rm todo` → `docker build -t todo-app .` → `docker run ...`

### `container is not running` и флаг `-d`
- Без `-d` команда `docker run` **занимает терминал**. Закрыл терминал или нажал Ctrl+C, и контейнер остановился.
- `docker run -d ...` запускает контейнер **в фоне**, терминал остаётся свободным. Логи смотрим через `docker logs todo`.
- Остановленный контейнер можно включить обратно: `docker start todo`.
- `docker exec` работает только с **запущенным** контейнером.

### Зачем шаги 5–6
- **`docker exec`** — способ выполнять команды внутри контейнера (создать админа, миграции). На сервере нужен постоянно.
- **Главный вывод:** при удалении контейнера **все данные внутри него исчезают**. База `db.sqlite3` создаётся внутри одноразовой коробки. На сервере контейнер пересоздаётся при каждом обновлении, поэтому базу нужно вынести наружу (урок 4).

### `pull access denied for todo` — перепутал образ и контейнер
| | Имя | Откуда |
|---|---|---|
| Образ | `todo-app` | `docker build -t todo-app .` |
| Контейнер | `todo` | `docker run --name todo ...` |

- `docker run` ждёт **имя образа** (в самом конце команды). Если такого образа нет локально, Docker ищет его на Docker Hub.
- `start / stop / rm / logs / exec` работают с **контейнером**.
- `docker images` — список образов, `docker ps -a` — список контейнеров.

✅ Эксперимент подтвердил: после `rm` + `run` пользователей стало 0.

---

## 🐘 Урок 4. Docker Compose + PostgreSQL

**Volume** — «флешка», которую Docker хранит отдельно от контейнеров. Контейнер (гостиничный номер) убрали, а флешка осталась.
**PostgreSQL** — настоящая база для продакшена, тоже работает в своём контейнере.
**Docker Compose** — дирижёр: один файл `docker-compose.yml` описывает все контейнеры, а запуск одной командой.
**Имя сервиса = адрес.** Внутри сети Compose контейнеры находят друг друга по имени (`HOST = 'db'`).

### Файлы (всё в `ToDo/ToDo/`)
- `pip install "psycopg[binary]"` + пересоздать requirements.txt
- `.env` — секреты (в git и в образ НЕ попадает):
```env
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=todo
POSTGRES_USER=todo
POSTGRES_PASSWORD=...
POSTGRES_HOST=db
POSTGRES_PORT=5432
```
- `settings.py`: если есть `POSTGRES_DB`, используем postgresql, иначе sqlite.
- `docker-compose.yml`:
```yaml
services:
  db:
    image: postgres:17
    env_file: .env
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      retries: 10
  web:
    build: .
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
volumes:
  pgdata:
```
- `healthcheck` + `depends_on`: сайт ждёт, пока база будет готова.

### Шпаргалка
| Команда | Что делает |
|---|---|
| `docker compose up -d --build` | Собрать и запустить всё |
| `docker compose ps` | Статус |
| `docker compose logs web` | Логи сайта |
| `docker compose exec web python manage.py createsuperuser` | Команда внутри сервиса |
| `docker compose down` | Удалить контейнеры (данные целы) |
| `docker compose down -v` | ☠️ Удалить контейнеры И данные |

### Задание
- [ ] `docker stop todo` + `docker rm todo`
- [ ] psycopg, .env, settings, docker-compose.yml
- [ ] `docker compose up -d --build`, сайт открывается
- [ ] createsuperuser, создать задачи
- [ ] `down` → `up -d`: данные на месте?
- [ ] Вопрос: разница между `down` и `down -v`?

### Ошибка урока 4: `service "db" refers to undefined volume pgdata`
Файл скопировался не до конца: не было блока `volumes: pgdata:` в конце, который **объявляет** volume. А ещё `services:` и `volumes:` должны стоять у левого края. В YAML отступы важны, делаются пробелами по 2.
💡 `docker compose config` проверяет файл до запуска.

✅ Итог урока 4: база PostgreSQL, 2 пользователя пережили `down` → `up`, volume `todo_pgdata`.

---

## 🐙 Урок 5. GitHub

```
Компьютер --(git push)--> GitHub --(git clone)--> Сервер
```
**Git** — сохранения в игре (локально). **GitHub** — облачные сохранения + портфолио.

### Шаги
1. `git add .` → `git status`: **проверить, что нет .env, db.sqlite3, staticfiles, .venv**
2. `git commit -m "..."`
3. github.com → New repository, **пустой** (без README / .gitignore / license)
4. Связать и отправить:
```powershell
git remote add origin https://github.com/ЛОГИН/todo-django.git
git branch -M main
git push -u origin main
```
- `remote add origin` — запомнить адрес облака под именем origin
- `branch -M main` — переименовать master в main
- `push -u` — отправить и запомнить связку (дальше просто `git push`)
5. Проверить на GitHub, что `.env` там нет.

### Правило про секреты
Если секрет попал в git, его не прячут, а **заменяют на новый**. Старый `django-insecure-...` ключ остался в Initial commit, но на сервере используется новый из `.env`.

✅ Итог урока 5: код на https://github.com/crstalk/todo-django, секретов в репозитории нет.

---

## 🖥️ Урок 6А. VPS + SSH + Docker на сервере

**Сервер** — компьютер в дата-центре, работает 24/7, у него есть публичный IP-адрес. Его берут в аренду.
**VPS vs PaaS:** выбрали VPS, потому что наш docker-compose работает как есть, а заодно учимся Linux и SSH.

**SSH** — защищённый удалённый терминал.
| Файл | Аналогия | Показывать? |
|---|---|---|
| `id_ed25519.pub` | 🔒 замок | ✅ да, вешаем на сервер |
| `id_ed25519` | 🔑 ключ | ❌ никогда и никому |

### Шаги
1. `ssh-keygen -t ed25519 -C "todo-server"` → `cat ~\.ssh\id_ed25519.pub`
2. Арендовать VPS: **Ubuntu 24.04**, 1 vCPU, 2 ГБ RAM (минимум 1), 15–25 ГБ диск, вставить публичный ключ
3. `ssh root@IP` → `yes` при первом входе. Выйти с сервера: `exit`
4. `apt update && apt upgrade -y` (apt — «магазин приложений» Ubuntu)
5. `curl -fsSL https://get.docker.com | sh` → `docker run hello-world`

### Вариант: Yandex Cloud (Compute Cloud)
- Оплата поминутная, пока ВМ работает. Есть стартовый грант для новых. Публичный IP оплачивается отдельно.
- Вход **не под root**: логин задаёшь сам при создании → `ssh artur@IP`, команды администратора через `sudo`.
- Настройки ВМ: Ubuntu 24.04, 2 vCPU, гарантированная доля **50%**, 2 ГБ RAM, диск 20 ГБ, **НЕ прерываемая**, публичный адрес **Автоматически**, вставить SSH-ключ.
- Динамический IP меняется после остановки ВМ. Перед уроком 7 сделать статическим (VPC → IP-адреса).
- Docker: `curl -fsSL https://get.docker.com | sudo sh` → `sudo usermod -aG docker $USER` → `exit` и переподключиться → `docker run hello-world`.
- Остановленная ВМ не платит за CPU/RAM, но платит за диск и IP.

### Заметки по серверу
- Строка ввода `arthur@...:~$` означает, что ты на **сервере**, `PS C:\...>` — на своём компьютере. `$` — обычный пользователь, `#` — root.
- `permission denied ... docker.sock` → нет прав на Docker: `sudo usermod -aG docker $USER` → `exit` → переподключиться. Проверка: `groups`.
- `command not found` чаще всего означает опечатку. **Tab** дописывает команды, **↑** вызывает прошлую команду.
- Копирование в терминале: выделить + правая кнопка мыши (или Ctrl+Shift+C). `Ctrl+C` = прервать команду!
- Сервер: Yandex Cloud, 2 vCPU, 1.9 ГБ RAM, 20 ГБ HDD, пользователь `arthur`.

---

## 🌍 Урок 6Б. Запуск сайта на сервере
```
Дома:    код в папке → .env → docker compose up
Сервер:  git clone   → .env → docker compose up   (то же самое!)
```
1. `git clone https://github.com/crstalk/todo-django.git` → `cd todo-django/ToDo`
2. Новые секреты для сервера: `openssl rand -base64 48` (ключ), `openssl rand -base64 24` (пароль БД)
3. `nano .env`, в `DJANGO_ALLOWED_HOSTS` = **IP сервера**. nano: `Ctrl+O` Enter — сохранить, `Ctrl+X` — выйти
4. `docker compose up -d --build` → `docker compose ps`
5. `docker compose exec web python manage.py createsuperuser`
6. Открыть `http://IP:8000`, проверить с телефона через мобильный интернет

Если не открывается: `docker compose logs web`. 400 → ALLOWED_HOSTS. Долго грузится → группа безопасности Yandex Cloud закрывает порт.
Порт 80/443 (без `:8000`) + HTTPS → урок 7.

✅ **Итог урока 6: сайт в интернете: http://51.250.40.90:8000** (gunicorn, DEBUG выключен, статика работает) 🥳

---

## 🔄 Как обновить сайт
```powershell
# дома
git add .
git commit -m "что изменил"
git push
```
```bash
# на сервере
cd ~/todo-django/ToDo
git pull
docker compose up -d --build
```
Данные сохраняются в volume `pgdata`. **Никогда не запускай на сервере `docker compose down -v`**: эта команда удалит базу.

## ⚠️ Помнить
- Сайт пока работает по HTTP: пароли идут без шифрования. Это исправит урок 7 (домен + HTTPS).
- Yandex Cloud списывает деньги, пока ВМ работает. Остановленная ВМ платит только за диск и IP.
- Перед уроком 7 сделать IP статическим (VPC → IP-адреса).

---

## 🌐 Урок 7А. Домен и DNS — ✅ http://todo-arthur.ru:8000
- **DNS** — телефонная книга интернета: имя → IP. **A-запись** связывает имя с IPv4.
- Записи у REG.RU: `@` → 51.250.40.90, `www` → 51.250.40.90. IP в Yandex Cloud сделан статическим.
- `NXDOMAIN` = домена не существует (или записи ещё не разошлись; ответ «нет» тоже кэшируется).
- **400 по домену** → домена нет в `DJANGO_ALLOWED_HOSTS`. Исправление на сервере: `.env` → `DJANGO_ALLOWED_HOSTS=todo-arthur.ru,www.todo-arthur.ru,51.250.40.90` → `docker compose up -d --force-recreate web` (код не менялся, поэтому `--build` не нужен).

## 🔒 Урок 7Б. HTTPS через Caddy
- HTTP — открытка, HTTPS — запечатанный конверт. Сертификат выдаёт Let's Encrypt (бесплатно, автоматически).
- **Caddy** — обратный прокси («ресепшен»): слушает 80/443, сам получает сертификат, перенаправляет http → https, передаёт запросы в `web:8000`.
- **Профили Compose:** `profiles: ["prod"]` — сервис запускается только при включённом профиле (на сервере `COMPOSE_PROFILES=prod` в .env).
- `"127.0.0.1:8000:8000"` — порт 8000 открыт только для своего компьютера, в обход Caddy не попасть.
- Сертификаты храним в volume `caddy_data`, потому что у Let's Encrypt есть лимиты на выдачу.
- Django за прокси: `SECURE_PROXY_SSL_HEADER` (иначе CSRF 403 на форме входа), `SESSION/CSRF_COOKIE_SECURE`. Всё это внутри `if DJANGO_HTTPS == '1'`, чтобы дома работал вход по http.

Caddyfile:
```
{$DOMAIN}, www.{$DOMAIN} {
    reverse_proxy web:8000
}
```
