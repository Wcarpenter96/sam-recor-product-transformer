import json

from recor_product_transformer.libs.services.product_transformer_service import (
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

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    items = []
    for record in event["Records"]:
        items.append(json.loads(record["body"]))

    woocommerce_products = ProductTransformerService().run(items)

    print("WOOCOMMERCE PRODUCTS")
    print(woocommerce_products)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world from recor product transformer!",
                # "location": ip.text.replace("\n", "")
            }
        ),
    }