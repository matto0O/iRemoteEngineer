import json
import boto3
from boto3.session import Session

class KinesisProducer:
	def __init__(self, stream_name="iRacingEngineer", region="eu-north-1", 
			   		identity_pool_id="eu-north-1:c475f3dd-658f-4d5c-80b0-8ea10b908e09", debug_mode=False):
		self.stream_name = stream_name
		self.debug_mode = debug_mode

		cognito = boto3.client('cognito-identity', region_name=region)
		resp = cognito.get_id(IdentityPoolId=identity_pool_id)
		identity_id = resp['IdentityId']

		creds = cognito.get_credentials_for_identity(IdentityId=identity_id)['Credentials']

		self.session = Session(
			aws_access_key_id=creds['AccessKeyId'],
			aws_secret_access_key=creds['SecretKey'],
			aws_session_token=creds['SessionToken'],
			region_name=region
		)

		self.kinesis_client = self.session.client('kinesis', region_name=region)

	def send_record(self, data, partition_key):
		# print(f"Sending data to Kinesis stream {self.stream_name} with partition key {partition_key}")
		if self.debug_mode:
			print(data)
			return (200, "Debug mode")
		
		response = self.kinesis_client.put_record(
			StreamName=self.stream_name,
			Data=json.dumps(data),
			PartitionKey=partition_key
		)
		return response