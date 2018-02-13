import boto.ec2
ec2 = boto.connect_ec2()
 
# Get all security groups
sgs = ec2.get_all_security_groups()
 
# Loop through all security groups
sglist = ''
for sg in sgs:
    # Get the instance count where the security group is attached
    sglen = len(sg.instances())
    # If the security group is not attached (0) it means it's not attached to an instance
    if sglen == 0 and sg.name != 'default':
        print sg.name, len(sg.instances())
        sglist = sglist + sg.name + '\n'

 
