# using aws-cdk to create a stack that creates an S3 bucket and a FastAPI app with the following features:
# a lambda function serving as a FastAPI app
# a API Gateway to route requests to the FastAPI app

from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_s3 as _s3,
    aws_apigatewayv2 as _apigw,
    RemovalPolicy
)
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration

class InfrastructureStack(Stack):

    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create an S3 bucket
        bucket = _s3.Bucket(self, 
            id="nemo-app-db",
            bucket_name="nemo-app-db",
            block_public_access=_s3.BlockPublicAccess.BLOCK_ALL,
            versioned=False,   # No versioning (to avoid unnecessary costs)
            removal_policy=RemovalPolicy.DESTROY  # Delete all objects when the stack is deleted
        )
        
        # Create a Lambda function
        base_lambda = _lambda.Function(self, 
            "nemo-app",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="main.handler",
            code=_lambda.Code.from_asset("lambda_function.zip"),
            environment={
                "ENV": "prod",
            },
            memory_size=256,
            timeout=Duration.seconds(120)
        )

        # Grant read/write permissions to the bucket
        bucket.grant_read_write(base_lambda)

        # Create an API Gateway
        base_api = _apigw.HttpApi(self, "NemoAppAPIGateway",
            api_name='nemo-app-api',
            cors_preflight=_apigw.CorsPreflightOptions(
                allow_origins=["*"],
                allow_methods=[_apigw.CorsHttpMethod.GET, _apigw.CorsHttpMethod.POST, _apigw.CorsHttpMethod.DELETE],
                allow_headers=["*"]
            ))
        
        base_api_integration = HttpLambdaIntegration("NemoAPILambdaIntegration", handler=base_lambda)
        
        # Add API Gateway routes
        base_api.add_routes(
            path="/{proxy+}",
            methods=[_apigw.HttpMethod.GET, _apigw.HttpMethod.POST, _apigw.HttpMethod.DELETE],
            integration=base_api_integration
        )