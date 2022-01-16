from metaflow import FlowSpec, step, conda
import pandas as pd

class CondaFlowTest(FlowSpec):
    @conda(libraries={'aiobotocore': '1.4.2'})
    @step
    def start(self):
        import aiobotocore
        print('aiobotocore %s: %s, %s' % (aiobotocore.__version__, aiobotocore.__file__, getattr(aiobotocore.client.AioClientCreator, '_register_lazy_block_unknown_fips_pseudo_regions', None)))
        import botocore
        print('botocore %s: %s, %s' % (botocore.__version__, botocore.__file__, getattr(botocore.client.ClientCreator, '_register_lazy_block_unknown_fips_pseudo_regions', None)))
        url = 's3://rac-test-bkt/test.csv'
        print(f'Reading from {url}…')
        self.df = pd.read_csv(url)
        self.next(self.end)
    @step
    def end(self):
        print(f'Found {len(self.df)} records')

if __name__ == '__main__':
    CondaFlowTest()
