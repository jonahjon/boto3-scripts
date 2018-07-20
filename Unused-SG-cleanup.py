
#!/usr/bin/env python3
import boto3
from prettytable import PrettyTable
from prettytable import PLAIN_COLUMNS


#creates pretty table with heders of Group, and Name, and using the Plain Columns for a clear look with no |'s
report = PrettyTable(['Group', 'Name'])
report.set_style(PLAIN_COLUMNS)

#Get all the SG's
def lookup_by_id(sgid):
    sg = ec2.get_all_security_groups(group_ids=sgid)
    return sg[0].name

# Getting our ec2 data, and making list of all groups
client = boto3.client('ec2')
ec2 = boto3.resource('ec2')
all_groups = []

whitelist = ['sg-xxxxxxx']
# Get ALL security groups names, and creating group of all SG ID's
security_groups_dict = client.describe_security_groups()
security_groups = security_groups_dict['SecurityGroups']
for groupobj in security_groups:
    if groupobj['GroupName'] == 'default' or groupobj['GroupName'].startswith('d-') or groupobj['GroupName'].startswith('AWS-OpsWorks-') or groupobj['GroupName'].startswith('ElasticMapReduce') or groupobj['GroupName'].startswith('Data-ETL'):
        security_groups_in_use.append(groupobj['GroupId'])
    all_groups.append(groupobj['GroupId'])

# Get all security groups used by instances
instances_dict = client.describe_instances()
reservations = instances_dict['Reservations']
network_interface_count = 0

#Checks through all instances for GroupID
for i in reservations:
    for j in i['Instances']:
        for k in j['SecurityGroups']:
            if k['GroupId'] not in security_groups_in_use:
                security_groups_in_use.append(k['GroupId'])		

# Security Groups in use by Network Interfaces				
eni_client = boto3.client('ec2')
eni_dict = eni_client.describe_network_interfaces()
for i in eni_dict['NetworkInterfaces']:
	for j in i['Groups']:
		if j['GroupId'] not in security_groups_in_use:
			security_groups_in_use.append(j['GroupId'])

# Security groups used by classic ELBs
elb_client = boto3.client('elb')
elb_dict = elb_client.describe_load_balancers()
for i in elb_dict['LoadBalancerDescriptions']:
    for j in i['SecurityGroups']:
        if j not in security_groups_in_use:
            security_groups_in_use.append(j)

# Security groups used by ALBs
elb2_client = boto3.client('elbv2')
elb2_dict = elb2_client.describe_load_balancers()
for i in elb2_dict['LoadBalancers']:
    for j in i['SecurityGroups']:
        if j not in security_groups_in_use:
            security_groups_in_use.append(j)

# Security groups used by RDS
rds_client = boto3.client('rds')
rds_dict = rds_client.describe_db_instances()
for i in rds_dict['DBInstances']:
	for j in i['VpcSecurityGroups']:
		if j['VpcSecurityGroupId'] not in security_groups_in_use:
			security_groups_in_use.append(j['VpcSecurityGroupId'])

# Security groups used by ElastiCache
cache_client = boto3.client('elasticache')
cache_dict = cache_client.describe_cache_clusters()
for i in cache_dict['CacheClusters']:
	for j in i['SecurityGroups']:
		if j['SecurityGroupId'] not in security_groups_in_use:
			security_groups_in_use.append(j['SecurityGroupId'])

# creating the delete groups, and the dict for reporting with name, and SG ID
delete_candidates = []
d = {}
# Checks all groups vs groups in use, to generate our list, and a dict with all SG's and ID's
for group in all_groups:
    if group not in security_groups_in_use:
        delete_candidates.append(group)
        for group in security_groups:
            d.update({(group['GroupId']):(group['GroupName'])})

#Check again for items in dict with certain keywords to filter out
for key, value in d.items():
    if value == 'default' or value.startswith('d-') or value.startswith('AWS-OpsWorks-') or value.startswith('ElasticMapReduce') or value.startswith('Data-ETL'):
        try:
            del d[key]
        except KeyError:
            pass
    #Check keys vs delete candidates, and deletes items that match
    elif key not in delete_candidates:
        try:
            del d[key]
        except KeyError:
            pass
    elif key in whitelist:
        try:
            del d[key]
        except KeyError:
            pass
        

#sort alphabetically by Value, and create the pretty table with key/value
for k, v in sorted(d.items(), key=lambda x: x[1]):
    report.add_row([k, v])
	
report.align['Name'] = 'l'

#get string from prettytable
email_body = report.get_string()

#get String with formatted stats about things checked
email_stats = ((('\n' * 5) + "Total number of Security Groups evaluated: {0:d}".format(len(all_groups))) + (" \nTotal number of EC2 Instances evaluated: {0:d}".format(len(reservations))) +
(" \nTotal number of Load Balancers evaluated: {0:d}".format(len(elb_dict['LoadBalancerDescriptions']) + len(elb2_dict['LoadBalancers']))) + ("\n* Sub Total number of ELB evaluated: {0:d}".format(len(elb_dict['LoadBalancerDescriptions']))) +
("\n* Sub Total number of ALB evaluated: {0:d}".format(len(elb2_dict['LoadBalancers']))) + ("\nTotal number of RDS Instances evaluated: {0:d}".format(len(rds_dict['DBInstances']))) +
("\nTotal number of Elasticache Clusters evaluated: {0:d}".format(len(cache_dict['CacheClusters']))) + ("\nTotal number of Network Interfaces evaluated: {0:d}".format(len(eni_dict['NetworkInterfaces']))))            

#create one string for SES with spacing because it's picky
emailer = (email_stats + ('\n' * 3) + email_body)

#Here is the Delete Function which will be run in the future
'''
for group in delete_candidates:
    security_group = ec2.SecurityGroup(group)
    try:
        security_group.delete()
    except Exception as e:
        print(e)
        print("{0} requires manual remediation.".format(security_group.group_name))
'''


#Sends email from systems to systems with the goods
client = boto3.client('ses', region_name='us-east-1') #Choose which region you want to use SES

# Change the 2 emails before you run it

response = client.send_email(
Source='blah@blah.com',
Destination={
    'ToAddresses':  ['blah@blah.com'
    ]
},
Message={
    'Subject': {
    'Data': 'Unused Security Groups Cleanup'
},
'Body': {
    'Text': {
        'Data': emailer,
        "Charset" : "UTF-8"
    }
}

}
)
