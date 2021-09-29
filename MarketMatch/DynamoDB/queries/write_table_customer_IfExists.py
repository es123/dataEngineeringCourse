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
               'user_name': 'erans112',
               'entity_id': 'CUST#erans112',
               'create_date': datetime.datetime.utcnow().isoformat(),
               'update_date': datetime.datetime.utcnow().isoformat(),
               'status': 'open'              
            #   'fname':'eran',
            #   'lname':'sar',
            #   'cust_contact': {"phone":"+972521111111","email":"erans1@example.com","city":"tel - aviv","address":"hertzel 1"},
            #   'filter_categories': ["flights","hotels"]
               },
        ConditionExpression ='attribute_not_exists(user_name)'
        )
    return response
    
try:
    conditionalUpdateResponse = insert_data()
    print("Added item")
except dynamodb.meta.client.exceptions.ConditionalCheckFailedException as e: 
    print(e)
    
