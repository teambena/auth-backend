FROM python:3.8

WORKDIR /app

COPY requirements.txt .

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py

RUN pip install -r requirements.txt
RUN pip install SQLAlchemy==1.4
COPY . .

EXPOSE 8060

CMD ["python", "run.py"]