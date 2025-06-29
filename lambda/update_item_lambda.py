import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FoodItems')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        user_id = body['user_id']
        item_id = body['item_id']

        update_expr = []
        expr_attr_vals = {}

        if 'item_name' in body:
            update_expr.append("item_name = :name")
            expr_attr_vals[":name"] = body['item_name']
        if 'expiry_date' in body:
            update_expr.append("expiry_date = :expiry")
            expr_attr_vals[":expiry"] = body['expiry_date']
        if 'quantity' in body:
            update_expr.append("quantity = :qty")
            expr_attr_vals[":qty"] = body['quantity']

        if not update_expr:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'No fields to update'})
            }

        update_expression = "SET " + ", ".join(update_expr)

        table.update_item(
            Key={'user_id': user_id, 'item_id': item_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expr_attr_vals
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Item updated successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error updating item', 'error': str(e)})
        }
