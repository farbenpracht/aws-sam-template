import boto3
import os
import logging
import urllib.parse
import json
import csv
import datetime
from zoneinfo import ZoneInfo

# 外部変数
s3 = boto3.client('s3')

# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

today = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S")

# メイン
def lambda_handler(event, context):
    logger.info("全体処理開始")
    
    # event発生したobjectより、バケット、key、size情報の抜き出し
    from_bucket = event['detail']['bucket']['name']
    from_key = event['detail']['object']['key']
    file_size = event['detail']['object']['size']
    logger.info("対象データ：" + from_bucket + "/" + from_key)

    # secrect managerからシークレット情報取得
    try:
        secret = get_secret()
    except Exception as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        logger.error("シークレット情報の取得にエラーが発生しました詳細: %s", str(e))
        raise e
    
    snowsecret = json.loads(secret)
      
    USER = snowsecret.get('username')
    PASSWORD = snowsecret.get('password')
    ACCOUNT = snowsecret.get('ACCOUNT')
    DATABASE = snowsecret.get('DATABASE')
    SCHEMA = snowsecret.get('SCHEMA')
    TABLE_TO = f'{DATABASE}.{SCHEMA}.TABLE_NAME'

    # csvファイルを読み取る
    try:
        response = s3.get_object(Bucket=from_bucket, Key=urllib.parse.unquote(from_key))
        content = response['Body'].read()
        content_decoded = content.decode('utf-8')
    except Exception as e:
        logger.error("ファイルを読み取れませんでした。{}/{}を確認してください。".format(urllib.parse.unquote(from_bucket), urllib.parse.unquote(from_key)))
        raise e
        
    content_decoded = content.decode('utf-8-sig').strip()
    lines = content_decoded.split('\n')
    csv_reader = csv.reader(lines)
    rows = list(csv_reader)

    logger.info("全体処理正常終了")
    
# AWS Secret ManagerからSnowflakeのアカウント情報取得
def get_secret():
    
    secret_name = os.environ['SECRET_NAME']
    region_name = os.environ['REGION_NAME']

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']

    return secret
