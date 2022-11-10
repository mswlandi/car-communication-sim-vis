FROM python:3.9.12-alpine3.15

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./car_communication.py ./
COPY ./messaging.py ./

CMD [ "python3", "car_communication.py" ]