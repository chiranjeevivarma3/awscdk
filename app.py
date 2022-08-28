#!/usr/bin/env python3
import aws_cdk as cdk
from stack.stacks import PowerCurveDataCopy 
import json

app = cdk.App()

env=cdk.Environment(account='123456789012', region='us-east-1')
pdc_stack= PowerCurveDataCopy(app, "PDC", sol_name= "pdc", env=env)

with open('config.json', 'r') as cfg:
    cfg_data = json.load(cfg)
    
    # create IAM roles for glue, sfn, lambda
    lambda_role = pdc_stack.create_iam_role(cfg_data["lambda_iam"]["assume_role_policy_document"], cfg_data["lambda_iam"]["policy_document"], cfg_data["iam_tags"], "lambda_role")
    sfn_role = pdc_stack.create_iam_role(cfg_data["sfn_iam"]["assume_role_policy_document"], cfg_data["sfn_iam"]["policy_document"], cfg_data["iam_tags"], "sfn_role")
    glue_role = pdc_stack.create_iam_role(cfg_data["glue_iam"]["assume_role_policy_document"], cfg_data["glue_iam"]["policy_document"], cfg_data["iam_tags"], "glue_role")
    
    # create glue connection 
    create_glue_connection = pdc_stack.create_glue_connection(cfg_data["glue_connections"][0], cfg_data["availability_zone"], cfg_data["security_group_id_list"], cfg_data["subnet_id"])

    for job in cfg_data["jobs"]:

        # create glue jobs  
        create_raw_job = pdc_stack.create_glue_job(job["raw_jobs"]["script_location"], glue_role, job["raw_jobs"]["default_arguments"], "raw", job["raw_jobs"]["tags"], job["job_name"], cfg_data["glue_connections"])
        create_processed_job = pdc_stack.create_glue_job(job["procesed_jobs"]["script_location"], glue_role, job["procesed_jobs"]["default_arguments"], "processed", job["procesed_jobs"]["tags"], job["job_name"])
        create_lambda_func = pdc_stack.create_lambda_function(lambda_role, "s3_bucket", "s3_key", job["lambda_env_vars"], job["lambda_tags"], job["job_name"]) 
        create_sfn = pdc_stack.create_sfn(sfn_role, job["sfn"]["definition_string"], job["sfn"]["definition_substitutions"], job["tags"], job["job_name"])
        
        
app.synth()

