# GPS Lambda Data Export Project

## Overview
This project contains a Python Lambda function to extract the 50 most recent GPS records from DynamoDB (`sb_teltonika_gps_data`) and export them as JSON to an S3 bucket (`gps-data-export`). The function runs automatically every 4 hours using EventBridge.

## Folder Structure
- `lambda_function.py`: Lambda function code
- `.env.example`: Example environment variables
- `TELTONIKA_DYNAMODB.md`: Teltonika & DynamoDB Markdown report
- `sample_output.json`: Example exported JSON
- `.gitignore`: Prevents committing sensitive files

## AWS Configuration
- **IAM Role:** `lambda-gps-export-role`  
  Permissions: DynamoDB read, S3 full access, CloudWatch logs
- **EventBridge Rule:** `0 */4 * * ? *` (every 4 hours)
- **S3 Bucket:** `gps-data-export`  
  Bucket policy allows Lambda role to write objects.

## Usage
1. Set environment variables in `.env`.
2. Deploy `lambda_function.py` to AWS Lambda.
3. Configure EventBridge rule for scheduled execution.
4. Monitor logs in CloudWatch.
5. Check exported JSON in `s3://gps-data-export/gps_exports/`.
