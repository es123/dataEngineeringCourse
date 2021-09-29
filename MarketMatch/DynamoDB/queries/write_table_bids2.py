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
               'user_name': 'erans1',
               'entity_id': 'BID#200000002',
               'create_date': datetime.datetime.utcnow().isoformat(),
               'update_date': datetime.datetime.utcnow().isoformat(),
               'status': 'open',               
               'categoy': 'Hotels',
               'bid_info': {"country": "Israel", "town": "Eilat", "persons":"2", "FromDate" : "15.8.2021", "ToDate": "19.8.2021", "target_price": "275"}
               }
             )
    return response
    
insert_data()