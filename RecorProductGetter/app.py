import json
import os
import traceback

from recor_product_getter.libs.services.product_getter_service import (
    ProductGetterService,
)


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
        max_batch_items = int(os.getenv("IML_MAX_BATCH_ITEMS"))
        max_total_items = int(os.getenv("IML_MAX_TOTAL_ITEMS"))
        ProductGetterService().run(
            max_batch_items=max_batch_items, max_total_items=max_total_items
        )

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
