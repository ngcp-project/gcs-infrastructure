FROM python:3.6

WORKDIR /usr/src/app

# COPY requirements.txt ./
RUN pip install digi-xbee

COPY . .

CMD ["python", "./xbeeReceive.py"]