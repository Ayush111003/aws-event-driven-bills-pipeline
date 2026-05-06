import boto3
import json
import uuid
import random

s3 = boto3.client('s3')
bucket_name = "apatel638-bills-bucket"

# Generate unique bill ID
bill_id = str(uuid.uuid4())

# Create bill data
data = {
    "accountNumber": random.randint(10000, 90000),
    "billNumber": random.randint(50, 500),
    "amountDue": random.randint(0, 200)
}

# S3 key format: bills/<uuid>.json
file_name = f"bills/{bill_id}.json"

# Upload to S3
s3.put_object(
    Bucket=bucket_name,
    Key=file_name,
    Body=json.dumps(data)
)

print("Uploaded:", file_name)
