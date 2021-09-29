import time
import boto3
import random
import uuid
import datetime
import json


kinesis_client = boto3.session.Session().client('kinesis')

item = {
       'user_name': 'aaa6',
       'entity_id': 'BID#200000006',
       'create_date': datetime.datetime.utcnow().isoformat(),
       'update_date': datetime.datetime.utcnow().isoformat(),
       'status': 'open',               
       'categoy': 'Flights',
       'bid_info': {"trip":"tlv-bgk","persons":"4","fromDate":"14.8","toDate":"20.8","target_price":"399"}
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