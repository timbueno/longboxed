require 'vagrant-ansible'

Vagrant::Config.run do |config|
  config.vm.box     = "precise32"
  config.vm.box_url = "http://files.vagrantup.com/precise32.box"
  
  config.vm.customize ["modifyvm", :id, "--memory", "512"]

  # This is only necessary if your CPU does not support VT-x or you run virtualbox
  # inside virtualbox
  config.vm.customize ["modifyvm", :id, "--vtxvpid", "off"]

  # You can adjust this to the amount of CPUs your system has available
  config.vm.customize ["modifyvm", :id, "--cpus", "1"]

  # IP address of vagrant system
  config.vm.network :hostonly, "33.33.33.33"

  # Forward guest port 80 to host port 4567
  #config.vm.forward_port 80, 4567

  config.vm.provision :ansible do |ansible|
    # point Vagrant at the location of your playbook you want to run
    #ansible.playbook = "devops/setup_server.yml"
    ansible.playbook = "devops/deploy2.yml"

    # the Vagrant VM will be put in this host group change this should
    # match the host group in your playbook you want to test
    ansible.hosts = "webservers"
  end
end
