import boto3
import os
from aws_lambda_powertools import Logger
from shared.twitter_backup_job import TwitterBackupJob
from shared.parameters_utils import get_parameter

logger = Logger()

# Improve warm start performance.
sqs = boto3.resource('sqs')
queue = sqs.Queue(os.environ["BACKUP_JOB_QUEUE_NAME"])

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event:dict, context):
   logger.info(f"Backing up twitter accounts.")
   
   data = get_parameter(os.environ["TWITTER_ACCOUNTS_PARAMETER_NAME"]).split(",")
   logger.info(f"Publishing for backup {len(data)} accounts. Accounts: {','.join(data)}")
   for item in data:
      # Assuming there aren't a lot of accounts, I'll avoid batch send.
      queue.send_message(MessageBody=TwitterBackupJob(twitter_account=item).to_json())
       
