import boto3
import os
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
table = dynamodb.Table('FoodItems')

SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
SPOONACULAR_API_KEY = os.environ['SPOONACULAR_API_KEY']

def lambda_handler(event, context):
    today = datetime.now(timezone.utc).date()
    threshold = today + timedelta(days=2)

    response = table.scan()
    near_expiry_items = []
    deleted_items = []

    for item in response.get('Items', []):
        expiry_str = item.get('expiry_date')
        if not expiry_str:
            continue

        expiry = datetime.strptime(expiry_str, "%Y-%m-%d").date()

        if expiry < today:
            table.delete_item(
                Key={
                    'user_id': item['user_id'],
                    'item_id': item['item_id']
                }
            )
            deleted_items.append(item)
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=f"❌ ShelfSense: '{item['item_name']}' was auto-deleted. It expired on {item['expiry_date']}."
            )

        elif expiry == threshold:
            near_expiry_items.append(item)

    recipe_text = ""

    if near_expiry_items:
        ingredients = ",".join(i['item_name'].lower() for i in near_expiry_items)
        encoded_ingredients = urllib.parse.quote(ingredients)
        url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={encoded_ingredients}&number=5&apiKey={"8a2b6d17d0c4458ba596bd1f4f30670b"}"

        try:
            with urllib.request.urlopen(url) as response:
                recipe_data = json.loads(response.read().decode())

            if recipe_data:
                recipe_text = "\n\n🍽 Suggested Recipes:\n" + "\n".join(
                    f"- {r['title']}" for r in recipe_data
                )
            else:
                recipe_text = "\n\nNo recipes found for your ingredients 😞"

        except Exception as e:
            recipe_text = f"\n\nError fetching recipes: {str(e)}"

        message = "⚠️ ShelfSense Alert: Items expiring soon:\n" + "\n".join(
            f"- {i['item_name']} (expires on {i['expiry_date']})"
            for i in near_expiry_items
        ) + recipe_text

        sns.publish(TopicArn=SNS_TOPIC_ARN, Message=message)

    return {
        "expiring": len(near_expiry_items),
        "auto_deleted": len(deleted_items)
    }
