# Foodgram Product Assistant Project

Working project on the domain:
```
iceadmin.ru
```

The Foodgram project is a web application implemented with React and Django. 
The Foodgram product assistant is created to allow users to publish their recipes,
subscribe to other authors, add recipes to favorites, and create a shopping
list based on the recipes in the cart. The site includes registration,
token-based authorization, an administrator panel, API requests,
and result filtering. It also has CI/CD through Git workflow and Docker.
The Foodgram application is hosted on a remote server. The application is
divided into containers: Frontend, Backend, Gateway, and Db. Upon pushing
to the main branch, a workflow instruction is triggered by Git actions.
Independent runners check the code using flake8, build images using
docker-compose, and push them to dockerhub. Upon successful completion of
actions, a message is sent to Telegram from a bot.

## Technology Stack:

```
Python 3.9.10
Django 3.2.16
gunicorn 20.1.0
djoser 2.1.0
nginx 1.19.3
postgres 12.4
```

## How to Run the Project: 

Clone the repository and navigate to it in the command line: 

```
git clone git@github.com:Ice444-222/grocery_assistant_django.git 
```

``` 
cd foodgram-project-react
```

Push to the main branch:

``` 
git push
```

Connect to the remote server and populate the database with initial data:

``` 
sudo docker compose -f docker-compose.yml exec backend python manage.py load_csv dbdata/ingredients.csv
```
Admin panel login details:
```
Username: ice
Password: ice
```
Create Tag model objects through the admin panel.


## Examples of Requests to the Application

### Request to the Home Page

A request to the home page will redirect to the authentication page if
the user is not logged in. If the user is already authenticated,
the page with all recipes will open.

```
https://iceadmin.ru/
```

### Adding a New Recipe

To access this page, you need to be authenticated.
You also need to upload an image of the recipe and select ingredients.

```
https://iceadmin.ru/recipes/create
```

### Editing a Recipe

Only the author of the recipe or an admin can edit a recipe.

```
https://iceadmin.ru/recipes/id/edit
```



## Workflow Status
![process](https://github.com/ice444-222/kittygram_final/actions/workflows/main.yml/badge.svg?event=push)
