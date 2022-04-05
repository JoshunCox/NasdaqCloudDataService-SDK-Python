# import testdata
import json
import boto3
import sys

# seed the pseudorandom number generator
from random import seed
from random import randint
import time
import random

kinesis = boto3.client("kinesis", region_name="us-west-1")
kinesis_stream_name = "NasdaqLivePriceKinesis"
seed(1)

i=0
while 1==1:

    new_dict={}    
    new_dict["timestamp"]=int(time.time())        
    new_dict["dataNum"]="data"+str(i)
    new_dict["device_name"]="dev"
    new_dict["HeartRate"]=random.randint(60, 120)

    print("loading ",json.dumps(new_dict))
    # time.sleep(0.2)
    
    kinesis.put_record(
        StreamName="NasdaqLivePriceKinesis", 
        Data=json.dumps(new_dict), 
        PartitionKey="1")   
    i+=1