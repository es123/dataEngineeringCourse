# https://www.fernandomc.com/posts/ten-examples-of-getting-data-from-dynamodb-with-python-and-boto3/

import boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = "bids"

# Creating the DynamoDB Client
dynamodb_client = boto3.client('dynamodb', region_name="us-east-2")

# Creating the DynamoDB Table Resource
dynamodb = boto3.resource('dynamodb', region_name="us-east-2")
table = dynamodb.Table(TABLE_NAME)

###############################################################################################
# Use the DynamoDB Table resource get item method to get a single item
# for specific PK and entity_id

pk = 'Anda786CostelaGEN'
entity_id = 'CUST#Anda786CostelaGEN'

response = table.get_item(
    Key={
        'user_name': pk,
        'entity_id': entity_id
    }
)

output = response['Item']

print(f'display specific item for pk {pk} and entity_id {entity_id} : \n {output}')
print('~' * 150)
######################################################################


###############################################################################################
# Use the Table resource to query for all items by user_name value
pk = 'Anda786CostelaGEN'

response = table.query(
  KeyConditionExpression=Key('user_name').eq(pk)
)

output = response['Items']

print(f'display all items for pk {pk} : \n {output}')
print('~' * 150)
###############################################################################################


############################ Get all Customer BIDS ##########################################
# Use the Table resource to query all entity_id Items by specific Customer
# that start with 'BID#'
pk = 'Anda786CostelaGEN'
entity_id_begin = 'BID#'

response = table.query(
  KeyConditionExpression=Key('user_name').eq(pk) & Key('entity_id').begins_with(entity_id_begin)
)

output = response['Items']

print(f'display all items for pk {pk} where entity_id begins with {entity_id_begin}:')
for i, bid in enumerate(output):
    print(f'{i+1}: {bid}')
print('~' * 150)
###############################################################################################

############################ Get all Customer OFFERS ##########################################
# Use the Table resource to query all entity_id Items by specific Customer
# that start with 'OFFER#'
pk = 'Anda786CostelaGEN'
entity_id_begin = 'OFFER#'

response = table.query(
  KeyConditionExpression=Key('user_name').eq(pk) & Key('entity_id').begins_with(entity_id_begin)
)

output = response['Items']

print(f'display all items for pk {pk} where entity_id begins with {entity_id_begin}:')
for i, bid in enumerate(output):
    print(f'{i+1}: {bid}')
print('~' * 150)
###############################################################################################


