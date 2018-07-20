import boto3
from prettytable import PrettyTable

def lambda_handler(event, context):
    region_list = ['eu-west-1', 'eu-central-1', 'us-east-1', 'us-west-1', 'us-west-2', 'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'sa-east-1']

    whitelist = [ 'Boxes_That_Should_Be_Public' ]

    InstanceSecurityGroupList =[]
    client = boto3.client('ec2')
    
    # this will include all EC2 names found with Open cidr ranges
    namelist = []

    report = PrettyTable(['port', 'protocol', 'Env', 'Name'])

    for Ec2Instance in client.describe_instances()['Reservations']:

        del InstanceSecurityGroupList[:]

        # check if it's public
        if Ec2Instance['Instances'][0]['PublicDnsName'] != '':
            
            # if public get it's groups
            for SecurityGroupId in Ec2Instance['Instances'][0]['SecurityGroups']:
                InstanceSecurityGroupList.append(SecurityGroupId['GroupId'])

            for IpPermission in client.describe_security_groups(GroupIds=InstanceSecurityGroupList)['SecurityGroups'][0]['IpPermissions']:

                for IPRange in IpPermission['IpRanges']:

                    # check if range is open to the werld
                    if IPRange['CidrIp'] == '0.0.0.0/0':

                        # check all the tags on the instance
                        for TagDocument in Ec2Instance['Instances'][0]['Tags']:
                            if TagDocument['Key'] == 'Name':
                                Ec2Name = TagDocument['Value']

                            # figure out the environment if it is not tagged
                            if TagDocument['Key'] == 'aws:cloudformation:stack-name':
                                Stackname = TagDocument['Value']
                                EnvironmentList = Stackname.split("-")
                                if EnvironmentList[1] == 'e':
                                    ppslist = Ec2Name.split("-")
                                    EnvironmentnonVar = ppslist[0]
                                else:
                                    EnvironmentnonVar = EnvironmentList[1]

                                try:
                                    Environment = TagDocument.get('stack', EnvironmentnonVar)
                                except KeyError:
                                    # Key is not present
                                    pass

                        if Ec2Name not in whitelist:
                            report.add_row([IpPermission['FromPort'], IpPermission['IpProtocol'], Environment, Ec2Name])

    report.align = "c"
    str1 = report.get_string(sortby="port")
                        
    client = boto3.client('ses', region_name='us-east-1') #Choose which region you want to use SES

    response = client.send_email(
        Source='blah@blah.com',
        Destination={
            'ToAddresses':  ['blah@blah.com'
            ]
        },
        Message={
            'Subject': {
            'Data': 'Open Instances to the World!'
        },
        'Body': {
            'Text': {
                'Data': str1,
                "Charset": "UTF-8"
            }
        }
    
        }
    )

lambda_handler(1,1)