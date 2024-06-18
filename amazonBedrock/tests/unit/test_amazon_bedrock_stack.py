import aws_cdk as core
import aws_cdk.assertions as assertions

from amazon_bedrock.amazon_bedrock_stack import AmazonBedrockStack

# example tests. To run these tests, uncomment this file along with the example
# resource in amazon_bedrock/amazon_bedrock_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AmazonBedrockStack(app, "amazon-bedrock")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
