import time
import boto3
import random
import uuid
import datetime
import json
import logging
from decimal import Decimal


kinesis_client = boto3.session.Session().client('kinesis')

def send_event(table, data_stream, pk, sk, item, debug=0):
    """
    
    This function sends data event to Kinesis data stream
    """
    
    if debug == 1:
        logging.info(f'table: {table}')
        logging.info(f'data_stream: {data_stream}')
        logging.info(f'pk: {pk}')
        logging.info(f'sk: {sk}')
    
    item_decimal = json.loads(json.dumps(item), parse_float=Decimal)

    def default_json(t):
        """
        "convert json elements to string in order to handle Float attributes which DynamoDB is not supported
        """
        return f'{t}'
    
           
    raw_data = json.dumps(item_decimal, default=default_json)
    # raw_data = json.dumps(item)
    encoded_data = bytes(raw_data, 'utf-8')
    kinesis_record = {
                       'Data': encoded_data,
                       'PartitionKey': item_decimal[pk]
                     }
    
    
    kinesis_record_list = []
    kinesis_record_list.append(kinesis_record)

    request = {
                'Records': kinesis_record_list,
                'StreamName': data_stream      
              }
    if debug == 1:
        logging.info(f'request sent to data_stream: {request}')

    
    kinesis_client.put_records(**request)
    
# table = 'r2rtrips1'
table = 'r2rTripsGenerator'
# stream = 'stream_r2rTrips1_kinesis_dynamodb'
stream = 'stream_r2rTrips_generator_kinesis_dynamodb'
# pk = 'origin'    
pk = 'trip' 
sk = 'entity_id'
item = {
        pk: 'stream_r2rTrips2',
        sk: 'TRIP#testStream15',
        'create_date': datetime.datetime.utcnow().isoformat(),
        'update_date': datetime.datetime.utcnow().isoformat(),
        'info': {"cat": "transit", "name": "train", "type": "purple", "duration": 480}
        # 'info': {"cat": "transit", "name": "train", "type": "purple", "duration": 480, "max_price": 33.78, "min_price": 3.784025, "org_cat": "station", "org_name": "Tokyo", "org_lat": 35.6813, "org_lng": 139.767, "dest_cat": "station", "dest_name": "Ueno", "dest_lat": 35.71351, "dest_lng": 139.7768},
        }
    
# send_event(table, stream, pk, sk, item, debug=1)    
