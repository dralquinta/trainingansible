#!/bin/sh
#Author: DALQUINT - denny.alquinta@oracle.com
#Purpose: This script wrapper executes logic for getting output from terraform, then filling both ansible_hosts and playbook.yaml for corresponding role.
#Copyright (c) 2021, Oracle and/or its affiliates. All rights reserved. 

export STAGE=json_stage
export STATE_TERRAFORM_INIT="false"
cd $TERRAFORM_ARTIFACT_WORKSPACE
mkdir -p  $ANSIBLE_WORKSPACE/$STAGE

for (( k=1; k<=5; k++ ))
do  
    
    echo "--- Executing terraform init (pass $k of 5)" 
    terraform init
    if [ $? == 0 ]; then 
        STATE_TERRAFORM_INIT="true"
        break ; 
    fi

    echo "--- Error in terraform init. Retrying terraform init in 10 seconds."
    sleep 10
done


if [ ${STATE_TERRAFORM_INIT} == "false" ]; then
    echo "terraform init failed. Exiting with command 1"
    exit 1
fi

echo " --- Writing integration json files in $STAGE"
terraform output -json Admin_Compute &> $ANSIBLE_WORKSPACE/$STAGE/admin_compute.json
terraform output -json Cluster_Compute &> $ANSIBLE_WORKSPACE/$STAGE/managed_compute.json
terraform output -json Domain_Name &> $ANSIBLE_WORKSPACE/$STAGE/domain_name.json
terraform output -json Cluster_Name &>$ANSIBLE_WORKSPACE/$STAGE/cluster_name.json
terraform output -json Managed_Servers_Per_Machine &> $ANSIBLE_WORKSPACE/$STAGE/num_managed_servers.json
terraform output -json FOOBAR &> $ANSIBLE_WORKSPACE/$STAGE/foobar.json

python3 $ANSIBLE_WORKSPACE/get_host_vars.py