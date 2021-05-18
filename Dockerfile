FROM python:3.8.2

WORKDIR /

COPY . ./Wueexam_logic
RUN pip install --upgrade pip
RUN pip install -r /Wueexam_logic/requirements_logic.txt

ENV PYTHONPATH /
ENV PYTHONUNBUFFERED=1

WORKDIR /Wueexam_logic/logic

CMD ["python3","-u","app.py"]
