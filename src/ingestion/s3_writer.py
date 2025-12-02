# src/ingestion/s3_writer.py
import boto3
import json
from typing import List
from src.schema.entity import ProcessedPaper  # ADD THIS


class S3PaperWriter:
    def __init__(self, bucket="med-graph-corpus"):
        self.s3 = boto3.client("s3")
        self.bucket = bucket

    def write_paper(self, paper: ProcessedPaper):
        """Write processed paper to S3 for later bulk import"""
        key = f"processed-papers/{paper.pmc_id}.json"
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=paper.model_dump_json())

    def list_papers(self) -> List[str]:
        """List all processed papers in S3"""
        response = self.s3.list_objects_v2(
            Bucket=self.bucket, Prefix="processed-papers/"
        )
        return [obj["Key"] for obj in response.get("Contents", [])]

    def read_paper(self, pmc_id: str) -> ProcessedPaper:
        """Read a processed paper from S3"""
        key = f"processed-papers/{pmc_id}.json"
        response = self.s3.get_object(Bucket=self.bucket, Key=key)
        data = json.loads(response["Body"].read())
        return ProcessedPaper.model_validate(data)
