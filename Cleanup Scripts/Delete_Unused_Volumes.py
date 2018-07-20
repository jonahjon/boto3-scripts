import boto3  
from prettytable import PrettyTable
from prettytable import PLAIN_COLUMNS

report = PrettyTable(['Volume Id', 'Name', 'Other Tags', 'Size'])
report.set_style(PLAIN_COLUMNS)

# I Like pretty Table for sending Email Reports through SES

region = "us-east-1"  
ec2 = boto3.client("ec2", region_name=region)

def get_available_volumes():  
    #  Find's All volume which are marked as "available" #
    available_volumes = ec2.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )
    size_counter = 0
    Other_tags = ''
    for x in available_volumes['Volumes']:
        # Stores the VolumeID, and Marks the Size as int+GB since it's more human understandable #
        volume_id = x['VolumeId']
        size = (str(x['Size']) + "GB")

        #  Filtering based off Tags, Looks for Name First, then any Other Tags #
        try:
            for tag in x['Tags']:
                if tag['Key'] == 'Name':
                    Tag_name = ("Tag | Name : {0}".format(tag['Value']))
                elif tag['Key'] != ['', 'Name']:
                    Other_tags = ("Tag | {0} : {1}".format(tag['Key'],tag['Value']))
            report.add_row([volume_id, Tag_name, Other_tags, size])
        # If the Volume isn't Tagged or Named It's Deletes it, and compiles a little counter to show cost saved #
        except KeyError:
            Tag_name = 'Untagged'
            Other_tags = 'Untagged'
            size_counter = size_counter + size
            report.add_row([volume_id, Tag_name, Other_tags, size])
            ec2.delete_volume(
                VolumeId=volume_id
            )
    # Reports Cost saving based off amazon pricing of $.10 / GB / Month #
    print ("Total GB to Delete {0} Saving us ${1} Per Month{2}{2}Keeping These Volumes which are Tagged:{2}".format((str(size_counter)), (size_counter * .1), "\n"))
    return available_volumes

# Some stuff to sort the rows better, and allign them
get_available_volumes()
report.align['Name'] = 'l'
report.align['Volume Id'] = 'l'
report.align['Other Tags'] = 'l'
report.sortby = 'Size'
report.sortby = 'Name'
report.sortby = 'Other Tags'
print (report)