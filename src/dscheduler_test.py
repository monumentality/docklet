# coding=UTF-8
#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import math
import random
import numpy as np
from mdkp import Colony
from dmachine_test import AllocationOfMachine
import heapq
from dconnection import *
import time
import _thread
import logging
import json
import jsonpickle
import os

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

def generate_test_data(cpu,mem,machines,request_type,distribution,id_base):
    task_requests = {}
    num_tasks = 0
    if distribution == 'binomial':
        num_tasks = int(cpu   * machines)
        cpu_arr = np.random.binomial(cpu, 4/cpu, num_tasks)
        mem_arr = np.random.binomial(mem, 1/256, num_tasks)
    elif distribution == 'uniform':
        num_tasks = int(cpu/8 * machines)
        cpu_arr = np.random.uniform(1,cpu,cpu*machines)
        mem_arr = np.random.uniform(1,mem,cpu*machines)

    bids = np.random.uniform(1,100,num_tasks)
    for i in range(0+id_base,int(num_tasks)):
        if cpu_arr[i]==0 or mem_arr[i] ==0:
            continue
        if request_type == 'reliable':
            task = {
                'id': str(i),
                'cpus': str(int(math.floor(cpu_arr[i]))),
                'mems': str(int(math.floor(mem_arr[i]))),
                'bid': str(int(bids[i]))
#                'bid': str(max(int(np.random.normal(cpu_arr[i]+mem_arr[i], 10, 1)[0]),0))
            }
        else:
            task = {
                'id': str(i),
                'cpus': str(int(math.floor(cpu_arr[i]))),
                'mems': str(int(math.floor(mem_arr[i]))),
                'bid': 0
            }
        key = str(i)
        task_requests[key] = task

    # write to a file
    with open("/home/augustin/docklet/test_data/"+distribution+'_tasks'+str(machines)+'.txt','w') as f:
        for key, task in task_requests.items():
            f.write(str(task['cpus'])+' '+str(task['mems'])+' '+str(task['bid'])+'\n')

        f.flush()
        os.fsync(f)
    return task_requests

def parse_test_data(filename,cpus,mems,machines,request_type):
    num_tasks =0
    if request_type=="uniform":
        num_tasks = cpus * machines
    else:
        num_tasks = cpus/2*machines
    task_requests = {}
    with open(filename,'r') as f:
        i =0
        for line in f.readlines()[0:int(num_tasks)]:
            arr = line.split()
            task = {
                'id': str(i),
                'cpus': arr[0],
                'mems': arr[1],
                'bid': arr[2]
            }
            key = str(i)
            task_requests[key] = task
            i+=1
            print(task)
    return task_requests

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
        machine.pre_cpus_wanted += int(task['cpus'])
        machine.pre_mems_wanted += int(task['mems'])
        machine.pre_unit_value = machine.total_value
#        machine.pre_unit_value = machine.total_value/(machine.pre_cpus_wanted/64 + machine.pre_mems_wanted/256)

        heapq.heappush(machine_queue,machine)

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

    return task



def allocate(id):
    task = tasks[id]
    machineid = task['machineid']
    machine = machines[machineid]
    if 'bid' in task and task['bid']!='0':
        #    slogger.debug("dispatch reliable")
        task = machine.add_reliable_task(task)

        #    slogger.debug("pop machine: id = %s", machine.machineid)
        send_task(machine,task,"add")

    else:
        #    slogger.debug("dispatch restricted")
        task = machine.add_restricted_task(task)

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
#    os.system("/home/augustin/docklet/src/aco-mmdkp/acommdkp >/home/augustin/docklet/src/aco-mmdkp.log 2>&1 &")
    
    slogger.setLevel(logging.INFO)
    slogger.info("init scheduler!")
    
    init_sync_socket()
    init_colony_socket()
    init_task_socket()
    init_result_socket()

    _thread.start_new_thread(recv_result,(machines,))

    
def test_all():

    init_scheduler()

    for i in range(0,2):
        add_machine("m"+str(i),64,256)

    slogger.info("add colonies done!")

#    requests = generate_test_data(64,256,2,"reliable",'uniform',0)
#    generate_test_data(64,256,1,"restricted",192)

    requests = parse_test_data('uniform_tasks1.txt',64,256,1,"uniform")
    
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
    
def relax_mdp(tasks,cpus,mems,machines):

    cpus = cpus*machines
    mems = mems * machines
    opt = np.zeros((cpus+1,mems+1))
    for key,task in tasks.items():
        i_cpu = int(task['cpus'])
        i_mem = int(task['mems'])
        bid = int(task['bid'])
        for j in range(cpus,i_cpu-1,-1):
            for k in range(mems,i_mem-1, -1):
                #                print(j,k)
                opt[j][k] = max(opt[j][k],opt[j-i_cpu][k-i_mem]+bid)

    #    print(opt)
    print("relax opt: ",opt[cpus][mems])
    return opt[cpus][mems]

def test_quality(num_machines,request_type):

    init_scheduler()
    for i in range(0,num_machines):
        add_machine("m"+str(i),64,256)

    time.sleep(10)
    slogger.info("add colonies done!")

#    requests = generate_test_data(64,256,2,"reliable",'uniform',0)
#    generate_test_data(64,256,1,"restricted",192)

    requests = parse_test_data("/home/augustin/docklet/test_data/"+request_type+'_tasks'+str(num_machines)+'.txt',64,256,num_machines,request_type)
    
    for index,request in requests.items():
        pre_allocate(request)
    slogger.info("pre allocate tasks done")
    
    for index,request in requests.items():
        allocate(request['id'])
    slogger.info("allocate tasks done")

    time.sleep(30)

    # generate result quality
    total_social_welfare = 0
    for i in range(0,num_machines):
        total_social_welfare += machines['m'+str(i)].social_welfare

    print("MDRPSPA social_welfare: ",total_social_welfare);

#    upper = relax_mdp(requests,64,256,num_machines)
#    print("upper bound: ", upper)
    
def test_generate_test_data(num,request_type):
    for i in range(1,num+1):
        generate_test_data(64,256,i,"reliable",request_type,0)    

if __name__ == '__main__':
#    test_pub_socket();
#    test_colony_socket();
#    test_all();
#    test_generate_test_data(1,'binomial')
    test_quality(100,'binomial')
#        generate_test_data(64,256,i,"reliable",'binomial',0)
