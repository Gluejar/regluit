So far, the vagrant/ansible setup is meant to build please.unglue.it on AWS.

For this script to work, you need to have AWS_ACCESS_KEY and AWS_SECRET_KEY environment variables set.
Run:

```
vagrant up --provider=aws
```

followed by

```
a-play-aws.sh unglueit.yml
```

I might not have removed all the dependencies on my own laptop yet for this setup.

Need to fill out host_vars/unglueit.template and copy it to hosts_vars/unglueit

