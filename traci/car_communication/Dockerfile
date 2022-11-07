FROM python:3.9.12-alpine3.15

WORKDIR /app

COPY ./car_communication.py ./
COPY ./messaging.py ./
COPY ./requirements.txt ./

RUN pip install -r requirements.txt

CMD [ "python3", "car_communication.py" ]