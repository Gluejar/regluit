**Instructions on how to run open_source branch**

To use vagrant/ansible to build the `{please|just|}.unglue.it`, you 
need to have the following installed:

* [Vagrant](https://www.vagrantup.com/docs/installation/) (e.g., to download: https://www.vagrantup.com/downloads.html) (at least version 1.8.1)
* [Installation — Ansible Documentation](http://docs.ansible.com/ansible/intro_installation.html#latest-releases-via-pip) (version 2+) -- use `pip install ansible`

We also need the `vagrant-aws vagrant plugin:


```
vagrant plugin install vagrant-aws --plugin-version 0.5.0
```

Optionally you can [VirtualBox – Oracle VM VirtualBox](https://www.virtualbox.org/wiki/VirtualBox) to enable the build of machines locally.


Layout of important files:

* [Vagrantfile](https://github.com/Gluejar/regluit/blob/1ac55c4f0a6b6a3dfc97652aa5ce33638a6140a1/vagrant/Vagrantfile), which is what `vagrant` looks for and defines various hosts: `please`, `just`, `just2`, `prod`, and `prod2`. 
* [dev.yml](https://github.com/Gluejar/regluit/blob/1ac55c4f0a6b6a3dfc97652aa5ce33638a6140a1/vagrant/dev.yml) -- the main ansible playbook that builds the various machines

* `please` is for buiding `please.unglue.it` -- it is a transient machine
* the reason I have a `just` *group* with `just` and `just2` hosts is while one is in production, I build the new one.  Once the new one is working, I can `vagrant stop` and then ultimately `vagrant destroy` the old one.
* similar logic for the production *group*. (Note that before I retire a production server, I copy over the logs to S3: [backing up production logs to S3](https://www.evernote.com/shard/s1/sh/f12406a7-de95-4d54-809d-9f3abe8eaabd/f935e813d8f16f25))


You also need AWS keys in the environment.  I have my key/secret pair configured with a shell script that I can run -- I've stored this file in `/Volumes/ryvault1/gluejar/other_keys/aws.sh`, stored in an encrypted volume on my laptop.  For convenience I link to the file from `~/bin/gj_aws.sh`:

```
#!/bin/bash
export BOTO_CONFIG=/Volumes/ryvault1/gluejar/other_keys/boto.cfg

# rdhyee key: https://console.aws.amazon.com/iam/home?region=us-east-1#/users/rdhyee
# eric: you can use the credentials from https://console.aws.amazon.com/iam/home?region=us-east-1#/users/eric
# note:  these credentials are tied to the Gluejar account

export AWS_ACCESS_KEY=[FILL IN]
export AWS_SECRET_KEY=[FILL IN]

# simple_public_vpc
export AWS_VPC_ID=vpc-6f7db10b

# EC2 API tools
export EC2_ACCESS_KEY=$AWS_ACCESS_KEY
export EC2_SECRET_KEY=$AWS_SECRET_KEY

# s3cmd
ln -fs /Volumes/ryvault1/gluejar/s3/s3cfg  ~/.s3cfg

export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_KEY

# AWS CLI http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_KEY
# http://docs.aws.amazon.com/cli/latest/userguide/controlling-output.html
export AWS_DEFAULT_OUTPUT="json"

```

e.g.,

```
hyptyposis-2014:vagrant raymondyee$ ls -lt ~/bin/gj_aws.sh
lrwxr-xr-x  1 raymondyee  501  43 Aug 18  2014 /Users/raymondyee/bin/gj_aws.sh -> /Volumes/ryvault1/gluejar/other_keys/aws.sh
```

In the `regluit/vagrant` directory, after I run `~/bin/gj_aws.sh` and  `vagrant status`, I get something like (the actual status of various machines can vary):

```
please                    not created (virtualbox)
just                      running (aws)
just2                     not created (virtualbox)
prod                      not created (virtualbox)
prod2                     running (aws)
localvm                   not created (virtualbox)
```

Once you have `vagrant status` works, a good place to start is how to build `please` with

```
vagrant up please --provider=aws
```

**For the moment, please leave building just and production to me.**

## running regluit on localhost

In the `vagrant` directory, you can run 

```
ansible-playbook create_commonpy.yml
```

to generate `settings/common.py`.  You should then be able to proceed as normal.  