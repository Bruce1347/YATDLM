FROM debian:buster

RUN apt update
RUN apt -y upgrade

RUN apt -y install python3 python3-pip libpq-dev

COPY requirements.txt /requirements.txt

RUN pip3 install -r /requirements.txt

COPY yatdlm /root/yatdlm

COPY docker-bootstrap.py /root/yatdlm/.

WORKDIR /root/yatdlm

RUN python3 /root/yatdlm/docker-bootstrap.py

CMD ["python3", "manage.py", "runserver"]