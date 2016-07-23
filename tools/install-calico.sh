#!/bin/bash
mkdir -p /opt/bin
mkdir -p /etc/cni/net.d
wget -N -O /opt/bin/calicoctl http://www.projectcalico.org/builds/calicoctl
wget -N -P /etc/cni/net.d https://github.com/projectcalico/calico-cni/releases/download/v1.0.2/calico
chmod a+w -R /etc/cni/net.d
chmod +x /etc/cni/net.d/calico
chmod +x /opt/bin/calicoctl
wget -P /opt/bin/ https://github.com/containernetworking/cni/releases/download/v0.3.0/cni-v0.3.0.tgz
tar -xf /opt/bin/cni-v0.3.0.tgz -C /opt/bin/
export PATH=$PATH:/opt/bin

sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
sudo apt-get install -y docker-engine
