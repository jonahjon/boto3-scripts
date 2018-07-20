# This writes a specific format we use in our CF templates, restructure if you wish

# Given the ID of an Amazon public AMI in one region, figure out what the
# equivalent AMI IDs are for that same AMI in all other regions known.
# If that AMI isn't defined in a region, it prints the region's name, but
# comments it out.


from __future__ import print_function
import boto3
import datetime


# This is "amzn-ami-hvm-2017.09.01
BASEAMIs= [ "ami-5583d42f" ]
BASEREGION="us-east-1"

# List all regions
client = boto3.client('ec2', region_name=BASEREGION)
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]

ec2 = boto3.resource('ec2', region_name=BASEREGION)

i = 0
target_image = {}
name_filter  = {}
for aminame in BASEAMIs:
    # Figure out what the AWS Name is for this image.
    # AMI filter
    image_filter = [{'Name':'image-id', 'Values':[BASEAMIs[i]]}]
    image_names = list(ec2.images.filter(Filters=image_filter).all())
    if( len(image_names) != 1 ):
        print( "ERROR: ", len(image_names), "matched", BASEAMIs[i])
        exit( 1 )
    target_image[i] = image_names[0].name
    # name-based filter
    name_filter[i] = [{'Name':'name', 'Values': [target_image[i]] }]
    i = i+1

# Print the lines in our cloudformation syntax
today = datetime.date.today()
print( '    "AmazonLinux"' + str(today) + " : {" )

# For every region, look up the AMI ID for that region by looking for
# the image with the same name.
for r in regions:
    ec2 = boto3.resource('ec2', region_name=r)
    i=0
    space = ' '
    print( '      "' + r + '"' + " " + ': { "64HVMGP2" : "' + image_names[0].id + '"')
    while (i < len(target_image.keys()) ):
        image_names = list(ec2.images.filter(Filters=name_filter[i]).all())
        if( len(image_names) != 1 ):
            print( '#  {} undefined'.format(r) ) 
        i=i+1
