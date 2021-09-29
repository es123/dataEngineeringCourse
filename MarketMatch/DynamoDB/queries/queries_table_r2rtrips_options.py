# https://www.fernandomc.com/posts/ten-examples-of-getting-data-from-dynamodb-with-python-and-boto3/

import boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = "r2rTrips"

# Creating the DynamoDB Client
dynamodb_client = boto3.client('dynamodb', region_name="us-east-2")

# Creating the DynamoDB Table Resource
dynamodb = boto3.resource('dynamodb', region_name="us-east-2")
table = dynamodb.Table(TABLE_NAME)


############################ Get all Customer BIDS ##########################################
# Use the Table resource to query all entity_id Items by specific Customer
# that start with 'BID#'
pk = 'Delhi_Mumbai'
entity_id_begin = 'OPTION#'
limit_options = 1

limit_options = limit_options - 1

response = table.query(
  KeyConditionExpression=Key('trip').eq(pk) & Key('entity_id').begins_with(entity_id_begin)
)

output = response['Items']

print(f'display all items for pk {pk} where entity_id begins with {entity_id_begin}:')
for i, record in enumerate(output):
    if i > limit_options:
      break
    print(f'option#{i+1}')
    for attribute in record["info"]:
      print(f'attributesn#{i+1}')
      if attribute != 'transits':
        print(attribute, ':', record["info"][attribute])
      else:
        print(f'transits')
        for transit_id in record["info"][attribute]:
           # print(transit, ':', record["info"][attribute][transit])
          print('transit_id#'+transit_id)
          for key, transit_attribute in record["info"][attribute][transit_id].items():
            print('\t', key, ':', transit_attribute)
            
            

      
print('~' * 150)
###############################################################################################
