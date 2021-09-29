import time
import boto3
import random
import uuid
import datetime
import json


kinesis_client = boto3.session.Session().client('kinesis')

item = {
           'user_name': 'dan1',
           'entity_id': 'OFFER#900000007',
           'create_date': datetime.datetime.utcnow().isoformat(),
           'update_date': datetime.datetime.utcnow().isoformat(),
           'status': 'open',
           'bid': 'BID#200000002',
           'offer_info': {"trip":"tlv-bgk", "persons":"4", "fromDate":"15.8", "toDate":"20.8", "airline": "Arkia", "stop":"0", "price":"350"}
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


kinesis_client.put_records(**request)