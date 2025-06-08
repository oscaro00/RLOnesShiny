import boto3
from dotenv import load_dotenv
import os
import io

import polars as pl

def load_r2_parquet(parquet_name: str) -> pl.DataFrame:
    
    load_dotenv()  # take environment variables from .env
    r2_access_id = os.getenv('R2_ACCESS_ID')
    r2_access_secret = os.getenv('R2_ACCESS_SECRET')
    r2_endpoint = os.getenv('R2_ENDPOINT')
    bucket_name = os.getenv('R2_BUCKET_NAME')
    
    s3 = boto3.resource(
        's3',
        endpoint_url = r2_endpoint,
        aws_access_key_id = r2_access_id,
        aws_secret_access_key = r2_access_secret
    )

    buffer = io.BytesIO()
    object = s3.Object(bucket_name, parquet_name)
    object.download_fileobj(buffer)
    df = pl.read_parquet(buffer)

    return df