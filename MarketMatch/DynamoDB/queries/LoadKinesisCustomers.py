import time
import boto3
import random
import uuid
import datetime
import json


class KinesisLoader:
    def __init__(self, batch_size=500, maximum_records=None): #org
        """
        The default batch_size here is to match the maximum allowed by Kinesis in a PutRecords request
        """
        self.batch_size = min(batch_size, 500)
        self.maximum_records = maximum_records
        self.kinesis_client = boto3.session.Session().client('kinesis')

    def generate_and_submit(self):
        counter = 0
        
        print('starting generate_and_submit')
        print('counter:',counter)
        print('self.maximum_records:', self.maximum_records)
        print('self.batch_size:', self.batch_size)
        
        # Simple cutoff here - guaranteed to not send in more than maximum_records, with single batch granularity
        while counter < self.maximum_records and counter <= (self.maximum_records - self.batch_size):
            records_batch = [self.get_kinesis_record() for _ in range(0, self.batch_size)]
            print('records_batch:', records_batch)
            request = {
                'Records': records_batch,
                'StreamName': 'stream_bids_kinesis_dynamodb'
            }

            response = self.kinesis_client.put_records(**request)
            self.submit_batch_until_successful(records_batch, response)

            counter += len(records_batch)
            print('Batch inserted. Total records: {}'.format(str(counter)))

        return

    def submit_batch_until_successful(self, batch, response):
        """ If needed, retry a batch of records, backing off exponentially until it goes through"""
        retry_interval = 0.5

        failed_record_count = response['FailedRecordCount']
        while failed_record_count:
            time.sleep(retry_interval)

            # Failed records don't contain the original contents - we have to correlate with the input by position
            failed_records = [batch[i] for i, record in enumerate(response['Records']) if 'ErrorCode' in record]

            print('Incrementing exponential back off and retrying {} failed records'.format(str(len(failed_records))))
            retry_interval = min(retry_interval * 2, 10)
            request = {
                'Records': failed_records,
                'StreamName': 'stream_bids_kinesis_dynamodb'
            }

            result = self.kinesis_client.put_records(**request)
            failed_record_count = result['FailedRecordCount']
            
    @staticmethod
    def get_kinesis_record():
        """
        Generate an item with a random hash key on a large range, and a unique sort key, and  a created date
        """
        # item = {'hashKey': random.randrange(0, 5000000), 'sortKey': str(uuid.uuid4()), 'created': datetime.datetime.utcnow().isoformat()}
        cust_id = random.randrange(1000000, 5000000)
        user_name = 'TestUser#'+str(cust_id)
        
        
        item = {
            'user_name': user_name,
            'entity_id': 'CUST#' + user_name
            # 'create_date': datetime.datetime.utcnow().isoformat(),
            # 'update_date': datetime.datetime.utcnow().isoformat()
            # 'status': 'open',               
            # 'fname':'Aastha',
            # 'lname':'Rodriguez',
            # 'phone': '+972521111777',
            # 'email': 'aaa@gmail.com'
           } 
               
        raw_data = json.dumps(item)
        encoded_data = bytes(raw_data, 'utf-8')
        kinesis_record = {
            'Data': encoded_data,
            'PartitionKey': user_name,
        }
    
        return kinesis_record            
            
testLoad = KinesisLoader(batch_size = 1, maximum_records = 2)            
testLoad.generate_and_submit()