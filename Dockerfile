FROM python:2.7

COPY . /app

WORKDIR /app/techtrends

RUN pip install -r requirements.txt

EXPOSE 3111

RUN python init_db.py

CMD [ "python", "app.py" ]