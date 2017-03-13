# coding=UTF-8
#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import math
import random
import numpy as np
from mdkp import Colony
from dmachine import AllocationOfMachine
import heapq
from dconnection import *
import time
import _thread
import logging
import json
import jsonpickle

from log import slogger

#import log

machine_queue = []

# only used for test
task_requests = {}

tasks = {}

machines = {}

restricted_index = 0

node_manager = None

etcdclient = None

def generate_test_data(cpu,mem,machines,type,id_base):
    task_requests = {}
#    cpus = np.random.binomial(test_cpus, test_cpus/16, test_cpus*2)
#    mems = np.random.binomial(test_mems, test_mems/16, test_mems*2)
    cpu_arr = np.random.uniform(1,cpu,cpu*machines)
    mem_arr = np.random.uniform(1,mem,cpu*machines)
    bids = np.random.uniform(1,100,cpu*machines)
    for i in range(0+id_base,cpu*machines):
        if cpu_arr[i]==0 or mem_arr[i] ==0:
            continue

        task = {
            'id': str(i),
            'cpus': str(int(math.floor(cpu_arr[i]))),
            'mems': str(int(math.floor(mem_arr[i]))),
            'bid': str(int(bids[i]))
        }
        key = str(i)
        task_requests[key] = task

    # write to a file
#    with open('uniform_tasks.txt','w') as f:
#        for key, task in tasks.items():
#            f.write(str(task['cpus'])+' '+str(task['mems'])+' '+str(task['bid'])+'\n')

    return task_requests

def parse_test_data(filename,cpus,mems,machines):
    global tasks
    with open(filename,'r') as f:
        i =0
        for line in f.readlines()[0:cpus*machines]:
            arr = line.split()
            task = {
                'id': str(i),
                'cpus': float(arr[0]),
                'mems': float(arr[1]),
                'bid': int(arr[2])
            }
            key = str(i)
            task_requests[key] = task
            i+=1
            print(task)


def add_machine(id, cpus=24, mems=240000):
    global machines
    global machine_queue

    machine = AllocationOfMachine(id, cpus, mems)

    machines[id] = machine
    heapq.heappush(machine_queue,machine)

    # to-do:改成多线程，直接运行每个线程
    # machine.colony.run()
    send_colony("create",machine.machineid, str(machine.reliable_cpus), str(machine.reliable_mems))
    sync_colony()

    # save_machine in etcd
    save_machine(machine)
    return machine

def pre_allocate(task):
    global restricted_index

    if 'bid' in task and task['bid']!='0':
        machine = heapq.heappop(machine_queue)

        task['machineid'] = machine.machineid
        
        task['allocation_type'] = 'none'
        task['allocation_cpus'] = str(int(task['cpus'])*1000)
        task['allocation_mems'] = task['mems']
        task['allocation_mems_sw'] = str( 2 * int(task['mems']) )
        task['allocation_mems_soft'] = str( 2 * int(task['mems']) )
        tasks[task['id']] = task
        
        machine.total_value += int(task['bid'])
        heapq.heappush(machine_queue,machine)
        # save machine and task
        save_machine(machine)
        save_task(task)
    else:
        if(restricted_index >= len(machines)):
            restricted_index = 0

        slogger.debug("restricted_index: ", restricted_index)
        values = list(machines.values())
        task['machineid'] = values[restricted_index].machineid

        restricted_index += 1
        
        task['allocation_type'] = 'none'
        task['allocation_cpus'] = str(int(task['cpus'])*1000)
        task['allocation_mems'] = task['mems']
        task['allocation_mems_sw'] = str( 2 * int(task['mems']) )
        task['allocation_memsp_soft'] = str( 2 * int(task['mems']) )
        
        tasks[task['id']] = task
        # save task
        save_task(task)
    return task



def allocate(id):
    task = tasks[id]
    machineid = task['machineid']
    machine = machines[machineid]
    if 'bid' in task and task['bid']!='0':
        #    slogger.debug("dispatch reliable")
        task = machine.add_reliable_task(task)
        # save task and machine
        save_task(task)
        save_machine(machine)
        #    slogger.debug("pop machine: id = %s", machine.machineid)
        send_task(machine,task,"add")

    else:
        #    slogger.debug("dispatch restricted")
        task = machine.add_restricted_task(task)
        # save task and machine
        save_task(task)
        save_machine(machine)
    return task

