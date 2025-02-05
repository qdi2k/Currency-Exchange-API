# Currency-Exchange-API
API проект для обмена валют. 
Пользователи могут получать последние курсы обмена различных валют 
и выполнять их конвертацию

---
## Перед стартом - обязательно
0.  В корне создайте файл `.env` и наполните его в предложенном формате 
    в `example.env`

## Старт на localhost - вручную

1. Если у вас нет виртуального окружения, то создайте и активируйте его
```shell
    python -m venv venv
```
```shell
    venv\Scripts\activate.bat
```

2. Обновите pip и установите необходимые зависимости
```shell
    python.exe -m pip install --upgrade pip
```
```shell
    pip install -r requirements.txt
```
3. Примените существующие миграций
```bash 
   alembic upgrade head
```
4. Запустите сервер
```shell
    uvicorn main:app --reload
```

---
Для того чтобы перезаписать миграции
```bash 
   alembic revision --autogenerate -m 'initial'
```
```bash 
   alembic upgrade head
```
