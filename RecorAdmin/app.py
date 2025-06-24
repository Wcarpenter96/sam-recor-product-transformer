import json
import os
import traceback

from recor_category_transformer.libs.services.category_transformer_service import (
    CategoryTransformerService,
)
from recor_admin.libs.models.reset_request import ResetRequest


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    try:
        request_type = event.get("request_type").lower()
        if request_type == "reset":
            service = ResetRequest()
        else:
            raise Exception("Invalid request type")
        service.run()

    except Exception as e:

        print(f"ERROR: {e}")
        traceback.print_exc()

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world from recor product getter!",
                # "location": ip.text.replace("\n", "")
            }
        ),
    }

