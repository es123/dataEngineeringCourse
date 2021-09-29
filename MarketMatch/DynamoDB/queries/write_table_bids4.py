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
               'entity_id': 'BID#200000005',
               'create_date': datetime.datetime.utcnow().isoformat(),
               'update_date': datetime.datetime.utcnow().isoformat(),
               'status': 'open',               
               'categoy': 'Flights',
               'bid_info': {"trip":"tlv-bgk","persons":"4","fromDate":"15.8","toDate":"21.8","target_price":"250"}
               }
             )
    return response
    
insert_data()