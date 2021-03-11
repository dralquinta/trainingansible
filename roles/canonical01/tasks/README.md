# lnx_static_wls_122/tasks



The following directory contains the playbook pieces required during the configuration of a **WebLogic Server 12.2.x Domain**



| File                         | Description                                                  |
| ---------------------------- | ------------------------------------------------------------ |
| `main.yaml`                  | Main playbook orchestrator. This file will call all the required configuration pieces in adequate order to configure a domain end-to-end. For more details, refer to section [main.yaml](##main.yaml) |
| `post_exec.yaml`             | Performs housekeeping of the machines related to the configuration. This includes the temporarily stage and cert directories which are no longer needed after configuration finishes. For more details, refer to the section [post_exec.yaml](##post_exec.yaml) |
| `pre_exec.yaml`              | Generates all required pre-condition checks for domain configuration. For more details, refer to the section [pre_exec.yaml](pre_exec.yaml) |
| `README.md`                  | This file                                                    |
| `wls_domain_config.yaml`     | Contains the steps required for end-to-end domain configuration. For more details, refer to the section [wls_domain_config.yaml](##wls_domain_config.yaml) |
| `wls_domain_creation.yaml`   | Contains the steps required for end-to-end domain creation. For more details, refer to the section [wls_domain_creation.yaml](##wls_domain_creation.yaml) |
| `wls_domain_nfs_config.yaml` | Contains the steps required to generate the NFS Configuration of the NFS volumes required by the domain. For more details, refer to the section [wls_domain_nfs_config.yaml](##wls_domain_nfs_config.yaml) |



## main.yaml

The following is the file structure of `main.yaml`

```yaml
---
#
# Author: DALQUINT - denny.alquinta@oracle.com
# Purpose: lnx_static_wls_122 orchestrator yaml file

# Copyright (c) 2021, Oracle and/or its affiliates. All rights reserved.
#

- include: tasks/pre_exec.yaml

- name: Tasks for Configuring Domain
  include_tasks: tasks/wls_domain_creation.yaml  
  when: (ansible_facts['distribution'] == "OracleLinux" and ansible_facts['distribution_major_version'] == "7") 

- name: Tasks for Configuring NFS Filesystem
  include_tasks: tasks/wls_domain_nfs_config.yaml  
  when: (ansible_facts['distribution'] == "OracleLinux" and ansible_facts['distribution_major_version'] == "7") 

- name: Tasks for Finalize Domain and Domain configuration
  include_tasks: tasks/wls_domain_config.yaml  
  when: (ansible_facts['distribution'] == "OracleLinux" and ansible_facts['distribution_major_version'] == "7") 
 
- include: tasks/post_exec.yaml
```



This file will orchestrate the playbook in the following order: 

- `pre_exec.yaml` to apply pre-condition checks on role.
- `wls_domain_creation.yaml` to create the domain.
- `wls_domain_nfs_config.yaml` to configure NFS volumes related to domain.
- `wls_domain_config.yaml` to apply specific domain configurations accordingly to use cases defined.
- `post_exec.yaml` to apply post-condition tasks such as house keeping inside machines.

**IMPORTANT:** All of these tasks will be included only under supported *OracleLinux OS*, which by this case is limited to *OEL7.x*



## pre_exec.yaml

The following files includes the required steps to do Pre-Execution check on the domain. This will register two variables, to see if the domain has been already created and configured and will interchange the required private and public keys so that the machines can interchange files upon creation and configuration stage. 

In order to determine if the domain has been already created, the pre-check condition will see if the file `startWebLogic.sh` is present under `$DOMAIN_HOME` in each machine. If so, this variable will register true

In order to determine if the domain has been already configured, the pre-check condition will poll for file `jaas.config` inside machine filesystem structure. This file should only appear on late configuration stages, so it serves as a marker for such condition. 



## post_exec.yaml

The following file will execute a set of tasks oriented to perform machine housekeeping of files and directories used during the creation and configuration. To understand more of it's behavior, check the self documented steps on `post_exec.yaml`



## wls_domain_config.yaml

The following file includes all the tasks required to configure a domain. Based on the pre-condition check ran in `pre_exec.yaml`, this playbook will behave as an idempotent entity, meaning that running the role again after it's first configured, will not change it's current status. To understand more of it's behavior, check the self documented steps on `wls_domain_config.yaml` 



## wls_domain_creation.yaml

The following file includes all the tasks required to create a domain. Based on the pre-condition check ran in `pre_exec.yaml`, this playbook will behave as an idempotent entity, meaning that running the role again after it's first configured, will not trigger another domain creation, but it'll immediately skip it's execution. The domain is created using the best practices of [Optimal Flexible Architecture](https://docs.oracle.com/en/database/oracle/oracle-database/12.2/ssdbi/optimal-flexible-architecture-file-path-examples.html#GUID-BB3EE4F7-50F4-4A2D-8A0D-96B7CC44029B) and the [Enterprise Deployment Guide](https://docs.oracle.com/middleware/1221/core/SOEDG/toc.htm). To understand more of it's behavior, check the self documented steps on `wls_domain_creation.yaml`



## wls_domain_nfs_config.yaml

The following file includes all the required tasks to mount the *NFS FSS* provisioned for the domain. Each domain will use 3 *NFS Filesystems*, which are oriented for OFA Logs, Application Home for non-stage deployments and directory named `/u01/escritura` related to *SURA* specific domain configuration. this playbook will behave as an idempotent entity, meaning that running the role again after it's first configured, will not trigger another NFS disk configuration, but it'll immediately skip it's execution. To understand more of it's behavior, check the self documented steps on `wls_domain_nfs_config.yaml`



------
The following code is protected using Oracle Technology Network License Agreement. For more details, please refer to the project's OEM [LICENSE](../../../LICENSE)  file.



**Copyright (c) 2021, Oracle, Oracle Advanced Customer Services and/or its affiliates. All rights reserved.**

