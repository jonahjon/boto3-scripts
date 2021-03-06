import sys
import boto.vpc

AWS_TARGET_REGION = 'us-east-1'
SOURCE_ROUTE_TABLE_ID = 'rt-xxxxxxx'
ROUTE_STATE_CREATED = 'CreateRoute'

# This Script copys your route table, and turns it into an AWS CLI command for another regoion!

def exit_error(message):
	sys.stderr.write('Error: {0}\n'.format(message))
	sys.exit(1)

def get_route_table_route_list(vpc_conn):
	route_table_list = vpc_conn.get_all_route_tables([SOURCE_ROUTE_TABLE_ID])

	route_table_item = None
	for route_table_check in route_table_list:
		if (route_table_check.id is not None):
			route_table_item = route_table_check
			break
	if (route_table_item is None):
		exit_error('Unable to locate route table {0}'.format(SOURCE_ROUTE_TABLE_ID))

	# return route table VPC ID and route list
	return route_table_item.vpc_id,route_table_item.routes

def generate_awscli_commands(vpc_id,route_list):
	# command to create a new route table
	print(
		'routeTableID=$(aws ec2 create-route-table --region {0} --vpc-id {1} --output text | grep "^ROUTETABLE" | cut -f2)\n' \
		'echo "Route table: $routeTableID"\n'.format(
			AWS_TARGET_REGION,
			vpc_id
	))

	# commands to create routes for route table
	for route_item in route_list:
		# ensure route has been explicitly created and has a CIDR block
		if (
			(route_item.origin != ROUTE_STATE_CREATED) or
			(route_item.destination_cidr_block is None)
		):
			continue

		# get AWS CLI parameter type and value to re-create route
		route_type_param,route_value = get_awscli_route_type_param_value(route_item)
		if (route_type_param is None):
			# unable to create route type - skip
			continue

		print('aws ec2 create-route --region {0} --route-table-id $routeTableID --destination-cidr-block {1} --{2} {3}'.format(
			AWS_TARGET_REGION,
			route_item.destination_cidr_block,
			route_type_param,
			route_value
		))

def get_awscli_route_type_param_value(route_item):
	# Internet/virtual gateway
	if (route_item.gateway_id is not None):
		return 'gateway-id',route_item.gateway_id

	# network interface
	if (route_item.interface_id is not None):
		return 'network-interface-id',route_item.interface_id

	# VPC peering connection
	if (route_item.vpc_peering_connection_id is not None):
		return 'vpc-peering-connection-id',route_item.vpc_peering_connection_id

	# note: NAT Gateway (not currently implemented by boto)
	# if (route_item.XXXX is not None):
	# 	return 'nat-gateway-id',route_item.XXXX

	# skip route item
	return None,None

def main():
	# make connection to VPC
	vpc_conn = boto.vpc.connect_to_region(AWS_TARGET_REGION)

	# fetch route list for route table
	route_table_vpc_id,route_list = get_route_table_route_list(vpc_conn)

	# generate AWS CLI commands
	generate_awscli_commands(route_table_vpc_id,route_list)


if (__name__ == '__main__'):
	main()
