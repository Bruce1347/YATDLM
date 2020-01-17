FROM debian:buster

RUN apt update
RUN apt -y upgrade

RUN apt -y install python3 python3-pip libpq-dev

COPY requirements.txt /requirements.txt

RUN pip3 install -r /requirements.txt

COPY yatdlm /root/yatdlm

WORKDIR /root/yatdlm

CMD ["python3", "manage.py", "runserver"]