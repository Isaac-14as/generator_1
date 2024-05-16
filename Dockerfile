FROM python:3.11.8

RUN mkdir /diploma

WORKDIR /diploma

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]