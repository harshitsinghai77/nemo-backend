# using aws-cdk to create a stack that creates an S3 bucket and a FastAPI app with the following features:
# a lambda function serving as a FastAPI app
# a API Gateway to route requests to the FastAPI app

import os
from dotenv import load_dotenv

from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    # aws_apigatewayv2 as _apigw,
)
# from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration

# Load environment variables from .env file
load_dotenv()  # This will read the .env file in the current directory

env = {
    'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'), 
    'SQLITE_CLOUD_API_KEY': os.getenv('SQLITE_CLOUD_API_KEY'), 
    'SQLITE_CLOUD_HOST': os.getenv('SQLITE_CLOUD_HOST'), 
}

class InfrastructureStack(Stack):

    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)
        
        # Create a Lambda function
        base_lambda = _lambda.Function(self, 
            "nemo-app",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="main.handler",
            code=_lambda.Code.from_asset("lambda_function.zip"),
            environment=env,
            memory_size=256,
            timeout=Duration.seconds(30)
        )

        # # Create an API Gateway
        # base_api = _apigw.HttpApi(self, "NemoAppAPIGateway",
        #     api_name='nemo-app-api',
        #     cors_preflight=_apigw.CorsPreflightOptions(
        #         allow_origins=["*"],
        #         allow_methods=[_apigw.CorsHttpMethod.GET, _apigw.CorsHttpMethod.POST, _apigw.CorsHttpMethod.DELETE],
        #         allow_headers=["*"]
        #     ))
        
        # base_api_integration = HttpLambdaIntegration("NemoAPILambdaIntegration", handler=base_lambda)
        
        # # Add API Gateway routes
        # base_api.add_routes(
        #     path="/{proxy+}",
        #     methods=[_apigw.HttpMethod.GET, _apigw.HttpMethod.POST, _apigw.HttpMethod.DELETE],
        #     integration=base_api_integration
        # )

        function_url = _lambda.FunctionUrl(self, "LambdaFunctionURL",
            function=base_lambda,
            auth_type=_lambda.FunctionUrlAuthType.NONE,
            cors={
                "allowed_origins": ["https://nemo-app.netlify.app"], 
                "allowed_methods": [_lambda.HttpMethod.GET, _lambda.HttpMethod.POST, _lambda.HttpMethod.DELETE], 
                "allowed_headers": ["*"],
            }
        )
