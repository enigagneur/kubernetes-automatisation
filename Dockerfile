FROM python:latest
ADD . /code
WORKDIR /code
ENV ACCESS_KEY=
ENV SECRET_KEY=
ENV REGION=
RUN pip install -r requirements.txt
CMD ["python3", "kubernetes.py"]
