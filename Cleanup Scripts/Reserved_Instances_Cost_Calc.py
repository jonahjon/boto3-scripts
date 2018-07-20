#!/usr/bin/env python
from __future__ import print_function
from prettytable import PrettyTable
from prettytable import PLAIN_COLUMNS
import argparse
import re
import boto3.session
import six

#Add in parsing standards to start
parser = argparse.ArgumentParser(
    description="Shows summary about 'Reserved' and 'On-demand' ec2 instances")
parser.add_argument("--region", type=str, default="us-east-1",
                    help="AWS Region name. Default is 'cn-north-1'")
args = parser.parse_args()
REGION = 'us-east-1'

#Declare Tables with no Columns because SES f's that up
ReservedTable = PrettyTable(['Number', 'Instance Type & Platform'])
ReservedTable.set_style(PLAIN_COLUMNS)

NotUsedTable = PrettyTable(['Number', 'Instance Type & Platform'])
NotUsedTable.set_style(PLAIN_COLUMNS)

OnDemandTable = PrettyTable(['Number', 'Instance Type & Platform'])
OnDemandTable.set_style(PLAIN_COLUMNS)

ec2_client = boto3.client('ec2')
ec2 = boto3.resource('ec2')

#Make Centos = Red Hat
IMAGE_PLATFORM_PAT = {
    'Red Hat': [
        re.compile(r'.*\b(RHEL|rhel)\b.*'),
    ],
}
image_id_to_platform = {}

# Retrieve instances
instances = ec2.instances.all()
running_instances = {}
for i in instances:
    if i.state['Name'] != 'running':
        continue

    image_id = i.image_id
    if image_id in image_id_to_platform:
        platform = image_id_to_platform[image_id]
    else:
        platform = 'Linux/UNIX'
        try:
            image = ec2.Image(image_id)
            if image.platform:
                platform = image.platform
            elif image.image_location.startswith('841258680906/'):
                platform = 'Red Hat'
            else:
                image_name = image.name
                for plat, pats in six.iteritems(IMAGE_PLATFORM_PAT):
                    for pat in pats:
                        if pat.match(image_name):
                            platform = plat
                            break
        except AttributeError:
            platform = 'Linux/UNIX'

        image_id_to_platform[image_id] = platform

    key = (platform, i.instance_type, i.placement['AvailabilityZone'] if 'AvailabilityZone' in i.placement else REGION)
    running_instances[key] = running_instances.get(key, 0) + 1

# Retrieve reserved instances
reserved_instances = {}
soon_expire_ri = {}
key = ()
reservations = ec2_client.describe_reserved_instances()
for ri in reservations['ReservedInstances']:
    if ri['State'] not in ('active', 'payment-pending'):
        continue
    key = (ri['ProductDescription'], ri['InstanceType'])
    reserved_instances[key] = \
        reserved_instances.get(key, 0) + ri['InstanceCount']



# Create a dict relating reserved instance keys to running instances.
# Reserveds get modulated by running.
diff = dict([(x, reserved_instances[x] - running_instances.get(x, 0))
             for x in reserved_instances])

# Subtract all unspecific RI's
for reserved_pkey in reserved_instances:
    for running_pkey in running_instances:
        if running_pkey[0] == reserved_pkey[0] and running_pkey[1] == reserved_pkey[1]:
            diff[running_pkey] = diff.get(running_pkey, 0) + running_instances[running_pkey]
            diff[reserved_pkey] -= running_instances[running_pkey]

# For all other running instances, add a negative amount
for pkey in running_instances:
    if pkey not in reserved_instances:
        diff[pkey] = diff.get(pkey, 0) - running_instances[pkey]

unused_ri = {}
unreserved_instances = {}
for k, v in six.iteritems(diff):
    if v > 0:
        unused_ri[k] = v
    elif v < 0:
        unreserved_instances[k] = -v

# Report Table for Reserved Instances
print("Reserved instances:")
for k, v in sorted(six.iteritems(reserved_instances), key=lambda x: x[1], reverse=True):
#Add the Tuple into format for good tables
    use = ()
    for z in reversed(k):
        use = use + (z,)
    print("\t(%s)\t%12s\t%s" % ((v,) + use))
    ReservedTable.add_row([v, use])
print("")

print("Unused reserved instances:")
for k, v in sorted(six.iteritems(unused_ri), key=lambda x: x[1], reverse=True):
    unuse = ()
    for z in reversed(k):
        unuse = unuse + (z,)
    print("\t(%s)\t%12s\t%s" % ((v,) + unuse))
    NotUsedTable.add_row([v, unuse])
if not unused_ri:
    print("\tNone")
print("")


print("On-demand instances, which haven't got a reserved instance:")
for k, v in sorted(six.iteritems(unreserved_instances), key=lambda x: x[1], reverse=True):
    demand = ()
    for z in reversed(k):
        demand = demand + (z,)
    OnDemandTable.add_row([v, demand])
if not unused_ri:
    print("\tNone")
print("")

#align table columns
ReservedTable.align['Instance Type & Platform'] = 'l'
NotUsedTable.align['Instance Type & Platform'] = 'l'
OnDemandTable.align['Instance Type & Platform'] = 'l'

#make Errr thing into a string and add a little verbage about instance types
email1 = ReservedTable.get_string()
email2 = NotUsedTable.get_string()
email4 = OnDemandTable.get_string()
stuffy = "--T2 Instance Class\n\t - This is an Instance with baseline stats, and above Baseline Burstable Computing \n\n --M4 Instance Class\n\t - Instance class with balanced compute, memory, and network \n\n --C4 Instance Class\n\t - C Class Instances are optimized for Compute-Intensive workloads\n\n\n"
email3= (stuffy + "RESERVED INSTANCES IN USE\n" + email1 + ('\n' * 3) + "RESERVED INSTANCES NOT BEING USED\n" + email2 + ('\n' * 3) + "ON DEMAND INSTANCES WHICH DON'T HAVE A RESERVED INSTANCE\n" + email4 )


#Sends email from systems to systems with the goods
client = boto3.client('ses', region_name='us-east-1') #Choose which region you want to use SES

response = client.send_email(
Source='blah@blah.com',
Destination={
    'ToAddresses':  ['blah@blah.com'
    ]
},
Message={
    'Subject': {
    'Data': 'Unused Reserved Instances'
},
'Body': {
    'Text': {
        'Data': email3,
        "Charset" : "UTF-8"
    }
}

}
)