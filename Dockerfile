FROM python:3

WORKDIR /

COPY . ./Wueexam_logic
RUN pip install --upgrade pip
RUN pip install -r /Wueexam_logic/requirements_logic.txt

ENV PYTHONPATH /


WORKDIR /Wueexam_logic/logic

CMD ["python3","app.py"]
