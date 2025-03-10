FROM python:3.10-alpine

LABEL org.opencontainers.image.title="DESH"
LABEL org.opencontainers.image.description="DESH: Data Engineering Staffing Helper - a tool to help staffing managers to find the right candidate for the right job."
LABEL org.opencontainers.image.authors="BBS Team"
LABEL org.opencontainers.image.vendor="Accenture"
LABEL org.opencontainers.image.source=https://github.com/lauryna-ramachandran-acc/gen-ai-sprint
LABEL org.opencontainers.image.url=https://github.com/lauryna-ramachandran-acc/gen-ai-sprint
LABEL org.opencontainers.image.licenses=Apache
LABEL maintainer="BBS Team <lauryna.ramachandran@accenture.com> (Lauryna Ramachandran) <yinan.li@accenture.com> (Yinan Li) <daniyal.ibrahim@accenture.com> (Daniyal Ibrahim) "
LABEL version="0.1.0"

ENV USER=desh

RUN apk update && apk add --no-cache \
    bash build-base dbus-x11 libffi-dev py3-pip python3 shadow \
    tcl tcl-dev tk tk-dev ttf-dejavu wget xfce4 xfce4-terminal \
    xorg-server xvfb unzip chromium chromium-chromedriver nss \
    freetype harfbuzz ca-certificates ttf-freefont

RUN mkdir -p /app/chrome/browser && \
    ln -s /usr/bin/chromium-browser /app/chrome/browser/chrome && \
    ln -s /usr/bin/chromedriver /app/chrome/chromedriver

RUN apk add --no-cache --virtual .build-deps gcc musl-dev && \
    pip install --upgrade pip && \
    pip install pipenv ttkbootstrap

WORKDIR /app

COPY . /app/
COPY ./Pipfile /app/Pipfile
COPY ./Pipfile.lock /app/Pipfile.lock

RUN adduser -D -s /bin/bash "$USER" && \
    chown -R "$USER":"$USER" /app

USER "$USER"

RUN pipenv install --deploy

CMD ["pipenv", "run", "python", "app.py"]
