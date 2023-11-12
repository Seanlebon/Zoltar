FROM python:3.11.6-slim-bullseye 

WORKDIR /Zoltar

RUN python -m venv /opt/venv

ENV PATH="opt/venv/bin/:$PATH"

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "main.py"]