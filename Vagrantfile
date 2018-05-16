# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.
  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "ubuntu/xenial64"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  config.vm.box_check_update = false

  # Setup specific for local machine
  config.vm.define "regluit-local", primary: true do |local|
    # Create a private network
    local.vm.network "private_network", type: "dhcp"
    local.vm.hostname = "regluit-local"

    # VirtuaLBox provider settings for running locally with Oracle VirtualBox
    # --uartmode1 disconnected is necessary to disable serial interface, which
    # is known to cause issues with Ubuntu 16 VM's
    local.vm.provider "virtualbox" do |vb|
      vb.name = "regluit-local"
      vb.memory = 1024
      vb.cpus = 2
      vb.customize [ "modifyvm", :id, "--uartmode1", "disconnected" ]
    end

  end

  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.synced_folder ".", "/opt/regluit"

  config.vm.network "forwarded_port", guest: 8000, host: 8000

  # Provision node with Ansible running on the Vagrant host
  # This requires you have Ansible installed locally
  # Vagrant autogenerates an ansible inventory file to use
  config.vm.provision "ansible_local" do |ansible|
    ansible.playbook = "/opt/regluit/provisioning/setup-regluit.yml"
    ansible.provisioning_path = "/opt/regluit"
    ansible.verbose = true
    ansible.install = true
  end

  config.vm.post_up_message = "Successfully created regluit-local VM. Run 'vagrant ssh' to log in and start the development server."

end
