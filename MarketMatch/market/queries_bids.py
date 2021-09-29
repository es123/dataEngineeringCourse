# https://learn-to-code.workshop.aws/persisting_data/dynamodb/step-4.html

import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr






# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


TABLE_NAME = "bids"
# Creating the DynamoDB Client
dynamodb_client = boto3.client('dynamodb', region_name="us-east-2")
# Creating the DynamoDB Table Resource
dynamodb = boto3.resource('dynamodb', region_name="us-east-2")
table = dynamodb.Table(TABLE_NAME)

def scan_users(entity_id):
  TABLE_NAME = "bids"
  
  # Creating the DynamoDB Client
  dynamodb_client = boto3.client('dynamodb', region_name="us-east-2")
  
  # Creating the DynamoDB Table Resource
  dynamodb = boto3.resource('dynamodb', region_name="us-east-2")
  table = dynamodb.Table(TABLE_NAME)
  
  
  fe = Key("entity_id").begins_with(entity_id)
  pe = "#time, user_name, entity_id, update_date ,bid_info "
  # Expression Attribute Names for Projection Expression only.
  ean = {"#time": "timestamp"}
  esk = None
  
  
  response = table.scan(
      FilterExpression=fe,
      ProjectionExpression=pe,
      ExpressionAttributeNames=ean
      )
  
  for i in response['Items']:
      yield(json.dumps(i, cls=DecimalEncoder))

  while 'LastEvaluatedKey' in response:
      response = table.scan(
          ProjectionExpression=pe,
          FilterExpression=fe,
          ExpressionAttributeNames= ean,
          ExclusiveStartKey=response['LastEvaluatedKey']
          )
  
      for i in response['Items']:
          yield(json.dumps(i, cls=DecimalEncoder))
          
  
