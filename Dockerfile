FROM python:3

WORKDIR /


COPY . ./wueexam_logic
RUN pip install --upgrade pip
RUN pip install -r /wueexam_logic/requirements_logic.txt

ENV PYTHONPATH /


WORKDIR /wueexam_logic/logic



CMD ["python3","app.py"]
