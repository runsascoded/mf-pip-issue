FROM python:3.7
# These boto versions are mutually consistent (and relatively recent), but Metaflow will inadvertently upgrade botocore
# and boto3, but not aiobotocore, during environment-initialization (by running `pip install awscli`), breaking
# aiobotocore.
#
# This happens because of the `pip install awscli`: pip checks the most recent awscli first, sees that it can be
# installed but requires a more recent boto3, and installs that newer awscli+boto3 combo (along with a newer botocore
# required by the newer boto3). At that point, aiobotocore is broken.
ARG aiobotocore=1.4.2
ARG botocore=1.20.106
ARG boto3=1.17.106
RUN pip install \
    aiobotocore==${aiobotocore} \
    botocore==${botocore} \
    boto3==${boto3} \
    fsspec pandas s3fs
