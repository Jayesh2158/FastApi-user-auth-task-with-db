FROM python:3.8

WORKDIR /movie_task

COPY ./requirment.txt /movie_task/requirments.txt

RUN pip install -r requirments.txt

CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--reload"]