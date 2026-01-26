import json
import boto3
from boto3.session import Session
import os
from datetime import datetime
import argparse
import logging


class KinesisConsumer:
    def __init__(
        self,
        stream_name="iRemoteEngineer",
        region="eu-north-1",
        identity_pool_id=os.getenv("IDENTITY_POOL_ID"),
    ):
        self.stream_name = stream_name
        self.region = region

        cognito = boto3.client("cognito-identity", region_name=region)
        resp = cognito.get_id(IdentityPoolId=identity_pool_id)
        identity_id = resp["IdentityId"]

        creds = cognito.get_credentials_for_identity(IdentityId=identity_id)[
            "Credentials"
        ]

        self.session = Session(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretKey"],
            aws_session_token=creds["SessionToken"],
            region_name=region,
        )

        self.kinesis_client = self.session.client("kinesis", region_name=region)

    def get_records_by_partition_key(self, partition_key):
        """
        Download all records from Kinesis stream with the specified partition key.
        Returns records sorted chronologically by their timestamp field.
        """
        logging.info(
            f"Fetching records from stream '{self.stream_name}' with partition key '{partition_key}'..."
        )

        all_records = []

        # Get list of shards in the stream
        response = self.kinesis_client.describe_stream(StreamName=self.stream_name)
        shards = response["StreamDescription"]["Shards"]

        logging.info(f"Found {len(shards)} shard(s) in the stream")

        # Iterate through each shard
        for shard in shards:
            shard_id = shard["ShardId"]
            logging.info(f"Processing shard: {shard_id}")

            # Get shard iterator starting from the beginning of the shard
            shard_iterator_response = self.kinesis_client.get_shard_iterator(
                StreamName=self.stream_name,
                ShardId=shard_id,
                ShardIteratorType="TRIM_HORIZON",  # Start from the oldest record
            )

            shard_iterator = shard_iterator_response["ShardIterator"]

            # Read records from this shard
            while shard_iterator:
                try:
                    records_response = self.kinesis_client.get_records(
                        ShardIterator=shard_iterator,
                        Limit=10000,  # Maximum records per request
                    )

                    records = records_response["Records"]

                    # Filter records by partition key and parse data
                    for record in records:
                        if record["PartitionKey"] == partition_key:
                            try:
                                data = json.loads(record["Data"])
                                all_records.append(
                                    {
                                        "data": data,
                                        "timestamp": data.get("timestamp"),
                                        "sequence_number": record["SequenceNumber"],
                                        "approximate_arrival_timestamp": record[
                                            "ApproximateArrivalTimestamp"
                                        ],
                                    }
                                )
                            except json.JSONDecodeError as e:
                                logging.warning(f"Could not parse record data: {e}")

                    # Get next shard iterator
                    shard_iterator = records_response.get("NextShardIterator")

                    # If no more records in this request, break
                    if not records:
                        break

                except Exception as e:
                    logging.error(f"Error reading from shard {shard_id}: {e}")
                    break

        # Sort records chronologically by timestamp
        if all_records:
            all_records.sort(key=lambda x: x["timestamp"] if x["timestamp"] else "")
            logging.info(f"Total records found: {len(all_records)}")
        else:
            logging.info(f"No records found with partition key '{partition_key}'")

        return all_records

    def save_records_to_file(self, records, output_file):
        """
        Save the downloaded records to a JSON file.
        """
        with open(output_file, "w") as f:
            json.dump(records, f, indent=2, default=str)
        logging.info(f"Records saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Download records from Kinesis by partition key"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output JSON file path",
        default="kinesis_records.json",
    )
    parser.add_argument(
        "--stream",
        "-s",
        type=str,
        help="Kinesis stream name",
        default="iRemoteEngineer",
    )
    parser.add_argument(
        "--region", "-r", type=str, help="AWS region", default="eu-north-1"
    )

    args = parser.parse_args()

    # Create consumer and fetch records
    consumer = KinesisConsumer(stream_name=args.stream, region=args.region)

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2JieV9uYW1lIjoiZ3Qgc3ByaW50IiwiZXhwIjoxNzY4NDIxNTk4LCJpYXQiOjE3NjgzMzUxOTh9.2jz-YIqiYX6hSFebXpK3JPlM3BckDv8RNMsEh2l1DIg"
    records = consumer.get_records_by_partition_key(token)

    if records:
        consumer.save_records_to_file(records, args.output)
        logging.info(f"First record timestamp: {records[0]['timestamp']}")
        logging.info(f"Last record timestamp: {records[-1]['timestamp']}")


if __name__ == "__main__":
    main()
