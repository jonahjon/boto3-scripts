import boto3
import pprint

#This script will list all beanstalk enviroments filtered by certain keywords 'dev', 'stage' 'qa', and you can programmatically
#apply changes or rebuild in a fashion with a success/failure on each one. This is useful when updating cloudformation stacks
#They often times will update but won't apply changes to beanstalk enviorments unless they are rebuilt. I built this
#For a project when updating ELB cipher SSL protocols, they didn't automagically apply until each env was rebuilt.

client = boto3.client('elasticbeanstalk')

response = client.describe_environments()

pp = pprint.PrettyPrinter(depth=6)

#Finds the EnvironmentName variable in the Environment section, that start with 'dev'
#You could change the rebuild to boto3 optionset, for programmable changesets.

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


