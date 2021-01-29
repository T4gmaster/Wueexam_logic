FROM python:3.10-rc-buster

WORKDIR /


COPY . ./backend
RUN pip install -r backend/requirements_logic.txt

ENV PYTHONPATH /


WORKDIR /backend/logic



CMD ["python3","app.py"]
