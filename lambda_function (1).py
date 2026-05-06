import json
import boto3
import os
from datetime import datetime

# Initialize AWS services
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Get table name from environment variable
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])


def lambda_handler(event, context):
    # Loop through SQS messages
    for record in event['Records']:
        try:
            # Step 1: Read SQS message
            body = json.loads(record['body'])

            # Step 2: Extract S3 details
            s3_record = body['Records'][0]
            bucket = s3_record['s3']['bucket']['name']
            key = s3_record['s3']['object']['key']

            # Step 3: Extract billId from S3 key (bills/<uuid>.json)
            file_name = key.split('/')[-1]
            bill_id = file_name.replace('.json', '')

            # Step 4: Get file from S3
            response = s3.get_object(Bucket=bucket, Key=key)
            file_content = response['Body'].read().decode('utf-8')

            # Step 5: Convert to JSON
            data = json.loads(file_content)

            # Step 6: Validate required fields
            if 'accountNumber' not in data:
                print("ERROR: accountNumber missing in file:", key)
                continue
            if 'billNumber' not in data:
                print("ERROR: billNumber missing in file:", key)
                continue
            if 'amountDue' not in data:
                print("ERROR: amountDue missing in file:", key)
                continue

            # Step 7: Create item for DynamoDB
            item = {
                'billId': bill_id,
                'accountNumber': data.get('accountNumber'),
                'billNumber': data.get('billNumber'),
                'amountDue': data.get('amountDue'),
                's3Bucket': bucket,
                's3Key': key,
                'processedAt': datetime.utcnow().isoformat()
            }

            # Step 8: Insert into DynamoDB
            table.put_item(Item=item)
            print("SUCCESS: File processed:", key)

        except Exception as e:
            print("ERROR processing message:", str(e))

    return {
        'statusCode': 200,
        'body': 'Done'
    }
