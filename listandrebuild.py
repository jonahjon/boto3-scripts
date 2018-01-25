import boto3
import pprint

client = boto3.client('elasticbeanstalk')

response = client.describe_environments()

pp = pprint.PrettyPrinter(depth=6)

#Finds the EnvironmentName variable in the Environment section, that start with 'dev'
for enviroment in (response['Environments']):
	if (enviroment['EnvironmentName']).startswith('dev'):
		#pp.pprint(enviroment['EnvironmentName'])
		env = (enviroment['EnvironmentName'])
		rebuilding = client.rebuild_environment(
			EnvironmentName=env
		)
		if (rebuilding['ResponseMetadata']['HTTPStatusCode']) == 200:
			print (env + ' success')
		else:
			print (env + ' failure')


