# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-

import math
import random
import numpy as np
from mdkp import Colony
from machine import AllocationOfMachine
import heapq
from connection import *
import time
import _thread
import logging
from log import slogger
#import log

reliable_queue = []

restricted_queue = []

machine_queue = []

# only used for test
task_requests = {}

tasks = {}

machines = {}

restricted_index = 0

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
            'cpus': int(math.floor(cpu_arr[i])),
            'mems': int(math.floor(mem_arr[i])),
            'bid': int(bids[i])
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


def add_machine(id,cpus,mems):
    global machines
    global machine_queue

    machine = AllocationOfMachine()
    machine.machineid = id
    machine.cpus = cpus
    machine.mems = mems
    machine.colony = Colony({},cpus=cpus,mems=mems)
    machine.tasks = {}
    machine.total_value = 0

    machine.cpus_wanted = 0
    machine.mems_wanted = 0

    # init allocation data
    machine.reliable_allocations = []
    machine.restricted_allocations = []

    machines[id] = machine
    heapq.heappush(machine_queue,machine)

    # to-do:改成多线程，直接运行每个线程
    # machine.colony.run()
    send_colony("create",machine.machineid, str(machine.cpus), str(machine.mems))



def allocate(task):
    if 'bid' in task and task['bid']!='0':
        machine = heapq.heappop(machine_queue)
        machine.total_value += task['bid']
        
        task = machine.add_reliable_task(task)
        heapq.heappush(machine_queue,machine)
        
        tasks[task['id']] = task
        
        #    slogger.debug("pop machine: id = %s", machine.machineid)
        send_task(machine,task,"add")

    else:
        if(restricted_index == len(machines)):
            restricted =0
        else:
            restricted_index += 1
            
        task = machines[restricted_index].add_restricted_task(task)

        tasks[task['id']] = task

    return task

def release(id):
    machine = tasks[id]['machine']
    if task['type'] == 'reliable':
        slogger.debug("release reliable")
        for index,machine in enumerate(machine_queue):
            if task['machine'] == machine:
                del machine_queue[index]
                break

        machine.total_value -= task['bid']
        heapq.heappush(machine_queue,machine)
        machine.release_reliable_task(id)
        
        send_task(self,task,"delete")
        
    else:
        slogger.debug("release restricted")
        machine.release_restricted_task(id)

    del tasks[id]


def test_allocate_and_release():

    init_scheduler(None)

    requests = generate_test_data(64,256,1000,"reliable",0)
#    generate_test_data(64,256,1,"restricted",192)

    for index,request in requests.items():
        allocate(request)
    slogger.info("dispatch tasks done")

    for index,request in requests.items():
        release(request)
    slogger.info("release tasks done")

    time.sleep(100)

#    for index,task in tasks.items():
#        release(task['id'])





def init_scheduler(initial_machines):
    #启动c程序，添加新进程


    slogger.setLevel(logging.INFO)

    slogger.info("init scheduler!")
    init_sync_socket()
    init_colony_socket()
    init_task_socket()
    init_result_socket()

    for i in range(0,1000):
        add_machine("m"+str(i),64,256)

    slogger.info("add colonies done!")
    sync_colonies(1000)
    slogger.info("sync colonies done!")

    _thread.start_new_thread(recv_result,(machines,))



if __name__ == '__main__':
#    test_pub_socket();
#    test_colony_socket();
    test_allocate_and_release();
