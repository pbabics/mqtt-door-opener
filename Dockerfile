FROM resin/raspberry-pi-alpine-python:3.6.1

RUN mkdir -p /usr/src/app

COPY requirements.txt /usr/src/app
RUN pip install -r /usr/src/app/requirements.txt

COPY . /usr/src/app

ENV MQTT_SERVER "mqtt://localhost:1883/"

EXPOSE 8080
CMD ["python3", "/usr/src/app/__main__.py"]
