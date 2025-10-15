import boto3
import json
import os
from decimal import Decimal
from datetime import datetime
from botocore.exceptions import ClientError

# --- Load environment variables from Lambda configuration ---
TABLE_NAME = os.environ["TABLE_NAME"]          # DynamoDB table
S3_BUCKET = os.environ["S3_BUCKET"]            # S3 bucket name
S3_PREFIX = os.environ["S3_PREFIX"]            # S3 folder/prefix
MAX_ITEMS = int(os.environ.get("MAX_ITEMS", 50))     # Max latest records to export
MAX_SCAN_PAGES = int(os.environ.get("MAX_SCAN_PAGES", 10))  # Max scan pagination pages

# --- AWS Clients ---
dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

# --- Fetch latest data from DynamoDB ---
def fetch_latest_data():
    table = dynamodb.Table(TABLE_NAME)
    all_items = []
    page_count = 0

    print(f"🔍 Scanning DynamoDB table: {TABLE_NAME} (full scan)")

    try:
        scan_kwargs = {}  # Full scan to get all fields
        response = table.scan(**scan_kwargs)

        while True:
            items = response.get("Items", [])
            all_items.extend(items)

            if "LastEvaluatedKey" not in response or page_count >= MAX_SCAN_PAGES:
                break

            page_count += 1
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"], **scan_kwargs)

        # Sort by event_timestamp descending
        timestamp_key = "event_timestamp" if "event_timestamp" in all_items[0] else "timestamp"
        all_items.sort(key=lambda x: x.get(timestamp_key, 0), reverse=True)
        latest_items = all_items[:MAX_ITEMS]

        print(f"✅ Retrieved {len(latest_items)} recent records.")
        if latest_items:
            print("Sample record:", latest_items[0])

        return latest_items

    except ClientError as e:
        print(f"❌ AWS ClientError: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

# --- Save data to S3 ---
def save_to_s3(data):
    if not data:
        print("⚠️ No data to export.")
        return

    def decimal_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError

    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{S3_PREFIX}/gps_data_{timestamp_str}.json"

    try:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=filename,
            Body=json.dumps(data, indent=4, default=decimal_default),
            ContentType="application/json"
        )
        print(f"✅ File uploaded: s3://{S3_BUCKET}/{filename}")
    except ClientError as e:
        print(f"❌ Error uploading to S3: {e}")

# --- Lambda Handler ---
def lambda_handler(event, context):
    print("🚀 GPS Data Extraction Started")
    data = fetch_latest_data()
    save_to_s3(data)
    print("🏁 Process Completed Successfully")
    return {"status": "success", "records_exported": len(data)}