def release(id):
    task = tasks[id]
    machineid = tasks[id]['machineid']
    machine = machines[machineid]
    if 'bid' in task and task['bid']!='0':
        slogger.debug("release reliable")
        machine.release_reliable_task(id)
        send_task(machine,task,'delete')
    else:
        slogger.debug("release restricted")
        machine.release_restricted_task(id)

def after_release(id):
    task = tasks[id]
    for index,machine in enumerate(machine_queue):
        if task['machineid'] == machine.machineid:
            del machine_queue[index]
            break

    machine.total_value -= int(task['bid'])
    heapq.heappush(machine_queue,machine)
    del tasks[id]

def init_scheduler():
    #启动c程序，后台运行
    import os
    os.system("/home/augustin/docklet/src/aco-mmdkp/acommdkp >/home/augustin/docklet/src/aco-mmdkp.log 2>&1 &")
    
    slogger.setLevel(logging.INFO)
    slogger.info("init scheduler!")
    
    init_sync_socket()
    init_colony_socket()
    init_task_socket()
    init_result_socket()

    _thread.start_new_thread(recv_result,(machines,))



def recover_scheduler():
    global machines
    global tasks
    global machine_queue

    #启动c程序，后台运行
    import os
    os.system("/home/augustin/docklet/src/aco-mmdkp/acommdkp >/home/augustin/docklet/src/aco-mmdkp.log 2>&1 &")
    
    slogger.setLevel(logging.INFO)
    slogger.info("recover scheduler!")

    init_sync_socket()
    init_colony_socket()
    init_task_socket()
    init_result_socket()

    # recover alll the machines
    [status, runlist] = etcdclient.listdir("machines/runnodes")
    for node in runlist:
        nodeip = node['key'].rsplit('/',1)[1]
        if node['value'] == 'ok':
            slogger.info ("running node %s" % nodeip)

            # inform dscheduler the recovered running nodes
            import dscheduler
            slogger.info("recover machine %s to scheduler",nodeip)
            machine = load_machine(nodeip)

            # recover machine_queue
            heapq.heappush(machine_queue,machine)

            # send machine to C process
            send_colony("create",machine.machineid, str(machine.reliable_cpus), str(machine.reliable_mems))
            sync_colony()

    # recover recv_result thread
    _thread.start_new_thread(recv_result,(machines,))
    # recover all the tasks
    load_tasks()
    # send tasks to colony 
    for id,task in tasks.items():
        machineid = task['machineid']
        machine = machines[machineid]        
        send_task(machine,task,"add")

    


def save_machine(machine):
    machine_str = jsonpickle.encode(machine)
    etcdclient.setkey("/scheduler/machines/"+machine.machineid, machine_str)

def load_machine(ip):
    global machines
    [string,machine_str] = etcdclient.getkey("/scheduler/machines/"+ip)
    machine = jsonpickle.decode(machine_str)
    machines[machine.machineid]=machine
    return machine
    
def load_machines():
    global machines
    [status,kvs] = etcdclient.listdir("/scheduler/machines/")
    for kv in kvs:
        machine_str = kv['value']
    machine = jsonpickle.decode(machine_str)
    machines[machine.id]=machine

def save_task(task):
    task_str = json.dumps(task)
    etcdclient.setkey("/scheduler/tasks/"+task['id'], task_str)

def load_tasks():
    global tasks
    [status,kvs] = etcdclient.listdir("/scheduler/tasks/")
    for kv in kvs:
        task_str = kv['value']
    task = jsonpickle.decode(task_str)
    if task['machineid'] in machines.keys():
        tasks[kv['key']]=task
    
def test_all():

    init_scheduler()

    for i in range(0,2):
        add_machine("m"+str(i),64,256)

    slogger.info("add colonies done!")

    requests = generate_test_data(64,256,2,"reliable",0)
#    generate_test_data(64,256,1,"restricted",192)

    for index,request in requests.items():
        pre_allocate(request)
    slogger.info("pre allocate tasks done")
    
    for index,request in requests.items():
        allocate(request['id'])
    slogger.info("allocate tasks done")

    time.sleep(10)
    
    for index,request in requests.items():
        release(request['id'])
    slogger.info("release tasks done")
    
    for index,request in requests.items():
        after_release(request['id'])
    slogger.info("after release tasks done")






if __name__ == '__main__':
#    test_pub_socket();
#    test_colony_socket();
    test_all();
