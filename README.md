# Metaflow/`pip`/Batch issue
Metaflow runs `pip install awscli … boto3` [while setting up task environements in Batch](https://github.com/Netflix/metaflow/blob/2.4.8/metaflow/metaflow_environment.py#L85), which can break `aiobotocore<2.1.0`.

## Repro
Docker image [runsascoded/mf-pip-issue-batch](https://hub.docker.com/repository/docker/runsascoded/mf-pip-issue-batch) ([`batch.dockerfile`](./batch.dockerfile)) pins recent versions of `botocore` and `aiobotocore`:
- [`aiobotocore==1.4.2`](https://pypi.org/project/aiobotocore/1.4.2/) (October 5, 2021)
- [`botocore==1.20.106`](https://pypi.org/project/botocore/1.20.106/) (July 6, 2021, [required by `aiobotocore==1.4.2`](https://github.com/aio-libs/aiobotocore/blob/1.4.2/setup.py#L10))

### Local mode: ✅
They work fine together normally; [runsascoded/mf-pip-issue-local](https://hub.docker.com/repository/docker/runsascoded/mf-pip-issue-local) ([`local.dockerfile`](./local.dockerfile)) runs [`s3_flow_test.py`](./s3_flow_test.py) successfully (in "local" mode):
```bash
docker run -it --rm runsascoded/mf-pip-issue-local
# Metaflow 2.4.8 executing S3FlowTest for user:user
# …
# 2022-01-16 21:21:59.162 Done!
```

### Batch mode: ❌
However, with a Metaflow Batch queue configured:
```bash
python s3_flow_test.py run --with batch:image=runsascoded/mf-pip-issue-batch
```
fails with:
```
AttributeError: 'AioClientCreator' object has no attribute '_register_lazy_block_unknown_fips_pseudo_regions'
```
due to a version mismatch (`botocore>=1.23.0`, `aiobotocore<2.1.0`).

### Version mismatch
`botocore` removed `ClientCreator._register_lazy_block_unknown_fips_pseudo_regions` in `1.23.0`, and `aiobotocore` only updated to `botocore>=1.23.0` in `2.1.0`, so `aiobotocore<2.1.0` requires `botocore<1.23.0`, otherwise reading from S3 via Pandas will raise this error.

### Cause
The version mismatch is caused by Metaflow [running `pip install awscli … boto3` while setting up the task environment](https://github.com/Netflix/metaflow/blob/2.4.8/metaflow/metaflow_environment.py#L85) ([in Batch](https://github.com/Netflix/metaflow/blob/2.4.8/metaflow/plugins/aws/batch/batch.py#L62) and [I believe k8s](https://github.com/Netflix/metaflow/blob/2.4.8/metaflow/metaflow_environment.py#L85)). If `awscli` or `boto3` aren't both installed already, it will pick a recent version to install, see that a recent `botocore` is also required by that version, and update `botocore` to `>=1.23.0` while `aiobotocore` is still `<2.1.0`, breaking Pandas→S3 reading.

### Simpler example
Here we see `pip install awscli` break `aiobotocore<2.1.0` directly (in the same image as above):
```bash
docker run --rm --entrypoint bash runsascoded/mf-pip-issue-batch -c '
  echo "Before \`pip install awscli\`:" && \
  pip list | grep botocore && \
  pip install awscli -qqq && \
  echo -e "----\nAfter \`pip install awscli\`:" && \
  pip list | grep botocore
' 2>/dev/null 
# Before `pip install awscli`:
# aiobotocore        1.4.2     # ✅
# botocore           1.20.106  # ✅
# ----
# After `pip install awscli`:
# aiobotocore        1.4.2     # ✅
# botocore           1.23.37   # ❌
```

`pip install awscli` upgraded `botocore` to a version that's incompatible with the already-installed `aiobotocore`.

## Workaround
The simplest workaround I've found is to ensure Metaflow's `pip install awscli click requests boto3` command no-ops, by having *some version* of those libraries already installed. They should also have consistent transitive dependency versions, otherwise `pip install` will "help" with those as well). 

## Scratch
These seem like the minimal Metaflow configs to submit to Batch (and reproduce the issue):
```
{
  "METAFLOW_BATCH_JOB_QUEUE": "arn:aws:batch:…",
  "METAFLOW_ECS_S3_ACCESS_IAM_ROLE": "arn:aws:iam::…",
  "METAFLOW_DEFAULT_DATASTORE": "s3",
  "METAFLOW_DATASTORE_SYSROOT_S3": "s3://<bucket>/metaflow",
  "METAFLOW_DATATOOLS_SYSROOT_S3": "s3://<bucket>/data"
}
```

Docker build commands:
```bash
docker build -f batch.dockerfile -t runsascoded/mf-pip-issue-batch .
docker build -f local.dockerfile -t runsascoded/mf-pip-issue-local .
```
