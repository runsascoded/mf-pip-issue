FROM python:3.7
ARG aiobotocore=1.4.2
ARG botocore=1.20.106
ARG boto3=1.17.106
ARG metaflow=2.4.8
RUN pip install \
    aiobotocore==${aiobotocore} \
    botocore==${botocore} \
    boto3==${boto3} \
    fsspec \
    metaflow==${metaflow} \
    pandas \
    s3fs
RUN useradd -m user
USER user
ENV USER=user
WORKDIR /home/user
ADD s3_flow_test.py ./
ENTRYPOINT [ "python", "s3_flow_test.py" ]
CMD [ "run" ]
