FROM python:3.12.4-slim

WORKDIR /code

COPY ./requirements.txt ./

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./sources /code/sources

CMD ["python", "sources/main.py"]
