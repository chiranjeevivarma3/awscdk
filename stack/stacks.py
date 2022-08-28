from unicodedata import name
from aws_cdk import (
    aws_glue as glue,
    aws_iam as iam,
    aws_lambda as cfn_lambda, 
    Stack,
    aws_stepfunctions as stepfunctions
)
from constructs import Construct
import aws_cdk as cdk

class PowerCurveDataCopy(Stack):

    def __init__(self, scope: Construct,  construct_id: str, sol_name, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.sol_name=sol_name
    
    def create_iam_role(self, assume_role_policy_document, policy_document, tags, role_name):
        cfn_role = iam.CfnRole(self, role_name,
            assume_role_policy_document=assume_role_policy_document,
            # the properties below are optional
            description="description",
            managed_policy_arns=["managedPolicyArns"],
            max_session_duration=123,
            path="path",
            permissions_boundary="permissionsBoundary",
            policies=[iam.CfnRole.PolicyProperty(
                policy_document=policy_document,
                policy_name=f'{self.sol_name}_{role_name}'
            )],
            role_name=self.sol_name,
            tags=tags
            # tags=[cdk.CfnTag(
            #     key="key",
            #     value="value"
            # )]
        )
        return cfn_role

    def create_glue_connection(self, connection_name: str, availability_zone: str, security_group_id_list: list, subnet_id: str):
        network_connection = glue.CfnConnection(self, connection_name,
            catalog_id="catalogId",
            connection_input=glue.CfnConnection.ConnectionInputProperty(
                connection_type="NETWORK",
                # the properties below are optional
                # connection_properties=connection_properties, 
                description="VPC network connection",
                # match_criteria=["matchCriteria"],
                name=connection_name,
                physical_connection_requirements=glue.CfnConnection.PhysicalConnectionRequirementsProperty(
                    availability_zone=availability_zone,
                    security_group_id_list=security_group_id_list,
                    subnet_id=subnet_id
                )
            )
        )
        return network_connection
    
    def create_glue_job(self, script_location, role, default_arguments, job_type, tags, job_name, connections = []):
        cfn_job = glue.CfnJob(self, f"{job_name}_{job_type}",
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                python_version="3.9",
                script_location=script_location
            ),
            role=role.role_name,

            # the properties below are optional
            allocated_capacity=1,
            connections=glue.CfnJob.ConnectionsListProperty(
                connections=connections
            ),
            default_arguments=default_arguments,

            description="pdc",
            execution_property=glue.CfnJob.ExecutionPropertyProperty(
                max_concurrent_runs=123
            ),
            glue_version="3.0",
            max_capacity=123,
            max_retries=123,
            name=f"{job_name}_{job_type}_{self.sol_name}",
            notification_property=glue.CfnJob.NotificationPropertyProperty(
                notify_delay_after=123
            ),
            number_of_workers=123,
            tags= tags,
            timeout=123,
            worker_type="workerType"
        )
        return cfn_job

    def create_lambda_function(self, role, s3_bucket, s3_key, env_variables, tags, job_name):       
        cfn_function = cfn_lambda.CfnFunction(self, job_name,
            code= cfn_lambda.CfnFunction.CodeProperty(
                s3_bucket=s3_bucket,
                s3_key=s3_key
            ),
            role=role.attr_arn,
            # the properties below are optional
            architectures=["architectures"],
            code_signing_config_arn="codeSigningConfigArn",
            description="description",
            environment=cfn_lambda.CfnFunction.EnvironmentProperty(
                variables=env_variables
            ),
            function_name=f"{job_name}_{self.sol_name}",
            handler="handler",
            layers=["layers"],
            runtime="runtime",
            tags=[cdk.CfnTag(
                key="key",
                value="value"
            ),cdk.CfnTag(
                key="c",
                value="jh"
            )],
            # tags=[cdk.CfnTag(key=x,value=y) for x,y in tags.items()],
            timeout=123
            
        )
        return cfn_function

#### stepfunctions
    def create_sfn(self, role, definition_string, definition_substitutions, tags, job_name):
        cfn_state_machine = stepfunctions.CfnStateMachine(self, f"{job_name}_sfn",
            role_arn=role.attr_arn,

            # the properties below are optional
            
            definition_string=definition_string,
            definition_substitutions={
                "definition_substitutions_key": definition_substitutions
            },
            state_machine_name=f"{job_name}_{self.sol_name}",
            state_machine_type="STANDARD",
            tags=[stepfunctions.CfnStateMachine.TagsEntryProperty(
                key="key",
                value="value"
            )],
        )
        return cfn_state_machine
        
        
        
        

                


