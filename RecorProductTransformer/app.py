import json
import traceback

from recor_layer.services.woocommerce.woocommerce_service import (
    ProductTransformerService,
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

        items = []
        for record in event["Records"]:
            items.extend(json.loads(record["body"]))

        ProductTransformerService().run(items)

    except Exception as e:

        print(f"ERROR: {e}")
        traceback.print_exc()

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world from recor product transformer!",
                # "location": ip.text.replace("\n", "")
            }
        ),
    }
