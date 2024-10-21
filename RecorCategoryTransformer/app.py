import json
import os
import traceback

from recor_category_transformer.libs.services.category_transformer_service import (
    CategoryTransformerService,
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
        max_batch_categories = int(os.getenv("IML_MAX_BATCH_CATEGORIES"))
        max_total_categories = int(os.getenv("IML_MAX_TOTAL_CATEGORIES"))
        CategoryTransformerService().run(
            max_batch_categories=max_batch_categories,
            max_total_categories=max_total_categories,
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
