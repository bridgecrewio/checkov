---
layout: default
published: true
title: Ansible configuration scanning
nav_order: 20
---

# Ansible configuration scanning
Checkov supports the evaluation of policies on your Ansible files.
When using checkov to scan a directory that contains Ansible tasks it will validate if the file is compliant with Ansible best practices such as validating certificates and using HTTPS to download files, and more.  

Full list of Ansible policies checks can be found [here](https://www.checkov.io/5.Policy%20Index/ansible.html).

### Example misconfigured Ansible file

```yaml
- name: Verify tests
  hosts: all
  gather_facts: False
  tasks:
    - name: disabled
      yum:
        name: httpd>=2.4
        state: present
        validate_certs: false
```
### Running in CLI

```bash
checkov -d . --framework ansible
```

### Example output
```bash
 
       _               _              
   ___| |__   ___  ___| | _______   __
  / __| '_ \ / _ \/ __| |/ / _ \ \ / /
 | (__| | | |  __/ (__|   < (_) \ V / 
  \___|_| |_|\___|\___|_|\_\___/ \_/  
                                      
By Prisma Cloud | version: x.x.x


ansible scan results:

Passed checks: 1, Failed checks: 1, Skipped checks: 0

Check: CKV_ANSIBLE_4: "Ensure that SSL validation isn't disabled with yum"
	PASSED for resource: task.disabled
	File: /site.yaml:6-12
Check: CKV_ANSIBLE_3: "Ensure that certificate validation isn't disabled with yum"
	FAILED for resource: task.disabled
	File: /site.yaml:6-12

		6  |     - name: disabled
		7  |       yum:
		8  |         name: httpd>=2.4
		9  |         state: present
		10 |         validate_certs: false
```
