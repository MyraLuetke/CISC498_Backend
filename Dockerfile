FROM python:3.7
ENV PYTHONUNBUFFERED=1
WORKDIR /src
COPY requirements.txt /src/
RUN pip install --upgrade pip 
RUN pip install -r requirements.txt
ADD . /src/
CMD python backend/manage.py runserver 0.0.0.0:8000
