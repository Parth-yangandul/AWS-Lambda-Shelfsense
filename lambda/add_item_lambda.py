import json
import boto3
import uuid
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FoodItems')

def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))

    user_id = body.get('user_id')
    item_name = body.get('item_name')
    expiry_date = body.get('expiry_date')
    quantity = body.get('quantity', '')

    if not all([user_id, item_name, expiry_date]):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing required fields'})
        }

    item_id = str(uuid.uuid4())

    table.put_item(Item={
        'user_id': user_id,
        'item_id': item_id,
        'item_name': item_name,
        'expiry_date': expiry_date,
        'quantity': quantity,
        'added_on': datetime.now(timezone.utc).date().isoformat()
    })

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Item added', 'item_id': item_id})
    }
