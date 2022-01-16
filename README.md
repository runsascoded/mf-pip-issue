# Metaflow `pip install awscli` breaks `aiobotocore<2.1.0` in Batch

Docker image [runsascoded/mf-pip-issue-batch](https://hub.docker.com/repository/docker/runsascoded/mf-pip-issue-batch) ([`batch.dockerfile`](./batch.dockerfile)) pins recent versions of `botocore` and `aiobotocore`:
- [`aiobotocore==1.4.2`](https://pypi.org/project/aiobotocore/1.4.2/) (October 5, 2021)
- [`botocore==1.20.106`](https://pypi.org/project/botocore/1.20.106/) (July 6, 2021, [required by `aiobotocore==1.4.2`](https://github.com/aio-libs/aiobotocore/blob/1.4.2/setup.py#L10))
- [`boto3==1.17.106`](https://pypi.org/project/boto3/1.17.106/) (July 6, 2021; this is the boto3 version [compatible with `botocore==1.20.106`](https://github.com/boto/boto3/blob/1.17.106/setup.py#L17))

They work fine together normally; [runsascoded/mf-pip-issue-local](https://hub.docker.com/repository/docker/runsascoded/mf-pip-issue-local) ([`local.dockerfile`](./local.dockerfile))) runs [`s3_flow_test.py`](./s3_flow_test.py) successfully locally:
```bash
docker run -it --rm runsascoded/mf-pip-issue-local
# Metaflow 2.4.8 executing S3FlowTest for user:user
# …
# 2022-01-16 21:21:59.162 Done!
```

However, with a Metaflow Batch queue configured:
```bash
python s3_flow_test.py run --with batch:image=runsascoded/mf-pip-issue-batch
```
fails with:
```
AttributeError: 'AioClientCreator' object has no attribute '_register_lazy_block_unknown_fips_pseudo_regions'
```
due to a version mismatch (`botocore>=1.23.0`, `aiobotocore<2.1.0`). `botocore` removed `ClientCreator._register_lazy_block_unknown_fips_pseudo_regions` in `1.23.0`, and `aiobotocore` only updated to `botocore>=1.23.0` in `2.1.0`, so `aiobotocore<2.1.0` requires `botocore<1.23.0`, otherwise reading from S3 via Pandas will raise this error.

The version mismatch is caused by Metaflow [running `pip install awscli … boto3` while setting up the task environment](https://github.com/Netflix/metaflow/blob/2.4.8/metaflow/metaflow_environment.py#L85) ([in Batch](https://github.com/Netflix/metaflow/blob/2.4.8/metaflow/plugins/aws/batch/batch.py#L62) and [I believe k8s](https://github.com/Netflix/metaflow/blob/2.4.8/metaflow/metaflow_environment.py#L85)). `pip install awscli` can update `botocore` to `>=1.23.0` while `aiobotocore` is still `<2.1.0`.

A simpler version of this can be observed by running `pip install awscli` in the same image:
```bash
docker run --rm --entrypoint bash runsascoded/mf-pip-issue-batch -c '
  echo "Before \`pip install awscli\`:" && \
  pip list | grep boto && \
  pip install awscli -qqq && \
  echo -e "----\nAfter \`pip install awscli\`:" && \
  pip list | grep boto
' 2>/dev/null 
# Before `pip install awscli`:
# aiobotocore        1.4.2     # ✅
# boto3              1.17.106  # ✅
# botocore           1.20.106  # ✅
# ----
# After `pip install awscli`:
# aiobotocore        1.4.2     # ✅
# boto3              1.17.106  # ✅
# botocore           1.23.37   # ❌
```
A non-`--upgrade` `pip install` of `awscli` upg breaks `aiobotocore`
This example also breaks `boto3`'s botocore constraint, since `boto3` wasn't included in the `pip install` in this example. I don't know if `boto3` )

Config:
```
{
  "METAFLOW_BATCH_JOB_QUEUE": "arn:aws:batch:…",
  "METAFLOW_ECS_S3_ACCESS_IAM_ROLE": "arn:aws:iam::…",
  "METAFLOW_DEFAULT_DATASTORE": "s3",
  "METAFLOW_DATASTORE_SYSROOT_S3": "s3://<bucket>/metaflow",
  "METAFLOW_DATATOOLS_SYSROOT_S3": "s3://<bucket>/data"
}
```
