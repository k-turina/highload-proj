FROM python:3

RUN mkdir -p /app/
WORKDIR /app/

COPY requirements.txt ./
COPY /highload-front/. ./
RUN pip install -r requirements.txt

CMD ["python", "-u" ,"./front.py"]
