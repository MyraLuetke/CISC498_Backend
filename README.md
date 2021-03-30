# CISC498 Backend for ChecQin

This is a Django REST API used by our ChecQin application

## Environment Setup

1. Clone the repository.

2. Setup your virtual environment:
```bash
cd CISC498_Backend
pip install virtualenv
virtualenv venv
cd venv/Scripts
```
For Windows run:
```bash
activate.bat
```
For MacOS run:
```bash
./activate
```

3. Return to backend directory
```bash
cd CISC498_Backend/backend
```

4. Install requirements:
```bash
pip install -r requirements.txt
```

## Run Locally

1. Create database tables (on first setup):

```bash
cd CISC498_Backend/backend
python manage.py makemigrations
python manage.py migrate
```

2. Run the server:
```
python manage.py runserver
```

### Resources

- https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username/
- https://simpleisbetterthancomplex.com/tutorial/2018/12/19/how-to-use-jwt-authentication-with-django-rest-framework.html
- https://www.django-rest-framework.org/
- https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html
