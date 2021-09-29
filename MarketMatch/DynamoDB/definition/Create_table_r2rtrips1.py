import boto3


def create_dynamodb_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.create_table(
        TableName='r2rtrips1',
        KeySchema=[
            {
                'AttributeName': 'origin',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'entity_id ',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'origin',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'entity_id ',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    return table


if __name__ == '__main__':
    r2rtrips1 = create_dynamodb_table()
    print("Table status:", r2rtrips1.table_status)