#Author: DALQUINT - denny.alquinta@oracle.com
#Purpose: This script constructs the ansible_hosts file with all required for OSB provisioning
#Copyright (c) 2021, Oracle and/or its affiliates. All rights reserved. 

import json
from json.decoder import JSONDecodeError
import os
import datetime
import re
import sys
import shutil
import socket
import ipaddress

# Static initialized variables. DO NOT TOUCH
an_workspace = os.environ['ANSIBLE_WORKSPACE']
tf_workspace = os.environ['TERRAFORM_ARTIFACT_WORKSPACE']
stage = os.environ['STAGE']
environment = os.environ['PIPELINE']
#try/catch block for variables that should come from setEnv.sh
try:
	machine_base_role = os.environ['ANSIBLE_BASE_ROLE']
except KeyError:
	print()

stage_home = an_workspace+'/'+stage
all_hosts = 'machines'
admin_hosts = 'admin'
managed_hosts = 'managed'
num_admin_compute_instances = 0
num_managed_compute_instances = 0
num_all_compute_instances = 0
#Defines files to be written for integration. Do not touch
ansible_hosts_file = open(an_workspace+'/ansible_hosts','w')
playbook_yaml_file = open(an_workspace+'/playbook.yaml','w')




#Helper functions

def isVarNull(var):	
	if var is None:
		return True
	else:
		return False

def isVarEmpty(var):	
	if var == "":
		return True
	else:
		return False

def validateJson(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True


def getJsonData(jsonFile):
	try:
		json_out = open(stage_home+'/'+jsonFile)
		text = json_out.read()
		if validateJson(text) == True:
			json_out.close()
			return json.loads(text)
	except JSONDecodeError:
		print()

def getJsonText(jsonFile):
	json_out = open(stage_home+'/'+jsonFile)
	text = json_out.read()
	json_out.close()
	return text

def print_with_date(message):
	print('['+ str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + '] '+ message)

def DEBUG(message):
	print("----DEBUG:  "+str(message))
	

##### HEADER WRITERS #####
def admin_header():
	ansible_hosts_file.write("\n\n["+admin_hosts+"]\n")

def managed_header():
	ansible_hosts_file.write("\n\n["+managed_hosts+"]\n")

def all_hosts_header():
	ansible_hosts_file.write("\n\n["+all_hosts+"]\n")


def housekeeping():
	shutil.rmtree(stage_home)
	playbook_yaml_file.close()
	ansible_hosts_file.close()


##### ANSIBLE_HOST WRITERS #####

def write_ansible_hosts_file():	
	print_with_date('Writing Compute Information from json file')	 
	if validateJson(getJsonText('admin_compute.json')) == True:
		admin_header()	
		admin_info()
		host_vars(admin_hosts)
	
	if validateJson(getJsonText('managed_compute.json')) == True:
		managed_header()
		managed_info()
		host_vars(managed_hosts)
	
	if validateJson(getJsonText('admin_compute.json')) == True and validateJson(getJsonText('managed_compute.json')) == True:
		all_hosts_header()
		admin_info()
		managed_info()
		host_vars(all_hosts)

def get_single_value_from_json(json_file):
	if validateJson(getJsonText(json_file)) == True:
		file = open(stage_home+'/'+json_file,'r')
		value = file.readline().replace('"',"")
		file.close()
		return value


def admin_info():		
	print_with_date('Writing Admin Server Compute Coordinates')
	data_compute = getJsonData('admin_compute.json')
	for value in data_compute:
		ansible_hosts_file.write("\t"+value['hostname_label']+" ansible_ssh_host="+value['private_ip']+" ansible_ssh_port=22 ansible_ssh_user=opc"+"\n")						


def managed_info():	
	
	print_with_date('Writing Managed Server Compute Coordinates')
	if validateJson(getJsonText('managed_compute.json')) == True:	
		data_compute = getJsonData('managed_compute.json')
		for value in data_compute:
			ansible_hosts_file.write("\t"+value['hostname_label']+" ansible_ssh_host="+value['private_ip']+" ansible_ssh_port=22 ansible_ssh_user=opc"+"\n")					

def get_num_compute():
	global num_managed_compute_instances
	print_with_date('Saving num_compute_instances')			
	if validateJson(getJsonText('managed_compute.json')) == True:	
		data_compute = getJsonData('managed_compute.json')
		for value in data_compute:		
			num_managed_compute_instances = num_managed_compute_instances + 1
			
	num_compute_instances = num_managed_compute_instances +1
	return num_compute_instances

def host_vars(host_group):
	print_with_date('Writing Compute common variables for host group: '+host_group)	
	ansible_hosts_file.write("\n\n["+host_group+":vars]\n")
	ansible_hosts_file.write("\tansible_ssh_private_key_file = /home/opc/.ssh/id_rsa\n")		
	ansible_hosts_file.write("\tdomain_name = "+get_single_value_from_json('domain_name.json'))	
	ansible_hosts_file.write("\tcluster_name = "+get_single_value_from_json('cluster_name.json'))
	num_managed_svrs = get_single_value_from_json('num_managed_servers.json')
	ansible_hosts_file.write("\tms_per_machine = "+num_managed_svrs)
	if host_group == all_hosts:
		num_compute_instances = str(get_num_compute()) 		
		ansible_hosts_file.write("\tnum_compute_instances = "+num_compute_instances+"\n")
		num_compute_instances=str(int(num_compute_instances)-1)
		ansible_hosts_file.write("\ttotal_managed_servers = "+str(int(num_managed_svrs) * int(num_compute_instances))+"\n")


def write_machines_info():
	try:
		if isVarEmpty(machine_base_role) == False:
			print_with_date("Writing ansible_host main tag for hosts")					
			write_ansible_hosts_file()
	except NameError:
		print()


def write_playbook_yaml():
	playbook_yaml_file.write("---\n")
	#Add network logic for machines:
	try:	
		if isVarEmpty(machine_base_role) == False :
			playbook_yaml_file.write("\n")				
			playbook_yaml_file.write("- hosts: "+all_hosts+"\n")
			playbook_yaml_file.write("  roles:\n")
			playbook_yaml_file.write("   - "+machine_base_role)
			playbook_yaml_file.write("\n")
	except NameError:
		print()	

def main():
	write_machines_info()
	write_playbook_yaml()	
	housekeeping()


main()