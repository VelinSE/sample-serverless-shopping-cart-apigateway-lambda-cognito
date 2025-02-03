import json
import os
from datetime import datetime

from aws_lambda_powertools import Logger, Tracer
from otel_utils import init_tracer

logger = Logger()
tracer = Tracer()

with open('product_list.json', 'r') as product_list:
    product_list = json.load(product_list)

HEADERS = {
    "Access-Control-Allow-Origin": os.environ.get("ALLOWED_ORIGIN"),
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Credentials": True,
}

otel_tracer = init_tracer("get_products")

@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    """
    Return list of all products.
    """
    with otel_tracer.start_as_current_span('root') as root:
        root.set_attribute("start_time", datetime.now())

        logger.debug("Fetching product list")

        root.set_attribute("end_time", datetime.now())
        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps({"products": product_list}),
        }
