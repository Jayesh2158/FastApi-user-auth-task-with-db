FROM python:3.8

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./movie_task ./movie_task

CMD ["uvicorn", "movie_task.main:app", "--host", "0.0.0.0", "--port", "80"]