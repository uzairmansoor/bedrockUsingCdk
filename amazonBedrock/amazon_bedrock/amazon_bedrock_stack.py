from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    CfnOutput,
    aws_iam as iam,
    aws_bedrock as bedrock,
    aws_opensearchserverless as opensearchserverless
)
import os
import json
from constructs import Construct

class AmazonBedrockStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_role = iam.Role(
            self,
            "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )

        lambda_function = _lambda.Function(
            self,
            "LambdaHandler",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="lambda_function.lambda_handler",
            code=_lambda.AssetCode("lambda/test.zip"),
            role=lambda_role,
            timeout=Duration.seconds(30),
        )

        principal = iam.ServicePrincipal("bedrock.amazonaws.com")
        lambda_function.add_permission(
            "agent-invoke-lambda", principal=principal, action="lambda:InvokeFunction"
        )

        agent_role = iam.Role(
            self,
            "BedrockAgentIamRole",
            role_name="AmazonBedrockExecutionRoleForAgents_" + "budgetbytesAgent",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            description="Agent role created by CDK.",
        )
        # This agent has permissions to do all things Bedrock
        agent_role.add_to_policy(
            iam.PolicyStatement(
                actions=["*"],
                resources=["*"],
            )
        )

        bedrock_agent_role = iam.Role(self, 'bedrock-agent-role',
            role_name='AmazonBedrockExecutionRoleForAgents_KIUEYHSVDR',
            assumed_by=iam.ServicePrincipal('bedrock.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonBedrockFullAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AWSLambda_FullAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchLogsFullAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AdministratorAccess')         
            ],
        )

        bedrock_agent_role.add_to_policy(
            iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["bedrock:InvokeModel", "bedrock:InvokeModelEndpoint", "bedrock:InvokeModelEndpointAsync"],
            resources=["*"],
            )
        )

        # schema = {
        #     "type": "object",
        #     "properties": {
        #         "input": {"type": "string"},
        #         "output": {"type": "string"}
        #     },
        #     "required": ["input", "output"]
        # }
        # schema_json = json.dumps(schema)
        # action_groups=bedrock.CfnAgent.AgentActionGroupProperty(
        #     action_group_name="testActionGroup",
        #     action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
        #         lambda_=lambda_function.function_arn
        #     ),
        #     api_schema=bedrock.CfnAgent.APISchemaProperty(payload=schema_json),
        #     description="Action that will trigger the lambda",
        # )

        bedrock_agent = bedrock.CfnAgent(self,"budgetbytesAgent",
            agent_name="budgetbytesAgent",
            # action_groups=[action_groups],
            auto_prepare=True,
            description="Test Agent",
            foundation_model="amazon.titan-text-premier-v1:0",
            instruction="You are a cooking recipe generation chatbot.",
            agent_resource_role_arn=bedrock_agent_role.role_arn,
        )

        cfn_agent_alias = bedrock.CfnAgentAlias(self, "MyCfnAgentAlias",
            agent_alias_name="bedrock-agent-alias",
            agent_id=bedrock_agent.ref,
            description="bedrock agent alias to simplify agent invocation",
            tags={
                "owner": "saas"
            }
        )
        cfn_agent_alias.add_dependency(bedrock_agent)

        # Define the collection and reference the security policy
        # cfn_collection = opensearchserverless.CfnCollection(self, "MyCfnCollection",
        #     name="collep95x4prargh671kq0a2",
        #     description="Opensearch collection",
        #     type="VECTORSEARCH"
        # )
        
        # cfn_knowledge_base = bedrock.CfnKnowledgeBase(self, "BedrockKnowledgeBase",
        #     knowledge_base_configuration=bedrock.CfnKnowledgeBase.KnowledgeBaseConfigurationProperty(
        #         type="VECTOR",
        #         vector_knowledge_base_configuration=bedrock.CfnKnowledgeBase.VectorKnowledgeBaseConfigurationProperty(
        #             embedding_model_arn="arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1" #amazon.titan-embed-text-v1"
        #         )
        #     ),
        #     name="BedrockKnowledgeBase",
        #     role_arn="arn:aws:iam::381709837985:role/service-role/AmazonBedrockExecutionRoleForKnowledgeBase_372ld",
        #     storage_configuration=bedrock.CfnKnowledgeBase.StorageConfigurationProperty(
        #         type="OPENSEARCH_SERVERLESS"

        #         # the properties below are optional
        #         # opensearch_serverless_configuration=bedrock.CfnKnowledgeBase.OpenSearchServerlessConfigurationProperty(
        #         #     collection_arn=cfn_collection.attr_arn,
        #         #     field_mapping=bedrock.CfnKnowledgeBase.OpenSearchServerlessFieldMappingProperty(
        #         #         metadata_field="AMAZON_BEDROCK_METADATA",
        #         #         text_field="AMAZON_BEDROCK_TEXT_CHUNK",
        #         #         vector_field="bedrock-knowledge-base-default-vector"
        #         #     ),
        #         #     vector_index_name="bedrock-knowledge-base-default-vector"
        #         # )
        #     ),
        #     description="description",
        #     tags={
        #         "tags_key": "tags"
        #     }
        # )
