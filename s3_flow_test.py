from metaflow import FlowSpec, step
import pandas as pd

class S3FlowTest(FlowSpec):
    '''Simple flow reading from S3 using pd.read_csv (which uses aiobotocore->botocore)

    `metaflow_environment.get_package_commands` includes a `pip install awscli …` that can trigger an upgrade of
    `botocore` but not `aiobotocore`, causing `pd.read_csv("s3://…")` to crash if `aiobotocore<2.1.0`.

    botocore>=1.23.0 (2021-11-08) removed a method (`ClientCreator._register_lazy_block_unknown_fips_pseudo_regions`).
    Versions of aiobotocore<2.1.0 pinned earlier versions of `botocore`, and use that method (via the `AioClientCreator`
    subclass), but when Metaflow's setup code triggers an upgrade for botocore, but not aiobotocore, that breaks earlier
    versions of aiobotocore (<2.1.0).
    '''
    @step
    def start(self):
        # Print aiobotocore, botocore versions, files, and check for method that was removed in botocore>=1.23.0:
        import aiobotocore
        print('aiobotocore %s: %s, %s' % (aiobotocore.__version__, aiobotocore.__file__, getattr(aiobotocore.client.AioClientCreator, '_register_lazy_block_unknown_fips_pseudo_regions', None)))
        import botocore
        print('botocore %s: %s, %s' % (botocore.__version__, botocore.__file__, getattr(botocore.client.ClientCreator, '_register_lazy_block_unknown_fips_pseudo_regions', None)))
        url = 's3://rac-test-bkt/test.csv'
        print(f'Reading from {url}…')
        # This crashes when aiobotocore is "old" and botocore has been updated by Metaflow's env-setup logic
        self.df = pd.read_csv(url)
        self.next(self.end)
    @step
    def end(self):
        print(f'Found {len(self.df)} records')

if __name__ == '__main__':
    S3FlowTest()
