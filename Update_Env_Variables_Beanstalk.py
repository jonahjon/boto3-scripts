import boto3
import pprint

client = boto3.client('elasticbeanstalk')


response = client.describe_environments()
#lists of env by variables
example-variables-env1  = ['app1', 'app2', 'app3']
example-variables-env2 = ['app1', 'app2', 'app4' ]


#actual variables in dict we will be inserting
Var1    = {	    'Namespace' : 'aws:elasticbeanstalk:application:environment',
				'OptionName' : 'JAVA-CONNECTION-PROFLE,
				'Value' : 'TEST'}

Var2 = {		'Namespace' : 'aws:elasticbeanstalk:application:environment',
				'OptionName' : 'exampleDBpassword',
				'Value' : 'P@$$W0rd' }


pp = pprint.PrettyPrinter(depth=6)

#Finds the EnvironmentName variable in the Environment section, that start with 'dev'
#If the environment is in the list to get dvm-encrypt password it gets it
for enviroment in (response['Environments']):
	if (enviroment['EnvironmentName']).startswith('app'):
        for enviroment in (response['Environments']):
    	    if (enviroment['EnvironmentName']).startswith(tuple(example-variables-env1)):
                env = (enviroment['EnvironmentName'])
                rebuilding = client.update_environment(
                    EnvironmentName=env,
                    OptionSettings=[
                        Var1])
    	    else (enviroment['EnvironmentName']).startswith(tuple(example-variables-env2)):
                env = (enviroment['EnvironmentName'])
                rebuilding = client.update_environment(
                    EnvironmentName=env,
                    OptionSettings=[
                        Var2])
            #code to see results of update  
            #if (rebuilding['ResponseMetadata']['HTTPStatusCode']) == 200:
                #print (env + ' success')
            #else:
                #print (env + ' failure')


                
            #HELPFUL THINGS

            #For snowflakes use a nested if statement and use the dict.update feature
            # Var1.update({'Value': 'NEWPASSWORD'})

            #.starts with is great but if you have app1, app2, app3 you can use .endswith for loops
