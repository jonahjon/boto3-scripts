import boto3
import sys
from botocore.exceptions import ClientError

ec2= boto3.client('ec2')
if sys.argv[1] == "ON":
    response = ec2.monitor_instances(InstanceIDs=['INSTANCE_ID'])
else:
    respone = ec2.unmonitor_instances(InstanceIDs=['INSTANCE_ID'])
print(response)






