# Проект Foodgram продуктовый помощник

Рабочий проект на домене:
```
iceadmin.ru
```

Проект Foodgram это WEB приложение реализованное на React и Django.
Продуктовый помошник Foodgram создан с целью предоставить пользователям возможность
публиковать свои рецепты, подписываться на других авторов, добавлять рецепты в избранное,
составлять список продуктовой корзины на основе рецептов в корзине. На сайте реализована
регистрация, авторизация на основе токенов, панель админинстратора, api запросы, фильтрация
выдачи. Присутствует CI/CD через Git workflow и Docker. Приложение Foodgram работает на удалённом сервере. 
Приложение Foodgram делится на контейнеры: Frontend, Backend, Gateway, Db.
При пуше на ветку main, стартует инструкция workflow которую исполняет git actions. 
Запускаются независымые раннеры, которые проверяют код по flake8, идёт сборка 
образов по docker-compose, которые в дальнейшем пушатся на dockerhub. 
При успешном выполнении actions прходит сообщение на Telegram от бота.

## Стек технологий:

```
Python 3.9.10
Django 3.2.16
gunicorn 20.1.0
djoser 2.1.0
nginx 1.19.3
postgres 12.4
```

## Как запустить проект: 

Клонировать репозиторий и перейти в него в командной строке: 

```
git clone git@github.com:Ice444-222/grocery_assistant_django.git 
```

``` 
cd foodgram-project-react
```

Сделать пуш в ветку main:

``` 
git push
```

Подключиться к удалённому серверу и наполнить базу исходными данными:

``` 
sudo docker compose -f docker-compose.yml exec backend python manage.py load_csv dbdata/ingredients.csv
```
Данные для панели админинстратора:
```
логин: ice
пароль: ice
```
Через панель админинстратора создать объекты модели Tag


## Примеры запросов к приложению

### Запрос к главной странице

Запрос к главной странице перенаправит на страницу
аутентификация если пользователь не зашёл в свой аккаунт.
Если пользователь уже аутентифицирован, то откроется
страница со всеми рецептами.

```
https://iceadmin.ru/
```

### Добавление нового рецепта

Чтобы попасть на эту страницу надо быть аунтифицированным.
Необходимо также загрузить изоброжение рецепта и выбрать ингредиенты

```
https://iceadmin.ru/recipes/create
```

### Редактирование рецепта

Редактировать рецепт можно только автор рецепта или админ.

```
https://iceadmin.ru/recipes/id/edit
```



## Состояние рабочего процесса
![process](https://github.com/ice444-222/kittygram_final/actions/workflows/main.yml/badge.svg?event=push)
