import boto3
import os
import json
from datetime import date, timedelta, datetime
from functools import cache
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType, batch_processor
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from shared.twitter_backup_job import TwitterBackupJob
from shared.parameters_utils import get_secret_parameter
import tweepy
import requests

firehose = boto3.client('firehose')


processor = BatchProcessor(event_type=EventType.SQS)
logger = Logger()

def record_handler(record: SQSRecord):
    payload: str = record.body
    client = tweepy.Client(get_secret_parameter(os.environ['TWITTER_BEARER_PARAM_NAME']))
    if payload:
        message = TwitterBackupJob.from_json(payload)
        logger.info(f"Pulling {message.twitter_account}", extra=message.to_dict())
        today = date.today()
        yesterday = today - timedelta(days = 1)
        yesterday_start = datetime.combine(yesterday, datetime.min.time())
        yesterday_end = datetime.combine(yesterday, datetime.max.time())
        
        user = client.get_user(username=message.twitter_account)
        tweets = client.get_users_tweets(id=user.data.id, start_time=yesterday_start, end_time=yesterday_end)
        if tweets.data:
            logger.info(f"Found {len(tweets.data)} tweets for {message.twitter_account}")
            tweets_text = [{"Data": json.dumps({"text": tweet.text, "twitter_account": message.twitter_account})} for tweet in tweets.data]
            firehose.put_record_batch(DeliveryStreamName=os.environ["TWITTER_FH_NAME"], Records=tweets_text)
            logger.info(f"Data sent to FH successfully")
        else:
            logger.info(f"No tweets for {message.twitter_account}")
           
       
       
@logger.inject_lambda_context(log_event=True)
@batch_processor(record_handler=record_handler, processor=processor)
def lambda_handler(event:dict, context):
   return processor.response()