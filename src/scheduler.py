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

tasks = {}

machines = {}

restricted_index = 0

def generate_test_data(cpu,mem,machines,type,id_base):
    global tasks
#    cpus = np.random.binomial(test_cpus, test_cpus/16, test_cpus*2)
#    mems = np.random.binomial(test_mems, test_mems/16, test_mems*2)
    cpu_arr = np.random.uniform(1,cpu,cpu*machines)
    mem_arr = np.random.uniform(1,mem,cpu*machines)
    prices = np.random.uniform(1,100,cpu*machines)
    for i in range(0+id_base,cpu*machines):
        if cpu_arr[i]==0 or mem_arr[i] ==0:
            continue

        task = {
            'id': str(i),
            'cpus': int(math.floor(cpu_arr[i])),
            'mems': int(math.floor(mem_arr[i])),
            'price': int(prices[i]),
            'allocated': "none",
            'type': type
        }
        key = str(i)
        tasks[key] = task
    #    print(task)
    # write to a file
    with open('uniform_tasks.txt','w') as f:
        for key, task in tasks.items():
            f.write(str(task['cpus'])+' '+str(task['mems'])+' '+str(task['price'])+'\n')

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
                'price': int(arr[2])
            }
            key = str(i)
            tasks[key] = task
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


# 从task_queue中取出最大的，从machines中取出最小的，放置
def dispatch_tasks(tasks):
    slogger.debug("dispatch")

    for key,task in tasks.items():
        price = int(0 - task['price'])
        heapq.heappush(reliable_queue,(price,task['id'],task))

    # the following is only for test
    while reliable_queue:
        neg_price,id, task = heapq.heappop(reliable_queue)
        slogger.debug("pop task: %s",id)
        machine = heapq.heappop(machine_queue)

        machine.add_reliable_task(task)

        print("pop machine: id = %s", machine.machineid)
        send_task(machine,task,"add")

        heapq.heappush(machine_queue,machine)

def dispatch(task):
    if task["type"]=='reliable':
        dispatch_reliable(task)
    else:
        dispatch_restricted(task)


def dispatch_reliable(task):
#    slogger.debug("dispatch reliable")

    tasks[task['id']] = task
    machine = heapq.heappop(machine_queue)

    machine.add_reliable_task(task)

#    slogger.debug("pop machine: id = %s", machine.machineid)
    send_task(machine,task,"add")

    heapq.heappush(machine_queue,machine)


def dispatch_restricted(task):
#    slogger.debug("dispatch restricted")

    tasks[task['id']] = task
    if(restricted_index == len(machines)):
        resctricted =0
    else:
        restrcted_index += 1

    machine.add_restricted_task(task)

def release(id):
    task = tasks[id]
    machine = task['machine']
    if task['type'] == 'reliable':
        slogger.debug("release reliable")
        machine.release_reliable_task(task)
    else:
        slogger.debug("release restricted")
        machine.release_restricted_task(task)


def test_dispatch_and_release():

    init_scheduler(None)

    generate_test_data(64,256,1000,"reliable",0)
#    generate_test_data(64,256,1,"restricted",192)

    for index,task in tasks.items():
        dispatch(task)

    slogger.info("dispatch tasks done")

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
    test_dispatch_and_release();
