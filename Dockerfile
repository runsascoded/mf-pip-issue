FROM python:3.7
# These boto versions are mutually consistent, but Metaflow will inadvertently upgrade botocore and boto3, breaking
# aiobotocore, by running `pip install awscli boto3` during environment-initialization:
#
# `pip` starts checks the most recent awscli first, sees that it wants a more recent boto3, and installs that newer
# awscli+boto3 combo (along with a newer botocore required by the newer boto3). At that point, aiobotocore is broken.
ARG aiobotocore=1.4.2
ARG botocore=1.20.106
ARG boto3=1.17.106
ARG metaflow=2.4.8
RUN pip install \
    aiobotocore==${aiobotocore} \
    botocore==${botocore} \
    boto3==${boto3} \
    metaflow==${metaflow} \
    fsspec pandas s3fs
