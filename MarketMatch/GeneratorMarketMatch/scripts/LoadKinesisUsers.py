import boto3
from random import randint
# import uuid
import json
# import datetime
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import logging
import time
import LoadKinesis
import GeneratorUtils


start_time = time.time()

def get_kinesis_record():
    """
    Generate an item with a random info such user_name, first name, surname, email, password etc.
    """
    
    dict_user_info = GeneratorUtils.random_user_generator(fname_path, surname_path)
    phone = GeneratorUtils.random_phone_generator()
    user_name = dict_user_info['user_name']
    password = user_name[:2] + str(randint(1000000, 5000000))
    cur_time = datetime.now()
    # setting cur_time to previous so update dates will be set with values till month ago
    # so bids and offers dates will be after
    cur_time_last_2months = cur_time - timedelta(days=60)
    # generate random timestamp along the last year
    previous_date = cur_time_last_2months - timedelta(days=randint(1, 365),
                                             hours=randint(1, 24),
                                             minutes=randint(1, 59),
                                             milliseconds=randint(1, 100))
    # generate user update date later then create date
    if randint(1, 10) % 9 == 0:                                                 
        updated_previous_date = previous_date + timedelta(days=randint(1, 2),
                                             hours=randint(1, 24),
                                             minutes=randint(1, 59),
                                             milliseconds=randint(1, 100))
    else:
        updated_previous_date = previous_date
        
    # set user contact information
    cust_contact = { "phone" : phone, 
                     "email" : dict_user_info['email'],
                     "address" : "address", 
                     "city" : "city"
                     }            
                    
    item = {
        'user_name'  : user_name,
        'entity_id'  : 'CUST#' + user_name,
        'timestamp'  : datetime.utcnow().isoformat(),
        'create_date': previous_date.isoformat(),
        'update_date': updated_previous_date.isoformat(),
        'fname'      : dict_user_info['fname'],
        'lname'      : dict_user_info['surname'],
        'cust_contact': cust_contact,
        'password'   : password
      } 
           
    raw_data = json.dumps(item)
    encoded_data = bytes(raw_data, 'utf-8')
    kinesis_record = {
        'Data': encoded_data,
        'PartitionKey': user_name,
    }
    
    return kinesis_record   
        
def load_users(stream_name, limit_batch_size, limit_total_users=1):
    """
    Loading total users according to given parameters
    """    
    logging.info(f'about to load {limit_total_users} in {limit_batch_size} batches')
    if limit_batch_size > limit_total_users:
        err_msg=f'limit_total_users {limit_total_users} must be greater than limit_total_users {limit_batch_size}'
        logging.error(err_msg)
        raise ValueError(err_msg)
            
    # generate users
    gen_users = LoadKinesis.KinesisLoader(stream_name, batch_size=limit_batch_size, maximum_records=limit_total_users)            
    gen_users.generate_and_submit(get_kinesis_record, 'user')
       

def main():
    
    # generate python log + timestamp
    log_file_path = str(log_dir_path) + r'/generator_users_log_' \
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

    # load new users to dynamodb
    # in case user_name + entity_id already exist will overide the item
    load_users(stream_name='stream_bids1_kinesis_dynamodb', limit_batch_size=1, limit_total_users=1)

   
if __name__ == "__main__":
    load_dotenv()
    log_dir_path = os.getenv("LOG_DIR_PATH")
    fname_path = os.getenv("FNAME_PATH")
    surname_path = os.getenv('SURNAME_PATH')    


    # calling main function
    main()

    diff_sec = time.time() - start_time
    diff_time = time.strftime("%H:%M:%S.%MS", time.gmtime(diff_sec))
    logging.info('\n')
    logging.info(f'--- total python duration: {diff_time} ---')


