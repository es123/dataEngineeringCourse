import time
import boto3
from random import randint
import uuid
import json
import datetime
from datetime import datetime, timedelta
import os
import logging
import time


start_time = time.time()


class KinesisLoader:
    """
    Send events to data stream
    """
    def __init__(self, stream_name, batch_size=500, maximum_records=None):
        """
        The default batch_size here is to match the maximum allowed by Kinesis in a PutRecords request
        
        @stream_name: kinesis related data stream
        @batch_size: total batches to run, used to supprt adding more records then the limit but thrugh multiple batches
        @maximum_records: max records to generate each batch in order to avoid aws limition
        """
        self.stream_name = stream_name
        # self.fname_path = fname_path
        # self.surname_path = surname_path
        self.batch_size = min(batch_size, 500)
        self.maximum_records = maximum_records
        self.kinesis_client = boto3.session.Session().client('kinesis')

        
    def generate_and_submit(self, get_kinesis_record, entity=None, user_info=None):
        self.get_kinesis_record = get_kinesis_record
        self.entity = entity
        self.user_info = user_info
        counter = 0
        
        logging.info('starting generate_and_submit')
        logging.info('counter: ' + str(counter))
        logging.info('self.maximum_records: ' + str(self.maximum_records))
        logging.info('self.batch_size: ' + str(self.batch_size))
        
        # simple cutoff here - guaranteed to not send in more than maximum_records, with single batch granularity
        while counter < self.maximum_records and counter <= (self.maximum_records - self.batch_size):
            # in case loading items other than users we pass the fuction get_kinesis_record user information through user_info parameter 
            if entity == 'user':
                records_batch = [self.get_kinesis_record() for item in range(0, self.batch_size)]
            else:
                records_batch = [self.get_kinesis_record(self.user_info) for item in range(0, self.batch_size)]
            print('records_batch:', records_batch)
            request = {
                'Records': records_batch,
                'StreamName': self.stream_name
            }

            response = self.kinesis_client.put_records(**request)
            self.submit_batch_until_successful(records_batch, response)

            counter += len(records_batch)
            logging.info('Batch inserted. Total records: {}'.format(str(counter)))

        return
    

    def submit_batch_until_successful(self, batch, response):
        """ If needed, retry a batch of records, backing off exponentially until it goes through"""
        retry_interval = 0.5

        failed_record_count = response['FailedRecordCount']
        while failed_record_count:
            time.sleep(retry_interval)

            # Failed records don't contain the original contents - we have to correlate with the input by position
            failed_records = [batch[i] for i, record in enumerate(response['Records']) if 'ErrorCode' in record]

            logging.info('Incrementing exponential back off and retrying {} failed records'.format(str(len(failed_records))))
            retry_interval = min(retry_interval * 2, 10)
            request = {
                'Records': failed_records,
                'StreamName': self.stream_name
            }

            result = self.kinesis_client.put_records(**request)
            failed_record_count = result['FailedRecordCount']
            
