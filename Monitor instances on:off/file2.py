import boto3
import sys
from botocore.exceptions import ClientError

instance_id = sys.argv[2]

action = sys.argv[1].upper()

ec2 = boto3.client('ec2')

if action == 'ON':
    try:
        ec2.start_instances(InstanceIds=[instance_id, DryRun==True])
    except ClientError as e:
        if 'DryRunOperation' not in str(e)
        raise
    
    try:
        response = ec2.start_instances(InstanceIds=[instance_id, DryRun=False])
        print(response)
    except ClientError as e:
        print (e)
else:
    try:
        ec2.start_instances(instanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        if DryRunOperation not in str(e)
        raise
    
    try:
        response = ec2.stop_instances(InstanceIds=[instance_id, DryRun=False])
        print(response)
    except ClientError as e:
        print(e)