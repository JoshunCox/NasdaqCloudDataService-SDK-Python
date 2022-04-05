import logging
import json
from importlib import resources
import ncdssdk_client.src.main.python.resources as configresources
from ncdssdk.src.main.python.ncdsclient.NCDSClient import NCDSClient
from confluent_kafka import KafkaException
import sys
import boto3
from base64 import b64encode
import json

def create_client(service, region):
    return boto3.client("kinesis", region_name="us-west-1")

def send_kinesis(kinesis_client, kinesis_stream_name, data):
    data = json.dumps(data)
    shardCount = "1" # shard counter
    response = kinesis_client.put_record(
                StreamName = kinesis_stream_name,
                Data=data,
                PartitionKey=shardCount
            )
    return response
security_cfg = {
    "oauth.token.endpoint.uri": "https://clouddataservice.auth.nasdaq.com/auth/realms/pro-realm/protocol/openid-connect/token",
    "oauth.client.id": "hedgepro-kyle-rawi",
    "oauth.client.secret": "78bf2c04-d1db-4147-834e-dfd2adb15785"
}

kafka_cfg = {
    "bootstrap.servers": "kafka-bootstrap.clouddataservice.nasdaq.com:9094",
    "auto.offset.reset": "earliest"
}

ncds_client = None
topic = "NLSUTP"

ncds_client = NCDSClient(security_cfg, kafka_cfg)
consumer = ncds_client.ncds_kafka_consumer(topic)
kinesis_stream_name = "NasdaqLivePriceKinesis"
kinesis = create_client('kinesis','eu-west-1')

try:
    while True:
        message = consumer.poll(sys.maxsize)
        if message:
            value = message.value()
            if value['msgType'] in ['T', 't']:
                response = send_kinesis(kinesis, kinesis_stream_name, value)
                print("===value==="*5)
                print(value)
                print("===response==="*5)
                print(response)
except KafkaException as e:
    logging.exception(f"Error in cont stream {e.args[0].str()}")
finally:
    consumer.close()