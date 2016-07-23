#!/bin/bash
name=$1
sudo lxc-create -t ubuntu -n $name -- -r precise

tee /var/lib/lxc/$name/config <<EOF
# Common configuration
lxc.include = /usr/share/lxc/config/ubuntu.common.conf

# Container specific configuration
lxc.rootfs = /var/lib/lxc/$name/rootfs
lxc.rootfs.backend = dir
lxc.utsname = $name
lxc.arch = amd64

# Network configuration
lxc.network.type = empty
lxc.network.flags = up
EOF

sudo lxc-start -n $name -d
pid=$(lxc-info -n $name | grep 'PID' | cut -d ':' -f 2 |  tr -d '[[:space:]]')
sudo mkdir /var/run/netns
sudo ln -s /proc/$pid/ns/net /var/run/netns/$pid

tee /etc/cni/net.d/10-calico-frontend.conf <<EOF
{
    "name": "frontend",
    "type": "calico",
    "ipam": {
        "type": "calico-ipam"

    }

}
EOF

CNI_PATH=/opt/bin cnitool add frontend /var/run/netns/$pid
