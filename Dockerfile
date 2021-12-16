FROM python:3.8

WORKDIR /movie_task

COPY ./requirements.txt /movie_task/requirements.txt

RUN pip install -r requirments.txt

EXPOSE 8000

CMD ["uvicorn", "src.main.app", "--host=0.0.0.0", "--reload"]


# # 
# FROM python:3.9

# # 
# WORKDIR /code

# # 
# COPY ./requirements.txt /code/requirements.txt

# # 
# RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# # 
# COPY ./app /code/app

# # 
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
