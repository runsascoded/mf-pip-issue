FROM python:3.7
ARG aiobotocore=1.4.2
ARG botocore=1.20.106
RUN pip install aiobotocore==${aiobotocore} botocore==${botocore} pandas
