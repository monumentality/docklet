#!/bin/bash

function usage
{
cat <<EOF 
usage: ./etcd-multi-nodes.sh [[--discovery discovery_url] [--network_device eth1] [-h]]
discovery_url can be get by:
    curl -w "\n" 'https://discovery.etcd.io/new?size=2'
note: change the size of etcd cluster
EOF
}

[[ $# -eq 0 ]] && usage && exit 1
while [ "$1" != "" ]; do
    case $1 in
	-d | --discovery )      shift
				cluster_url=$1
				;;
	-n | --network_device ) shift
	                        network_device=$1
	                        ;;
	-h | --help )           usage
				exit
				;;
	* )                     usage
				exit 1
    esac
    shift
done

network_device=${network_device:-eth1}
echo $network_device
hostname=$(hostname)
hostip=$(ifconfig $network_device | grep "inet addr" | cut -d ':' -f 2 | cut -d ' ' -f 1)
# -initial-advertise-peer-urls  :  tell others what peer urls of me
# -listen-peer-urls             :  what peer urls of me

# -listen-client-urls           :  what client urls to listen
# -advertise-client-urls        :  tell others what client urls to listen of me

# -initial-cluster-state        :  new means join a new cluster; existing means join an existing cluster
#                               :  new not means clear 


etcd --name $hostname \
     --initial-advertise-peer-urls http://$hostip:2380 \
     --listen-peer-urls http://$hostip:2380 \
     --listen-client-urls http://$hostip:2379,http://127.0.0.1:2379 \
     --advertise-client-urls http://$hostip:2379 \
     --discovery $cluster_url \
     --initial-cluster-state new &
