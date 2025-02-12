import json
import os

import boto3
from aws_lambda_powertools import Logger, Tracer

from shared import handle_decimal_type
from otel_utils import OtelTracer

logger = Logger()
tracer = Tracer()

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])
otel_tracer = OtelTracer('get_cart_total')

@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    """
    List items in shopping cart.
    """
    with otel_tracer.start_trace('root') as root:
        product_id = event["pathParameters"]["product_id"]
        with otel_tracer.start_trace('db_query') as db_query:
            response = table.get_item(
                Key={"pk": f"product#{product_id}", "sk": "totalquantity"}
            )
        quantity = response["Item"]["quantity"]

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"product": product_id, "quantity": quantity}, default=handle_decimal_type
            ),
        }
