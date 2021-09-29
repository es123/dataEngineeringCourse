import time
import boto3
import random
import uuid
import datetime
import json


kinesis_client = boto3.session.Session().client('kinesis')

item = {
       'trip': 'NEW YORK1',
       'entity_id': 'DEST#Bangkok',

        } 
        
raw_data = json.dumps(item)
encoded_data = bytes(raw_data, 'utf-8')
kinesis_record = {
    'Data': encoded_data,
    'PartitionKey': item['trip'],
}


kinesis_record_list = []
kinesis_record_list.append(kinesis_record)
print(kinesis_record_list)

request = {
            'Records': kinesis_record_list,
            'StreamName': 'stream_r2rTrips_generator_kinesis_dynamodb'
        }
        
print(request)


kinesis_client.put_records(**request)