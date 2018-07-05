import boto3
import re


ec2 = boto3.client('ec2')

# These are the tags to apply
TagKey = 'Application'
TagValue = 'Grafana'
# To any instance with this string in it
boxname = 'Grafana-TEST'
# Declare empty lists
ec2_names = []
ec2_id = []

def create_tags(ec2list, TagKey, TagValue ):
    ec2.create_tags(
        Resources=ec2list,
        Tags=[
            {   'Key': TagKey,
                'Value': TagValue } ] )

def get_ec2_names(Filter_key, Filter_value):
    get_stuff = ec2.describe_instances(
                 Filters=[
            {
                'Name': Filter_key,
                'Values': Filter_value
            }, ] )
    return get_stuff

# Get all Boxes with Names
get_stuff = get_ec2_names('tag-key', ['Name'])

# Add Names to list, and compare against regex we supplied in boxnames
for reservation in get_stuff['Reservations']:
    for instance in reservation['Instances'][0]['Tags']:
        if instance['Key'] == 'Name':
            ec2_names.append(instance['Value']) 
r = re.compile(".*({}).*".format(boxname))
matched_names = filter(r.match, ec2_names)

# Run the function again, this time with list of matched names
get_stuff = get_ec2_names('tag:Name', matched_names)
for reservation in get_stuff['Reservations']:
    for instance in reservation['Instances']:
        ec2_id.append(instance['InstanceId'])

print ('There are {0} Boxes matching the string: {1}\n\n{2}\n\nTagging all {0} Boxes with:  {3}:{4}'.format((len(matched_names)), boxname, matched_names, TagKey, TagValue))

try:
  create_tags(ec2_id, TagKey, TagValue)

  print ('\nAll Tagged!')

except Exception as e:
  
  print ('Failed Creating Tags, Exiting Program')
  
  exit(1)
