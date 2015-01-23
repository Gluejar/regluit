This directory is for [ansible](http://www.ansible.com/home) playbooks for sysadmin tasks around unglue.it.

We start with automating tasks such as [applying security upgrades](unattended-upgrade.yml) to the servers.

Goal is to build playbooks for the configuration of servers.

# Current status of playbooks

* [host](hosts) is currently written by hand -- the inventory might be dynamically generated at some point.


# Installing ansible

[installation instructions](http://docs.ansible.com/intro_installation.html).

On the mac, easiest approach is probably to use [homebrew](http://brew.sh/):

    brew install ansible
    
You can also use `pip`:

    pip install ansible
    
Note: ansible depends on one having ssh access to the servers.


# Running unattended-upgrade

in `regluit/sysadmin/playbooks`, run

    ansible-playbook -i hosts -e "target=instances" unattended-upgrade.yml
    
to run on all the servers.

    ansible-playbook -i hosts unattended-upgrade.yml
    
will run only just.

