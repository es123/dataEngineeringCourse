import time
import boto3
import random
import uuid
import datetime
import json


kinesis_client = boto3.session.Session().client('kinesis')

item = {
       'user_name': 'testEran',
       'entity_id': 'CUST#Eran',
       'create_date': datetime.datetime.utcnow().isoformat(),
       'update_date': datetime.datetime.utcnow().isoformat(),
       'status': 'open',               
       'fname':'TestEvent',
       'lname':'TestEvent',
       'cust_contact': {"phone":"+972521111555","email":"dan1@example.com","city":"tel - aviv","address":"hertzel 7"},
       'filter_categories': ["flights","hotels", "zimmers"]
        } 
        
raw_data = json.dumps(item)
encoded_data = bytes(raw_data, 'utf-8')
kinesis_record = {
    'Data': encoded_data,
    'PartitionKey': item['user_name'],
}


kinesis_record_list = []
kinesis_record_list.append(kinesis_record)
print(kinesis_record_list)

request = {
            'Records': kinesis_record_list,
            'StreamName': 'stream_bids_kinesis_dynamodb'
        }
        
print(request)


kinesis_client.put_records(**request)