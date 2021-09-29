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

start_time = time.time()

def get_kinesis_record(dict_user):
    """
    Generate an item with a random hash key on a large range, and a unique sort key, and  a created date
    """
    
    # get user info
    dict_user_info = dict_user
    user_name = dict_user_info['user_name']
    user_update_date = dict_user_info['update_date']
    user_update_date_converted = datetime.fromisoformat(user_update_date)
    
    # generate random timestamp user created on system
    bid_create_date = user_update_date_converted + timedelta(days=randint(1, 10),
                                                 hours=randint(1, 24),
                                                 minutes=randint(1, 59),
                                                 milliseconds=randint(1, 100))
    # bid_update_date = bid_create_date
    bid_unique = ulid.new()
    bid_entity_id = 'BID#'+str(bid_unique)
    
    item = {
      'user_name': user_name,
      'entity_id': bid_entity_id,
      'timestamp'  : datetime.utcnow().isoformat(),
      'create_date': bid_create_date.isoformat(),
      'update_date': bid_create_date.isoformat(),
      'status': 'open',               
      'category': 'flights',
      'bid_info': {"origin":"tel-aviv", "destination":"bkk","from_date":"15.8","to_date":"21.8","adults":"2","children":"3","target_price":"400"}
      }
     
    raw_data = json.dumps(item)
    encoded_data = bytes(raw_data, 'utf-8')
    kinesis_record = {
        'Data': encoded_data,
        'PartitionKey': user_name,
    }

    return kinesis_record   

def load_bids(stream_name, limit_batch_size, limit_total_users, limit_total_bids):
    # get list of all current users
    ls_items_users = list(qry.scan_users("bids1", "CUST#"))
    # get current total of users on the system
    cur_total_users = len(ls_items_users)
    logging.info(f'current total users on system: {cur_total_users}') 
    

    if cur_total_users < limit_total_users:
        logging.info(f'defined max users to create bids for them {limit_total_users} is less then current total users {cur_total_users} \
                  \n \t\t\t\t\t\t\t\t about to set max users to {cur_total_users}')
        # set max users to create bids for them to be as current total users
        limit_total_users = cur_total_users 
        logging.info(f'limit_total_users: {limit_total_users}')
    
    for i_user, item in enumerate(ls_items_users):
        print('i_user:', i_user) 
        print('limit_total_users:', limit_total_users) 
        if i_user > limit_total_users:
            logging.info(f'total of {limit_total_users} user/s for creating bids been reached')
            break

        logging.info(f'generating bid#{limit_total_bids} for user#{i_user}')
        # generate bids for existing users
        gen_bids = LoadKinesis.KinesisLoader(stream_name, batch_size=limit_batch_size, maximum_records=limit_total_bids)            
        gen_bids.generate_and_submit(get_kinesis_record, 'bids', json.loads(item))

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

    logging.info(f'logging to: {log_file_path}')
    logging.info('\n')
    
    # load users
    load_bids(stream_name='stream_bids1_kinesis_dynamodb', limit_batch_size=1, limit_total_users=3, limit_total_bids=2)
    

if __name__ == "__main__":

    # calling main function
    main()

    diff_sec = time.time() - start_time
    diff_time = time.strftime("%H:%M:%S.%f", time.gmtime(diff_sec))
    logging.info('\n')
    logging.info(f'--- total python duration: {diff_time} ---')


