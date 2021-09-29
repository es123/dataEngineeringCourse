# todo: need to verify adding offers per bids - per customers logic

import time
import boto3
from random import randint
import json
import datetime
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import logging
import time
import queriesDynamoDB as qry
import ulid
import LoadKinesis
import GeneratorUtils


start_time = time.time()

def get_kinesis_record(dict_user):
    """
    Generate an item with a random hash key on a large range, and a unique sort key, and  a created date
    """
    # get user info
    dict_bid_info = dict_user
    user_name = dict_bid_info['user_name']
    entity_id = dict_bid_info['entity_id']
    bid_update_date = dict_bid_info['update_date']
    bid_update_date_converted = datetime.fromisoformat(bid_update_date)


    # get flights buisness info
    dict_buis_info = GeneratorUtils.random_buis_flight_generator(buis_flights_path) 
    b_flight = dict_buis_info['buis_flight']
    # generate random timestamp for offer created record on system
    offer_create_date = bid_update_date_converted + timedelta(days=randint(1, 10),
                                                 hours=randint(1, 24),
                                                 minutes=randint(1, 59),
                                                 milliseconds=randint(1, 100))
    offer_unique = ulid.new()
    offer_entity_id = 'OFFER#'+b_flight+'#'+str(offer_unique)

    item = {
      'user_name': user_name,
      'entity_id': offer_entity_id,
      'timestamp'  : datetime.utcnow().isoformat(),
      'create_date': offer_create_date.isoformat(),
      'update_date': offer_create_date.isoformat(),
      'bid': entity_id,
      'offer_user_name': b_flight,
      'contact_info': {"name":"best-flights", "phone":"777-232-999"},
      'offer_info': {"price":"370", "notes":"great deal - you shell thake it"}
      }
     
    raw_data = json.dumps(item)
    encoded_data = bytes(raw_data, 'utf-8')
    kinesis_record = {
        'Data': encoded_data,
        'PartitionKey': user_name,
    }

    return kinesis_record   

# def load_offers(b_flights_path, items_list, total_bids, total_offers):
def load_offers(stream_name, limit_batch_size, limit_total_users, limit_total_bids, limit_total_offers):
    # get list of all current users
    ls_items_bids = list(qry.scan_users("bids1", "BID#"))
    # get total users
    cur_total_bids = len(ls_items_bids)
    logging.info(f'total bids on system: {cur_total_bids}')
    
    
    # get total users
    # cur_total_bids = len(items_list)
    
    if cur_total_bids < limit_total_bids:
        logging.info(f'defined max bids to create offers for them {limit_total_bids} is less then current total bids {cur_total_bids} \
                     \n \t\t\t\t\t\t\t\t about to set max users to {cur_total_bids}')
        # set max users to create bids for them to be as current total users
        limit_total_bids = cur_total_bids 
        
    for i_bid, item in enumerate(ls_items_bids):
        # exit loop when reaching total_users 
        if i_bid > limit_total_bids:
            break

        logging.info(f'generating bid#{i_bid} out of {limit_total_bids}')
        # generate offers for existing users bids
        gen_offers = LoadKinesis.KinesisLoader(stream_name, batch_size=limit_batch_size, maximum_records=limit_total_offers)            
        gen_offers.generate_and_submit(get_kinesis_record, 'offers', json.loads(item))       

def main():
    
    # load env. variables
    load_dotenv()
    log_dir_path = os.getenv("LOG_DIR_PATH")
    
    # generate python log + timestamp
    log_file_path = str(log_dir_path) + r'/generato_bids_log_' \
                    + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.txt'

    # set up logging to file
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s.%(msecs)03d %(name)-12s %(module)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=log_file_path,
                        filemode='w'
                        )

    # define a console Handler which writes messages to the sys.stderr
    console = logging.StreamHandler()
    # set console handler level
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s %(name)-12s: %(module)s %(levelname)-8s %(message)s')
    # define miliseconds format
    formatter.default_msec_format = '%s.%03d'
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    logging.info(f'logging to : {log_file_path}')
    logging.info('\n')

    load_offers(stream_name='stream_bids1_kinesis_dynamodb', limit_batch_size=1, limit_total_users=1, limit_total_bids=2, limit_total_offers=2)


if __name__ == "__main__":
    
    # load env. variables
    load_dotenv()
    log_dir_path = os.getenv("LOG_DIR_PATH")
    buis_flights_path = os.getenv('BUIS_FLIGHTS_PATH')

    # calling main function
    main()

    diff_sec = time.time() - start_time
    diff_time = time.strftime("%H:%M:%S.%f", time.gmtime(diff_sec))
    logging.info('\n')
    logging.info(f'--- total python duration: {diff_time} ---')


