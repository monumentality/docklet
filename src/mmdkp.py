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
import thread

task_queue = []

machine_queue = []

tasks = {}

machines = {}

def get_machines():
    global machines
    return machines

def generate_test_data(cpu,mem,machines):
    global tasks
#    cpus = np.random.binomial(test_cpus, test_cpus/16, test_cpus*2)
#    mems = np.random.binomial(test_mems, test_mems/16, test_mems*2)
    cpu_arr = np.random.uniform(1,cpu,cpu*machines)
    mem_arr = np.random.uniform(1,mem,cpu*machines)
    prices = np.random.uniform(1,100,cpu*machines)
    for i in range(0,cpu*machines):
        if cpu_arr[i]==0 or mem_arr[i] ==0:
            continue

        task = {
            'id': str(i),
            'cpus': int(math.floor(cpu_arr[i])),
            'mems': int(math.floor(mem_arr[i])),
            'price': int(prices[i]),
            'allocated': "none"
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


def init_machines(cpus,mems,num):
    global machines
    global machine_queue
    machine_queue = []

    for i in range(0,num):
        machine = AllocationOfMachine()
        machine.machineid = str(i)
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

        machines[str(i)] = machine

        # to-do:改成多线程，直接运行每个线程
        # machine.colony.run()
        send_colony("create",machine.machineid, str(machine.cpus), str(machine.mems))


        heapq.heappush(machine_queue,machine)


# 从task_queue中取出最大的，从machines中取出最小的，放置
def dispatch(tasks):
    print("dispatch")

    for key,task in tasks.items():
        price = int(0 - task['price'])
        heapq.heappush(task_queue,(price,task['id'],task))

    # the following is only for test
    while task_queue:
        neg_price,id, task = heapq.heappop(task_queue)
        print("pop task: ",id)
        machine = heapq.heappop(machine_queue)

        machine.add_reliable_task(task)

        print("pop machine: id = ", machine.machineid)
        send_task(machine,task,"add")

        heapq.heappush(machine_queue,machine)


def mdp(tasks,cpus,mems):

#    print(max(1,2,3))
#    print("numpy array: ")
#    print(np.zeros((2,4,2,4)))
    opt = np.zeros((cpus+1,mems+1,cpus+1,mems+1))
    #    print(opt)
    for key,task in tasks.items():
        cpu = int(task['cpus'])
        mem = int(task['mems'])
        price = int(task['price'])
        for i in range(cpus,0,-1):
            for j in range(mems,0, -1):
                for k in range(cpus,0,-1):
                    for l in range(mems,0,-1):
                #                print(i,j,k,l)
                        if not (i< cpu or j< mem) and not (k < cpu or l<mem):
                            opt[i][j][k][l] = max(opt[i][j][k][l],opt[i][j][k-cpu][l-mem]+price,opt[i-cpu][j-mem][k][l]+price)
                        elif (i <cpu or j<mem) and not (k<cpu or l<mem):
                            opt[i][j][k][l] = max(opt[i][j][k][l],opt[i][j][k-cpu][l-mem]+price)
                        elif not (i<cpu or j<mem) and (k<cpu or l<mem):
                            opt[i][j][k][l] = max(opt[i][j][k][l],opt[i-cpu][j-mem][k][l]+price)

                        # 两台机器都不能放的时候什么都不用做
    #print(opt)
    print("exact opt: ",opt[cpus][mems][cpus][mems])
    return opt[cpus][mems][cpus][mems]

def relax_mdp(tasks,cpus,mems,machines):

    cpus = cpus*machines
    mems = mems * machines
    opt = np.zeros((cpus+1,mems+1))
    for key,task in tasks.items():
        i_cpu = int(task['cpus'])
        i_mem = int(task['mems'])
        price = int(task['price'])
        for j in range(cpus,i_cpu-1,-1):
            for k in range(mems,i_mem-1, -1):
                #                print(j,k)
                opt[j][k] = max(opt[j][k],opt[j-i_cpu][k-i_mem]+price)

    #    print(opt)
    print("relax opt: ",opt[cpus][mems])
    return opt[cpus][mems]

def test3():
    relax = 0
    exact = 0
    aco  = 0
    for i in range(0,1):
        parse_test_data('uniform_tasks.txt',64,256,20)

        init_machines(64,256,20)
        dispatch(tasks)

        aco_fast_result = 0
        for machine in machine_queue:
            machine.colony.aco_fast()
            #machine.colony.exact()
            aco_fast_result += machine.colony.current_sum
            print("aco fast result: ",aco_fast_result)

        aco += aco_fast_result

#    print("exact/relax: ", exact/relax)
#    print("aco/exact: ", aco/exact)
#    print("aco/relax: ", aco/relax)
    print("aco: ",aco)

def start_mmdkp():
    #启动c程序，添加新进程
    return

def test_mmdkp():

    generate_test_data(64,256,3)

    init_colony_socket()
    init_task_socket()
    init_result_socket()

    init_machines(64, 256, 3)

    sync_colonies(3);

    thread.start_new_thread(recv_result,(machines,))

    dispatch(tasks);

    while(True):
        print("sleep 1s")
        time.sleep(1)

#    recv_result(machines);

if __name__ == '__main__':
#    test_pub_socket();
#    test_colony_socket();
    test_mmdkp();
