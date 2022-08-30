FROM python:3

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt
RUN python -m pip install git+https://github.com/muepsilon/elasticemail-django@1dad468041bf0e4e9bf9ac8260fcbf95c8c58a22#egg=elasticemail_django

COPY . /usr/src/app/
