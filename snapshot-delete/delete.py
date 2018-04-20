# Delete snapshots older than retention period

import boto3
from botocore.exceptions import ClientError
from prettytable import PrettyTable
from prettytable import PLAIN_COLUMNS
from datetime import datetime,timedelta
import time

#delete function
def delete_snapshot(snapshot_id, reg):
    print "Deleting snapshot %s " % (snapshot_id)
    try:  
        ec2resource = boto3.resource('ec2', region_name=reg)
        snapshot = ec2resource.Snapshot(snapshot_id)
        snapshot.delete()
    except ClientError as e:
        print "Caught exception: %s" % e
        
    return
    
#PrettyTable is borderless is my go-to for emails through SES
tagged_delete_list = []
untagged_delete_list = []

deletion_counter = 0
size_counter = 0

#checks all regions
for region in regions:
    print "Checking region %s " % region['RegionName']
    reg=region['RegionName']

    ec2 = boto3.client('ec2', region_name=reg)
    
    # Grab all snapshot id's
    result = ec2.describe_snapshots( OwnerIds=[account_id], Filters=filter )

    #Gets name or description if no name
    for snapshot in result['Snapshots']:
        print "Checking snapshot %s which was created on %s" % (snapshot['SnapshotId'],snapshot['StartTime'])
        snapshot_time = snapshot['StartTime'].replace(tzinfo=None)
        if snapshot['Tags'][0]['Key'] == 'Name':
            snapname = snapshot['Tags'][0]['Value']
        else:
            snapname = snapshot['Description']
        # Check if the timedelta is greater than retention days
        if (now - snapshot_time) > timedelta(retention_days_tag):
            
            #Delete or post error if fail
            try:
                delete_snapshot(snapshot['SnapshotId'], reg)
            except Exception as e:
                print e
            #Take out minutes/seconds from timestamp
            formatted_time = snapshot_time.strftime("%Y-%m-%d")
            
            #Increment counters, and give verbose as deleting
            print "Snapshot's DeleteOn Tag is has passed, and is now older than %d days " % (retention_days_tag)
            report.add_row([snapname, snapshot['SnapshotId'], snapshot['VolumeSize'], formatted_time])
            deletion_counter = deletion_counter + 1
            size_counter = size_counter + snapshot['VolumeSize']
            print "Deleting snapshot " + snapshot['SnapshotId']
        else:
            print "Snapshot is newer than configured retention of %d days so we keep it" % (retention_days_tag)

#cost calculator based off 1% drift / day
cost = (((size_counter) * .05) * 4.65) / 365
intcost = round(cost) 
totals = 'Deleted {number} snapshots totalling {size} GB saving us an estimated ${saving} each month'.format(
	number=deletion_counter,
	size=size_counter,
    saving=intcost
)
#format table and turn to string for SES
report.sortby = "Name"
report.align['Snapshot age'] = 'l'
report.align['Snapshot Size'] = 'l'
report.align['Name'] = 'l'
str1 = report.get_string()
report.del_row(0)
str1 = report.get_string()
statement = 'Snapshots not part of AMIs and older than %s Days\n' % (str(retention_days_tag))
tosend = (('\n' * 3) + totals + ('\n' * 3) + statement + str1)


tosend = (('\n' * 3) + totals + ('\n' * 3) + statement + str1)
print (tosend)

#Send out emails
          
client = boto3.client('ses', region_name='us-east-1') #Choose which region you want to use SES
response = client.send_email(
    Source='blah@blah.com',
    Destination={
        'ToAddresses':  ['blah@blah.com'
        ]
    },
    Message={
        'Subject': {
        'Data': 'Deleting Snapshots older than 180 Days without KeepForever Tag, DRY RUN no deletion happening'
    },
    'Body': {
        'Text': {
            'Data': tosend,
            "Charset": "UTF-8"
        }
    }

    }
)
