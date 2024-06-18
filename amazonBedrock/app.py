#!/usr/bin/env python3
import os

import aws_cdk as cdk

from amazon_bedrock.amazon_bedrock_stack import AmazonBedrockStack


app = cdk.App()
AmazonBedrockStack(app, "AmazonBedrock")

app.synth()