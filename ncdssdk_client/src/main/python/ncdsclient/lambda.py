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
    return boto3.client(service, region_name=region)

def send_kinesis(kinesis_client, kinesis_stream_name, data):
    data = json.dumps(data)
    shardCount = 1 # shard counter
    # data = b64encode(bytes(str(data), 'utf-8'))
    # kinesisRecord = [{
    #     "Data": str(data), # data byte-encoded
    #     "PartitionKey": str(shardCount) # some key used to tell Kinesis which shard to use
    # }]
    response = kinesis_client.put_record(
                StreamName = kinesis_stream_name,
                Data=data,
                PartitionKey=str(shardCount)
            )
    return response
def load_auth_properties(auth_props_file):
    cfg = {}
    try:
        if auth_props_file:
            with open(auth_props_file) as f:
                cfg = json.load(f)
                f.close()
        else:
            with resources.open_text(configresources, "client-authentication-config.json") as f:
                cfg = json.load(f)
            f.close()

    except OSError as e:
        logging.exception(f"Could not open/read file: {auth_props_file}")
        raise e

    return cfg

def load_kafka_config(kafka_cfg_file):
    cfg = {}
    try:
        if kafka_cfg_file:
            with open(kafka_cfg_file) as f:
                cfg = json.load(f)
            f.close()
        else:
            with resources.open_text(configresources, "kafka-config.json") as f:
                cfg = json.load(f)
            f.close()

    except OSError as e:
        logging.exception(f"Could not open/read file: {kafka_cfg_file}")
        raise e

    return cfg 

security_cfg = load_auth_properties("./client-authentication-config.json")
kafka_cfg = load_kafka_config("./kafka-config.json")
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
            response = send_kinesis(kinesis, kinesis_stream_name, value)
            print(value)
            print("="*120)
            print(response)
except KafkaException as e:
    logging.exception(f"Error in cont stream {e.args[0].str()}")
finally:
    consumer.close()