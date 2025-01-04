FROM python:3.13

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN python source/manage.py migrate

CMD ["python","source/manage.py","runserver","0.0.0.0:8000"]
