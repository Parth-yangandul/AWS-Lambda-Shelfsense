import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FoodItems')  # Match your table name

def lambda_handler(event, context):
    # Handle case where queryStringParameters might be None
    query_params = event.get('queryStringParameters') or {}
    user_id = query_params.get('user_id')
    
    if not user_id:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Missing user_id'})
        }
    
    try:
        response = table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(response.get('Items', []))
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Internal server error', 'message': str(e)})
        }