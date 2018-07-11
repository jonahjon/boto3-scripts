import boto3
import re

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    # These are the tags to apply
    TagKey = 'Name'
    TagValue = ''

    # To any instance with this string in it
    boxname = ['application1', 'application2']

    # Declare empty lists
    ec2_names = []
    ec2_id = {}

    # Functions We need
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

    def get_vpc(Filter_key, Filter_value):
        get_vpc = ec2.describe_vpcs(
                     Filters=[
                {
                    'Name': Filter_key,
                    'Values': Filter_value
                }, ] )
        return get_vpc

    # Get all Boxes with Names
    get_stuff = get_ec2_names('tag-key', ['Name'])

    # Add Names to list, and compare against regex we supplied in boxnames
    for reservation in get_stuff['Reservations']:
        for instance in reservation['Instances'][0]['Tags']:
            if instance['Key'] == 'Name':
                ec2_names.append(instance['Value']) 


    i = 0
    while i < len(boxname):
        r = re.compile(".*({}).*".format(boxname[i]))
        matched_names = filter(r.match, ec2_names)

        # Run the function again, this time with list of matched names
        get_stuff = get_ec2_names('tag:Name', matched_names)
        for reservation in get_stuff['Reservations']:
            for instance in reservation['Instances']:
                ######## This uploading values to each ec2's dict to be used later on ####################
                ec2_id.update({'InstanceID':instance['InstanceId']})
                ec2_id.update({'VPCId':instance['VpcId']})

                ########### This looks up the VPC name, and uses it to create the new name for the EC2 ###
                vpc = get_vpc('vpc-id', [ec2_id['VPCId']] )
                for tags in vpc['Vpcs'][0]['Tags']:
                    if tags['Key'] == 'Name':
                        ec2_id.update({'VPCName':tags['Value']})
                        new_name = '{0}-{1}'.format(ec2_id['VPCName'], boxname[i])
                        TagValue = new_name

                ########## This Creates the Tags for each Instance ID in the ec2_id Dict #################
                try:
                    create_tags([ec2_id['InstanceID']], TagKey, TagValue)
                except Exception as e:
                    print ('Failed Creating Tags, Exiting Program: ' + str(e))
                    exit(1)

        ############ Verbage letting you know what is going on ####################
        print ('######STATUS REPORT#######\nThere are {4} Boxes matching the strings supplied: {0}\n{1}\nTagging all {4} Boxes with environment-name format: {2}: {3}\n\n'.format( (boxname[i]), matched_names, TagKey, TagValue, (len(matched_names)) ))
        i += 1

        # Run the function again, this time with list of matched names
lambda_handler(1,1)
