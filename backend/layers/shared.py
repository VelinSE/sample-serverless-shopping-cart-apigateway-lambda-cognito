import calendar
import datetime
import os
import uuid
from decimal import Decimal
from http.cookies import SimpleCookie

from aws_lambda_powertools import Tracer

from jwt import PyJWKClient, decode, exceptions

tracer = Tracer()

HEADERS = {
    "Access-Control-Allow-Origin": os.environ.get("ALLOWED_ORIGIN"),
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Credentials": True,
}
JWKS_URL = f"http://localhost:4566/{os.environ['USERPOOL_ID']}/.well-known/jwks.json"


class NotFoundException(Exception):
    pass


@tracer.capture_method
def handle_decimal_type(obj):
    """
    json serializer which works with Decimal types returned from DynamoDB.
    """
    if isinstance(obj, Decimal):
        if float(obj).is_integer():
            return int(obj)
        else:
            return float(obj)
    raise TypeError


@tracer.capture_method
def generate_ttl(days=1):
    """
    Generate epoch timestamp for number days in future
    """
    future = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    return calendar.timegm(future.utctimetuple())


@tracer.capture_method
def get_user_sub(jwt_token):
    """
    Validate JWT claims & retrieve user identifier
    """
    try:
        jwks_client = PyJWKClient(JWKS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(jwt_token)
        verified_claims = decode(jwt_token, signing_key)

    except (exceptions.InvalidTokenError, ValueError):
        print("-----------------FAILED TO VERIFY---------------------")
        verified_claims = {}

    return verified_claims.get("sub")


@tracer.capture_method
def get_cart_id(event_headers):
    """
    Retrieve cart_id from cookies if it exists, otherwise set and return it
    """
    cookie = SimpleCookie()
    try:
        cookie.load(event_headers["cookie"])
        cart_cookie = cookie["cartId"].value
        generated = False
    except KeyError:
        cart_cookie = str(uuid.uuid4())
        generated = True

    return cart_cookie, generated


@tracer.capture_method
def get_headers(cart_id):
    """
    Get the headers to add to response data
    """
    headers = HEADERS
    cookie = SimpleCookie()
    cookie["cartId"] = cart_id
    cookie["cartId"]["max-age"] = (60 * 60) * 24  # 1 day
    cookie["cartId"]["secure"] = True
    cookie["cartId"]["httponly"] = True
    cookie["cartId"]["samesite"] = "None"
    cookie["cartId"]["path"] = "/"
    headers["Set-Cookie"] = cookie["cartId"].OutputString()
    return headers
