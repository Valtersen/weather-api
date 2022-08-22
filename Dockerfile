FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /dj
COPY requirements.txt /dj/
RUN pip install -r requirements.txt
