# import modules
import boto3
import datetime

# Generating a resources from the default session
dynamodb = boto3.resource('dynamodb')


def insert_data():
    """
    This function inserts data in dynamodb table
    Returns
    -------
    Dictionary
        Response Dictionary
    """

    table = dynamodb.Table('bids') 
    #with put_item function we insert data in Table
    response = table.put_item(
        Item = {
               'user_name': 'revm1',
               'entity_id': 'CUST#revm1',
               'create_date': datetime.datetime.utcnow().isoformat(),
               'update_date': datetime.datetime.utcnow().isoformat(),
               'status': 'open',               
               'fname':'rev',
               'lname':'mat',
               'cust_contact': {"phone":"+972521111222","email":"revm1@example.com","city":"tel - aviv","address":"hertzel 2"},
               'filter_categories': ["flights"]
               } 
        )
    return response
    
insert_data()