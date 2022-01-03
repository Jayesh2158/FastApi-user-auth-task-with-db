FROM python:3.8

WORKDIR /movie_task

COPY ./requirements.txt /movie_task/requirements.txt

RUN pip install -r requirments.txt

CMD ["uvicorn", "movie_task.main.app", "--reload"]

