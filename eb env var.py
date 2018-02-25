import boto3
import pprint

client = boto3.client('elasticbeanstalk')


response = client.describe_environments()
#lists of env by variables
dvmencryptpwlist = ['qa-asy', 'qa-dataex', 'qa-dvmadmin', 'qa-paw', 'qa-practice']
jayencryptpwlist = ['qa-alloc', 'qa-integration', 'qa-orderintake', 'qa-wagx-docker']
serverlist = ['qa-async1', 'qa-sync2', 'qa-async3', 'qa-async4']
springproflist = ['qa-alloc', 'qa-integration', 'qa-orderintake', 'qa-wagx-docker', 'qa-refillapp-api','qa-rxtransfer']
jbocstring = ['qa-async1', 'qa-sync2', 'qa-async3', 'qa-async4','qa-alloc', 'qa-integration',
'qa-dataex', 'qa-dvmadmin', 'qa-paw', 'qa-practice', 'qa-pci', 'qa-refillapp', 'qa-rxtransfer']

#actual variables in dict we will be inserting
JDBC    = {	    'Namespace' : 'aws:elasticbeanstalk:application:environment',
				'OptionName' : 'JDBC_CONNECTION_STRING',
				'Value' : ''}

jaypwqa = {		'Namespace' : 'aws:elasticbeanstalk:application:environment',
				'OptionName' : 'jasypt.encryptor.password',
				'Value' : '9rollO464J590structUreD814disInterested?0beneDicK2boraTE4NuMerousnesS785NUtty7170caTHI13'}

dvmpwqa = {     'Namespace' : 'aws:elasticbeanstalk:application:environment',
				'OptionName' : 'dvm_encryption_password',
				'Value' : '9rollO464J590structUreD814disInterested?0beneDicK2boraTE4NuMerousnesS785NUtty7170caTHI13'}

vfcenvqa = {	'Namespace' : 'aws:elasticbeanstalk:application:environment',
				'OptionName' : 'VFC_ENV',
				'Value' : 'qa'}

springprofile =	{'Namespace' : 'aws:elasticbeanstalk:application:environment',
				'OptionName' : 'spring.profiles.active',
				'Value' : 'qa'}

async1 = {	    'Namespace' : 'aws:elasticbeanstalk:application:environment',
			    'OptionName' : 'queues.run'}

timezone = {	'Namespace' : 'aws:elasticbeanstalk:application:environment',
				'OptionName' : 'user.timezone',
				'Value' : 'UTC'}

GRADLE_HOME = {'Namespace' : 'aws:elasticbeanstalk:application:environment',
               'OptionName' : 'GRADLE_HOME', 'Value' : '/usr/local/gradle'}

JAVA_HOME = {'Namespace' : 'aws:elasticbeanstalk:application:environment',
             'OptionName' : 'JAVA_HOME', 'Value' : '/usr/lib/jvm/java'}

M2 =   {'Namespace' : 'aws:elasticbeanstalk:application:environment',
       'OptionName' : 'M2', 'Value' : '/usr/local/apache-maven/bin'}

M2_HOME = {'Namespace' : 'aws:elasticbeanstalk:application:environment',
           'OptionName' : 'M2_HOME', 'Value' : '/usr/local/apache-maven'}


pp = pprint.PrettyPrinter(depth=6)
allocation = {''}

#Finds the EnvironmentName variable in the Environment section, that start with 'dev'
#If the environment is in the list to get dvm-encrypt password it gets it
for enviroment in (response['Environments']):
	if (enviroment['EnvironmentName']).startswith('qa'):
        for enviroment in (response['Environments']):
    	    if (enviroment['EnvironmentName']).startswith(tuple(dvmencryptpwlist)):
                env = (enviroment['EnvironmentName'])
                rebuilding = client.update_environment(
                    EnvironmentName=env,
                    OptionSettings=[
                        dvmpwqa])
                #adding in Async queues.run variables
                for enviroment in (response['Environments']):
                    if (enviroment['EnvironmentName']).startswith(tuple(serverlist)):
                        env = (enviroment['EnvironmentName'])
                        #adding element to dict depending on async number
                        if env.endswith('1'):
                            async1['Value'] = '1'
                            rebuilding = client.update_environment(
                                EnvironmentName=env,
                                OptionSettings=[
                                    async1])
                        #same thing updaying dict for server 2 and adding in spring.profile logic
                        elif env.endswith('2'):
                            async1['Value'] = '2'
                            springprofile.update({'dvm-px-kafka-consume'})
                            rebuilding = client.update_environment(
                                EnvironmentName=env,
                                OptionSettings=[
                                    async1, springprofile]])
                        elif env.endswith('3'):
                            async1['Value'] = '3'
                            springprofile.update({'Value': 'dvm-quartz'})
                            rebuilding = client.update_environment(
                                EnvironmentName=env,
                                OptionSettings=[
                                    async1, springprofile])
                        # and finally 4 although this one says 3 online o well
                        else env.endswith('4'):
                            async1['Value'] = '3'
                            rebuilding = client.update_environment(
                                EnvironmentName=env,
                                OptionSettings=[
                                async1])
            # Now adding in jasypt encryptor password / and 
            # spring.profile except for the snowflake(integration)
    	    elif (enviroment['EnvironmentName']).startswith(tuple(jayencryptpwlist)):
                env = (enviroment['EnvironmentName'])
                rebuilding = client.update_environment(
                    EnvironmentName=env,
                    OptionSettings=[
                        jaypwqa, springprofile ])
                #Adding update on springprofile for qa-intergration with cognito
                for enviroment in (response['Environments']):
            	    if (enviroment['EnvironmentName']).startswith('qa-integration-ads'):
                    env = (enviroment['EnvironmentName'])
                        springprofile.update({'Value': 'qa,cognitoauth'})
                        rebuilding = client.update_environment(
                            EnvironmentName=env,
                            OptionSettings=[
                                springprofile ])
                #adding in snowflake jaysp password and timezone var
                for enviroment in (response['Environments']):
                	if (enviroment['EnvironmentName']).startswith('qa-rxtransfer'):
                    env = (enviroment['EnvironmentName'])
                        jaypwqa.update({'Value': 'TheOtherGuysQA'})
                        rebuilding = client.update_environment(
                            EnvironmentName=env,
                            OptionSettings=[
                                jaypwqa, timezone ])
            # only exception of env that needs spring profile without jayspt pw
            else (enviroment['EnvironmentName']).startswith('qa-refillapp-api'):
                env = (enviroment['EnvironmentName'])
                rebuilding = client.update_environment(
                    EnvironmentName=env,
                    OptionSettings=[
                        springprofile ])
            # adding in JDBC_Connection_String whatever that is since there is no value
    	    if (enviroment['EnvironmentName']).startswith(tuple(jbocstring)):
                env = (enviroment['EnvironmentName'])
                rebuilding = client.update_environment(
                    EnvironmentName=env,
                    OptionSettings=[
                        jbocstring ])
            #Super special snowflae of qa-pps
            if(enviroment['EnvironmentName']).startswith('qa-pps'):
            env = (enviroment['EnvironmentName'])
            rebuilding = client.update_environment(
                EnvironmentName=env,
                OptionSettings=[
                    GRADLE_HOME, JAVA_HOME, M2, M2_HOME
                        ])





                        
           # if (rebuilding['ResponseMetadata']['HTTPStatusCode']) == 200:
                #print (env + ' success')
            #else:
                #print (env + ' failure')