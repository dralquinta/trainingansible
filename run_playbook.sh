#!/bin/sh
#Author: DALQUINT - denny.alquinta@oracle.com
#Purpose: This script wrapper executes ansible with embedded playbook.yaml created by integration
#Copyright (c) 2021, Oracle and/or its affiliates. All rights reserved. 
echo "--- Executing playbook"

ansible-playbook playbook.yaml 