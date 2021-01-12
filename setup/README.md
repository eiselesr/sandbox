Steps to set up new computer

1. install bitwarden
1. host is xubuntu
    1. turn off alt-tab(cycle windows) in windows manager 
1. client is xubuntu
    1. turn on `super` to open start menu 
        1. keyboard menu
        1. add `xfce4-popup-whiskermenu`
        1. press desired key
1. setup github private/public key
1. 'git clone git@github.com:eiselesr/sandbox.git'
1. install jetbrains toolbox
	1. https://account.jetbrains.com/licenses
	1. https://www.jetbrains.com/toolbox-app
	1. downlowd
	1. `tar -xvf <toolbox.tar.gz>
	1. execute
1. open toolbox and install pycharm
1. 'git clone git@github.com:TransactiveSCC/TRANSAX.git'

1. install tmux
    1. `sudo apt install tmux`

1. install docker
    1. curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    1. `sudo add-apt-repository \ "deb [arch=amd64] https://download.docker.com/linux/ubuntu \    $(lsb_release -cs) \    stable"`  
    1. `sudo apt-get update`
    1. `sudo apt-get install docker-ce docker-ce-cli containerd.io`
    1. `sudo groupadd docker`
    1. `sudo usermod -aG docker $USER`
    1. `newgrp docker`
1. install docker-compose (https://docs.docker.com/compose/install/)
    1. `sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose`
    1. `sudo chmod +x /usr/local/bin/docker-compose`
    1. test: `docker-compose --version`

1. setup git public/private keys
1. current repos
    1. `git clone git@github.com:eiselesr/sandbox.git`
    1. `git clone git@github.com:RIAPS/riaps-apps.git`
    1. 

