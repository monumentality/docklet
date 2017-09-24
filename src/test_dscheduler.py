# coding=UTF-8
#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from scipy.stats import norm
from scipy.stats import binom
from scipy.stats import expon
from scipy.stats import genexpon
import math
import random
import numpy as np
from mdkp import Colony
from test_dmachine import AllocationOfMachine
import heapq
from dconnection import *
#import dconnection
import time
import _thread
import logging
import json
import jsonpickle
import os
import threading
import matplotlib.pyplot as plt

from log import slogger

#import log

machine_queue = []

queue_lock = threading.Lock()

# only used for test
task_requests = {}

tasks = {}

machines = {}

restricted_index = 0

node_manager = None

etcdclient = None

recv_stop = False

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
    global queue_lock
    global machines
    
    if 'bid' in task and task['bid']!='0':
#        queue_lock.acquire()
#        machine = heapq.heappop(machine_queue)

# 计算每台机器新的heu, 挑选最小的
        least_heu = float('inf')
        selected_machine = {}
        for id, machine in machines.items():
            heu = machine.cpu_value * int(task['cpus']) + machine.mem_value * int(task['mems'])
            if heu < least_heu:
                selected_machine = machine
                least_heu = heu

        task['machineid'] = selected_machine.machineid

        task['allocation_type'] = 'none'
        task['allocation_cpus'] = str(int(task['cpus'])*1000)
        task['allocation_mems'] = task['mems']
        task['allocation_mems_sw'] = str( 2 * int(task['mems']) )
        task['allocation_mems_soft'] = str( 2 * int(task['mems']) )
        tasks[task['id']] = task

# 更新该台机器的MPV, RV不变
        machine = selected_machine
        machine.pre_cpus_wanted += int(task['cpus'])
        machine.pre_mems_wanted += int(task['mems'])

        #把该task加入heu_allocations
        machine.heu_tasks.append(task)

        # 不满
        if(machine.pre_cpus_wanted <= machine.reliable_cpus and machine.pre_mems_wanted <= machine.reliable_mems):
            #            utilization = (machine.pre_cpus_wanted * machine.rareness_ratio + machine.pre_mems_wanted) / (machine.reliable_cpus * machine.rareness_ratio + machine.reliable_mems)
            utilization = 0.5 * machine.pre_cpus_wanted / machine.reliable_cpus + 0.5 * machine.pre_mems_wanted / machine.reliable_mems
            machine.cpu_value = 0.01 * machine.rareness_ratio * utilization
            machine.mem_value = 0.01 * utilization

            machine.rareness_ratio = ((machine.reliable_mems ** 2) * machine.pre_cpus_wanted) / ((machine.reliable_cpus ** 2) * machine.pre_mems_wanted)

        # 满，贪心算法，求出获胜者中的最低出价
        else:
            if float(task['bid']) <= machine.cpu_value * int(task['cpus']) + machine.mem_value * int(task['mems']):
                return task
            
            for task in machine.heu_tasks:
                heu = float(task['bid']) / (int(task['cpus']) * machine.rareness_ratio + int(task['mems']))
                task['heu'] = heu
                
            sorted_heu = sorted(machine.heu_tasks, key=lambda k: k['heu'],reverse=True)

            utilized_cpus = 0
            utilized_mems = 0
            lowest_heu = 0.01

            for task in sorted_heu:
                if utilized_cpus + int(task['cpus']) < machine.reliable_cpus and utilized_mems + int(task['mems']) < machine.reliable_mems:
                    lowest_heu = task['heu']
                    utilized_cpus += int(task['cpus'])
                    utilized_mems += int(task['mems'])

                else:
                    break

            machine.cpu_value = machine.rareness_ratio * lowest_heu
            machine.mem_value = lowest_heu

            machine.rareness_ratio = ((machine.reliable_mems ** 2) * utilized_cpus) / ((machine.reliable_cpus ** 2) * utilized_mems)
            
#        time.sleep(0.1)
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
        send_task(machineid,task,"add")

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

def stop_scheduler():
    global queue_lock
#    print("stop scheduler")
    queue_lock.acquire()
    os.system("kill -9 $(pgrep acommdkp) > /dev/null 2>&1")
#    time.sleep(1)
#    print("close sockets")
    close_sync_socket()
    close_colony_socket()
    close_task_socket()
    import dconnection
    dconnection.recv_run = False
    queue_lock.release()
#    time.sleep(1)

def init_scheduler():
    global queue_lock
    #启动c程序，后台运行
    os.system("rm -rf /home/augustin/docklet/src/aco-mmdkp.log")
    os.system("/home/augustin/docklet/src/aco-mmdkp/acommdkp >/home/augustin/docklet/src/aco-mmdkp.log 2>&1 &")
#    time.sleep(1)
    slogger.setLevel(logging.INFO)
    slogger.info("init scheduler!")
#    print("init scheduler")
    init_sync_socket()
    init_colony_socket()
    init_task_socket()
    init_result_socket()
    _thread.start_new_thread(recv_result,(machines,machine_queue,queue_lock))


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


corr0 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

corr1 = [[1, 0.9, 0.9], [0.9, 1, 0.9], [0.9, 0.9, 1]]

#corr1 = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]


corr2 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


corr05 = [[1, -0.5, 0.5, -0.5], [-0.5, 1, -0.5, 0.5], [0.5, -0.5, 1, -0.5], [-0.5, 0.5, -0.5, 1]]

corr_opt = [[1, -0.9, 0.9, -0.9], [-0.9, 1, -0.9, 0.9], [0.9, -0.9, 1, -0.9], [-0.9, 0.9, -0.9, 1]]

corr00 = [[1, 0, 0.5, -0.5], [0, 1, 0, 0.5], [0.5, 0, 1, 0], [0, 0.5, 0, 1]]

def generate_uniform_opt(cpu,mem,num_tasks):
    mean = [0, 0, 0, 0]

    corr = corr_opt
    a,b,c,d = np.random.multivariate_normal(mean, corr, num_tasks).T
#    for i,ia in enumerate(a):
#        print(a[i],b[i],c[i],d[i],'\n')

    cpus = []
    mems = []
    values = []
    for ix in a:
        cpus.append(norm.cdf(ix)*(cpu/4-1)+1)

    for iy in b:
        mems.append(norm.cdf(iy)*(mem/4-1)+1)

    for index in range(len(c)):
        if a[index]> b[index]:
            values.append(norm.cdf(c[index])*(100-1)+1)
        else:
            values.append(norm.cdf(d[index])*(100-1)+1)
#    for i,icpus in enumerate(cpus):
#        print(cpus[i],mems[i],values[i],'\n')
#    print(np.corrcoef([cpus,mems,values]))
    return cpus,mems,values

def generate_uniform(cpu,mem,num_tasks,corr):
    mean = [0, 0, 0]
    if corr == 'corr0':
        corr = corr0
    elif corr == 'corr1':
        corr = corr1
    elif corr == 'corr2':
        corr = corr2
    x, y, z = np.random.multivariate_normal(mean, corr, num_tasks).T

#    print(np.corrcoef([x,y,z]))
    cpus = []
    mems = []
    values = []
    for ix in x:
        cpus.append(norm.cdf(ix)*(cpu/4-1)+1)

    for iy in y:
        mems.append(norm.cdf(iy)*(mem/4-1)+1)

    for iz in z:
        values.append(norm.cdf(iz)*(100-1)+1)

#    print( np.corrcoef([cpus,mems,values]) )
    return cpus,mems,values

def generate_multivariate_binomial(cpu,mem,num_tasks):
    mean = [0, 0, 0]
    corr = [[1, -0.5, -0.5], [-0.5, 1, -0.5], [-0.5, -0.5, 1]]
    x, y, z = np.random.multivariate_normal(mean, corr, num_tasks).T

    cpus = []
    mems = []
    values = []
    for ix in x:
        cpus.append(binom.ppf(norm.cdf(ix),cpu,8/cpu))

    for iy in y:
        mems.append(binom.ppf(norm.cdf(iy),mem,8/mem))

    for iz in z:
        values.append(norm.cdf(iz)*(100-1)+1)
#    print("cpu mem corr: ", np.corrcoef(cpus,mems)[0, 1])
#    print("cpus: ",cpus)
    return cpus,mems,values

def generate_ec2(cpu,mem,num_tasks,corr):
    mean = [0, 0, 0]
    if corr == 'corr0':
        corr = corr0
    elif corr == 'corr1':
        corr = corr1
    elif corr == 'corr2':
        corr = corr2
    x, y, z = np.random.multivariate_normal(mean, corr, num_tasks).T

    cpus = []
    mems = []
    values = []
    for ix in x:
#        cpus.append(int(8-round(expon.ppf(norm.cdf(ix),0,0.25))))
        cpus.append(norm.cdf(ix)*3+5)
    for iy in y:
#        mems.append(int(15-round(expon.ppf(norm.cdf(iy),0,0.25))))
        mems.append(norm.cdf(iy)*14+1)
    for iz in z:
        values.append(norm.cdf(iz)*(100-1)+1)
#    print("cpu value corr: ", np.corrcoef(cpus,values)[0, 1])
#    print("cpus: ",cpus)
#    print("mems: ",mems)
#    print("values:",values)
    return cpus,mems,values

def generate_ec2_opt(cpu,mem,num_tasks):

    mean = [0, 0, 0, 0]
    corr = corr_opt
    a,b,c,d = np.random.multivariate_normal(mean, corr, num_tasks).T
#    for i,ia in enumerate(a):
#        print(a[i],b[i],c[i],d[i],'\n')

    cpus = []
    mems = []
    values = []
    for ix in a:
        cpus.append(norm.cdf(ix)*3+5)
    for iy in b:
        mems.append(norm.cdf(iy)*14+1)

    for index in range(len(c)):
        if a[index]> b[index]:
            values.append(norm.cdf(c[index])*(100-1)+1)
        else:
            values.append(norm.cdf(d[index])*(100-1)+1)

#    for i,icpus in enumerate(cpus):
#        print(cpus[i],mems[i],values[i],'\n')
    return cpus,mems,values

def generate_test_data(cpu,mem,machines,request_type,distribution,corr,id_base):
    task_requests = {}
    num_tasks = 0
    if distribution == 'binomial':
        num_tasks = int(32 * machines)
#        cpu_arr = np.random.binomial(cpu, 4/cpu, num_tasks)
#        mem_arr = np.random.binomial(mem, 1/256, num_tasks)
        cpu_arr, mem_arr,bids = generate_multivariate_binomial(cpu,mem,num_tasks)
    elif distribution == 'uniform':
        num_tasks = int(32 * machines)
#        cpu_arr = np.random.uniform(1,cpu,cpu*machines)
#        mem_arr = np.random.uniform(1,mem,cpu*machines)
        if corr == 'corr_opt':
            cpu_arr,mem_arr,bids = generate_uniform_opt(cpu,mem,num_tasks)
        else:
            cpu_arr,mem_arr,bids = generate_uniform(cpu,mem,num_tasks, corr)

    elif distribution == 'ec2':
        num_tasks = int(cpu/4 * machines)
#        cpu_arr = np.random.uniform(1,cpu,cpu*machines)
#        mem_arr = np.random.uniform(1,mem,cpu*machines)
        if corr == 'corr_opt':
            cpu_arr, mem_arr,bids = generate_ec2_opt(cpu,mem,num_tasks)
        else:
            cpu_arr, mem_arr,bids = generate_ec2(cpu,mem,num_tasks,corr)            

    elif distribution == 'ca':
        num_tasks = int(32 * machines)
        if corr == 'corr_opt':
            cpu_arr,mem_arr,bids = generate_uniform_opt(cpu,mem,num_tasks)
        else:
            cpu_arr,mem_arr,bids = generate_uniform(cpu,mem,num_tasks, corr)

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
    with open("/home/augustin/docklet/test_data/"+distribution + corr + '_tasks'+str(machines)+'.txt','w') as f:
        for key, task in task_requests.items():
            f.write(str(task['cpus'])+' '+str(task['mems'])+' '+str(task['bid'])+'\n')

        f.flush()
        os.fsync(f)
    return task_requests

def parse_test_data(filename,cpus,mems,machines,distribution):
    num_tasks =0
    if distribution=="uniform":
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
#            print(task)
    return task_requests

def test_generate_test_data(num,distribution, corr):
    for i in range(1,num+1):
        print(i)
        generate_test_data(64,256,i,"reliable",distribution,corr,0)

def test_compare_ec2(num_machines, distribution, corr):
    os.system("kill -9 $(pgrep acommdkp) > /dev/null 2>&1")
#    time.sleep(1)
    init_scheduler()
    for i in range(0,num_machines):
        add_machine("m"+str(i),256,480)
    slogger.info("add colonies done!")
#    time.sleep(1)
    requests = parse_test_data("/home/augustin/docklet/test_data/"+distribution + corr +'_tasks'+str(num_machines)+'.txt',256,480,num_machines, distribution)

    i = 0
    j=0
    for index,request in requests.items():
        pre_allocate(request)
        allocate(request['id'])
        if i == len(requests.items())/num_machines*2:
            time.sleep(0.1)
#            print("part ",j, " done")
            i =0
            j+=1
        i+=1

    slogger.info("pre allocate tasks done")
    slogger.info("allocate tasks done")

    time.sleep(max(1,0.1 * num_machines))

    # generate result quality
    total_social_welfare = 0
    for i in range(0,num_machines):
#        print('m'+str(i)+": social_welfare", machines['m'+str(i)].social_welfare)
#        print('m'+str(i)+": heu", machines['m'+str(i)].placement_heu)
        total_social_welfare += machines['m'+str(i)].social_welfare

#    print("MDRA social_welfare: ",total_social_welfare);
    ec2_social_welfare = 0
    newlist = sorted(list(requests.values()), key=lambda k: k['bid'],reverse=True)
    for i in range(0,32*num_machines):
        ec2_social_welfare += int(newlist[i]['bid'])

#    print("ec2 social_welfare: ",ec2_social_welfare)
#    upper = relax_mdp(requests,256,480,num_machines)
#    print("upper bound: ", upper)

    stop_scheduler()
    return total_social_welfare, ec2_social_welfare


def generate_ec2_1(num, corr):
    sw1 = []
    sw2 = []
    for i in range(1,num):
        times = int(num/i)
        sw1_i = 0
        sw2_i = 0

        for j in range(times):
            generate_test_data(256,480,i,"reliable",'ec2',corr,0)
            sw1_i_j, sw2_i_j = test_compare_ec2(i,'ec2', corr)
            sw1_i += sw1_i_j
            sw2_i += sw2_i_j
        sw1_i = sw1_i / times
        sw2_i = sw2_i / times

        print(i, " th sw1, sw2:  ", sw1_i, sw2_i, sw1_i/sw2_i)
        sw1.append(sw1_i)
        sw2.append(sw2_i)
        


    with open("/home/augustin/docklet/test_result/ec2_1_"+str(num)+"_"+corr+".txt",'w') as f:
        for i in range(1,num):
            f.write(str(sw1[i-1])+' '+str(sw2[i-1])+'\n')
        f.flush()
        os.fsync(f)

    plt.clf()
    plt.plot(range(1,num), sw1, 'k-', label='MDRA', color='red')
    plt.plot(range(1,num), sw2, 'k--', label='EC2', color='blue')
    plt.xlabel('number of machines')
    plt.ylabel('social welfare')
    plt.legend(loc ='lower right')
    plt.savefig("ec2_1_"+str(num)+"_"+corr+".png")

def generate_ec2_2(num, corr):
    ratios = []
    with open("/home/augustin/docklet/test_result/ec2_1_"+str(num)+"_" + corr + ".txt",'r') as f:
        for line in f.readlines()[0:num]:
            arr = line.split()
            ratio = float(arr[0])/float(arr[1])
            ratios.append(ratio)

    print(len(ratios))
    plt.figure(2,figsize=(8,4))
    plt.plot(np.array(range(1,num)),np.array(ratios),'k-')
    plt.xlabel('number of machines')
    plt.ylabel('Improvement factor of Social welfare')
    plt.ylim(1,1.3)
#    plt.legend()
    plt.savefig("ec2_2_"+str(num)+"_" + corr + ".png")

def draw_ec2(num, corr):
    ratios = []
    sw1 = []
    sw2 = []
    with open("/home/augustin/docklet/test_result/ec2_1_"+str(num)+"_" + corr + ".txt",'r') as f:
        for line in f.readlines()[0: num]:
            arr = line.split()
            ratio = float(arr[0])/float(arr[1])
            ratios.append(ratio)
            sw1.append(float(arr[0]))
            sw2.append(float(arr[1]))

    plt.clf()
    plt.plot(range(1,num), sw1, 'k-', label='MDRA', color='red')
    plt.plot(range(1,num), sw2, 'k--', label='SPOT-C3-2XL', color='blue')
    plt.xlabel('number of machines')
    plt.ylabel('social welfare')
    plt.legend(loc ='lower right')
    plt.savefig("ec2_1_"+str(num)+"_"+corr+".png")

#    plt.figure(2)
#    plt.plot(np.array(range(1,100)),np.array(ratios),'k-')
#    plt.xlabel('number of machines')
#    plt.ylabel('Ratio of Social welfare of MDRPSPA to EC2')
#    plt.ylim(1,1.3)
#    plt.savefig("ec2_2_"+str(num)+"_" + corr + ".png")

def draw_ec2_all(num):
    ratios1 = []
    ratios2 = []
    ratios3 = []
    with open("/home/augustin/docklet/test_result/ec2_1_100_corr0.txt",'r') as f:
        for line in f.readlines()[0: num]:
            arr = line.split()
            ratio = float(arr[0])/float(arr[1])
            ratios1.append(ratio)

    with open("/home/augustin/docklet/test_result/ec2_1_100_corr1.txt",'r') as f:
        for line in f.readlines()[0: num]:
            arr = line.split()
            ratio = float(arr[0])/float(arr[1])
            ratios2.append(ratio)

    with open("/home/augustin/docklet/test_result/ec2_1_100_corr_opt.txt",'r') as f:
        for line in f.readlines()[0: num]:
            arr = line.split()
            ratio = float(arr[0])/float(arr[1])
            ratios3.append(ratio)            

    plt.clf()
    plt.plot(range(1,100),ratios3,'k-',label='bids_type_2', color='red')
    plt.plot(range(1,100),ratios1,'k--',label='bids_type_0', color='blue')
    plt.plot(range(1,100),ratios2,'k-.',label='bids_type_1', color='purple')

    plt.xlabel('number of machines')
    plt.ylabel('Ratio of Social Welfare of MDRA to EC2')
    plt.ylim(1,1.4)
    plt.legend(loc ='lower right')
    plt.savefig("ec2_2_all.png")

def compare_ca(num_machines, distribution, corr):
    
    os.system("kill -9 $(pgrep acommdkp) > /dev/null 2>&1")
    init_scheduler()
    for i in range(0,num_machines):
        add_machine("m"+str(i),64,256)
    slogger.info("add colonies done!")

    requests = parse_test_data("/home/augustin/docklet/test_data/"+distribution + corr +'_tasks'+str(num_machines)+'.txt',64,256,num_machines,distribution)

    i = 0
    j=0
    for index,request in requests.items():
        pre_allocate(request)
        allocate(request['id'])
        if i == len(requests.items())/num_machines*2:
            i =0
            j+=1
        i+=1
    
    slogger.info("pre allocate tasks done")
    slogger.info("allocate tasks done")

    time.sleep(0.1*num_machines)

    # generate result quality
    total_social_welfare = 0
    for i in range(0,num_machines):
#        print('m'+str(i)+": social_welfare", machines['m'+str(i)].social_welfare)
#        print('m'+str(i)+": heu", machines['m'+str(i)].placement_heu)
        total_social_welfare += machines['m'+str(i)].social_welfare

#    print("MDRA social_welfare: ",total_social_welfare);

    # calculate ca-provision social welfare
    ca_social_welfare = 0
    vmbids = []
    for index,request in requests.items():
        vmbid = {}
        num_vm = max(int(request['cpus']), math.ceil(float(request['mems'])/4))
        vmbid['vms'] = num_vm
        vmbid['bid'] = float(request['bid'])
        vmbid['sort'] = float(request['bid'])/num_vm
        vmbids.append(vmbid)
    newlist = sorted(vmbids, key=lambda k: k['sort'],reverse=True)
    total_capacity = 64 * num_machines
    utilized = 0
    for vmbid in newlist:
#        print("ca bid: ",vmbid['vms'],"  ",vmbid['bid'])
        utilized += vmbid['vms']
        if utilized <= total_capacity:
            ca_social_welfare += vmbid['bid']
        else:
            break

#    print("ca social_welfare: ",ca_social_welfare)

#    upper = relax_mdp(requests,64,256,num_machines)
#    print("upper bound: ", upper)

    stop_scheduler()
    return total_social_welfare, ca_social_welfare

def compare_ca_1(num_machines, distribution, corr):
    sw1 = []
    sw2 = []
    num = num_machines
    for i in range(1,num_machines):
        times = int(num_machines/i)
        sw1_i = 0
        sw2_i = 0

        for j in range(times):
            generate_test_data(64,256,i,"reliable",distribution,corr,0)
            sw1_i_j, sw2_i_j = compare_ca(i, distribution, corr)
            sw1_i += sw1_i_j
            sw2_i += sw2_i_j

        sw1_i = sw1_i / times
        sw2_i = sw2_i / times
        print(i, " th sw: ", sw1_i, sw2_i, sw1_i/sw2_i)
        sw1.append(sw1_i)
        sw2.append(sw2_i)
        


    with open("/home/augustin/docklet/test_result/"+distribution+"_1_" +str(num) +"_"+corr+".txt",'w') as f:
        for i in range(1,num_machines):
            f.write(str(sw1[i-1])+' '+str(sw2[i-1])+'\n')
        f.flush()
        os.fsync(f)

    plt.clf()
    plt.plot(range(1,num_machines), sw1, 'k-', label='MDRA', color='red')
    plt.plot(range(1,num_machines), sw2, 'k--', label='CA-PROVISION', color='blue')
    plt.xlabel('number of machines')
    plt.ylabel('social welfare')
    plt.legend(loc ='lower right')
    plt.savefig(distribution+"_1_"+str(num)+"_"+corr+".png")
    return

def compare_ca_2(num, distribution, corr):
    ratios = []
    with open("/home/augustin/docklet/test_result/" + distribution + "_1_" +str(num)+"_" + corr + ".txt",'r') as f:
        for line in f.readlines()[0:num]:
            arr = line.split()
            ratio = float(arr[0])/float(arr[1])
            ratios.append(ratio)

    plt.clf()
    plt.plot(np.array(range(1,num)),np.array(ratios),'k-')
    plt.xlabel('number of machines')
    plt.ylabel('Improvement factor of Social welfare')
    plt.ylim(1,2)
#    plt.legend()
    plt.savefig(distribution+"_2_"+str(num)+"_" + corr + ".png")

def draw_ca(num, dis, corr):
    ratios = []
    sw1 = []
    sw2 = []
    with open("/home/augustin/docklet/test_result/ca_1_" +str(num)+"_" + corr + ".txt",'r') as f:
        for line in f.readlines()[0: num]:
            arr = line.split()
            ratio = float(arr[0])/float(arr[1])
            ratios.append(ratio)
            sw1.append(float(arr[0]))
            sw2.append(float(arr[1]))

    plt.clf()
    plt.plot(range(1,num), sw1, 'k-', label='MDRA', color='red')
    plt.plot(range(1,num), sw2, 'k--', label='CA-PROVISION', color='blue')
    plt.xlabel('number of machines')
    plt.ylabel('social welfare')
    plt.legend(loc ='lower right')
    plt.savefig(dis+"_1_"+str(num)+"_"+corr+".png")
    
 
#    plt.clf()
#    plt.plot(np.array(range(1,100)),np.array(ratios),'k-')
#    plt.xlabel('number of machines')
#    plt.ylabel('Ratio of Social welfare of MDRPSPA to CA-PROVISION')
#    plt.ylim(1,2)
#    plt.savefig("ca_2_" + str(num)+ "_" + corr + ".png")
#    return

def draw_ca_all():
    ratios1 = []
    ratios2 = []
    ratios3 = []
    with open("/home/augustin/docklet/test_result/ca_1_100_corr0.txt",'r') as f:
        for line in f.readlines()[0: 100]:
            arr = line.split()
            ratio = float(arr[0])/float(arr[1])
            ratios1.append(ratio)

    with open("/home/augustin/docklet/test_result/ca_1_100_corr1.txt",'r') as f:
        for line in f.readlines()[0: 100]:
            arr = line.split()
            ratio = float(arr[0])/float(arr[1])
            ratios2.append(ratio)

    with open("/home/augustin/docklet/test_result/ca_1_100_corr_opt.txt",'r') as f:
        for line in f.readlines()[0: 100]:
            arr = line.split()
            ratio = float(arr[0])/float(arr[1])
            ratios3.append(ratio)            

    plt.clf()
    plt.plot(range(1,100),ratios3,'k-',label='bids_type_2', color='red')
    plt.plot(range(1,100),ratios1,'k--',label='bids_type_0', color='blue')
    plt.plot(range(1,100),ratios2,'k-.',label='bids_type_1', color='purple')

    plt.xlabel('number of machines')
    plt.ylabel('Ratio of Social Welfare of MDRA to CA-PROVISION')
    plt.ylim(1,1.6)
    plt.legend(loc ='upper right')
    plt.savefig("ca_2_all.png")
    
    return

def test_quality(num_machines, distribution, corr):
    os.system("kill -9 $(pgrep acommdkp) > /dev/null 2>&1")
    init_scheduler()
    for i in range(0,num_machines):
        add_machine("m"+str(i),64,256)

#    time.sleep(1)
    slogger.info("add colonies done!")

#    requests = generate_test_data(64,256,2,"reliable",'uniform',0)
#    generate_test_data(64,256,1,"restricted",192)

    requests = parse_test_data("/home/augustin/docklet/test_data/"+distribution +corr+'_tasks'+str(num_machines)+'.txt',64,256,num_machines, distribution)

    i = 0
    j=0
    for index,request in requests.items():
        pre_allocate(request)
        allocate(request['id'])
        if i == len(requests.items())/num_machines/2:
#            time.sleep(1)
#            print("part ",j, " done")
            i =0
            j+=1
        i+=1

    slogger.info("pre allocate tasks done")
    slogger.info("allocate tasks done")

    time.sleep(max(1, 0.1 * num_machines))

    # generate result quality
    total_social_welfare = 0
    for i in range(0,num_machines):
        total_social_welfare += machines['m'+str(i)].social_welfare
    stop_scheduler()
    print("MDRA social_welfare: ",total_social_welfare);


#    upper = relax_mdp(requests,64,256,num_machines)
#    print("upper bound: ", upper)
    return total_social_welfare

def quality_mdra(num_machines, distribution, corr):
    arr = list(range(1,21))
    arr.append(30)
    arr.append(40)
    arr.append(50)
    arr.append(60)
    arr.append(70)
    arr.append(80)
    arr.append(90)
    arr.append(100)
    result = {}
    for i in arr:
        times = int(num_machines/i)
        sw_i = 0
        for j in range(times):
            sw_i += test_quality(i,distribution, corr)
        sw_i = sw_i / times
        result[i] = sw_i
        print(i," th sw: ", sw_i)

    # write to a file
    with open('/home/augustin/docklet/test_result/quality_mdra_'+distribution +'_'+corr+'_'+str(num_machines)+'.txt','w') as f:    
        for key, task in result.items():
            f.write(str(key) + ' '+ str(result[key]) + '\n')
        f.flush()
        os.fsync(f)
    return

def generate_quality_data(num_machines, distribution, corr):
    os.system("kill -9 $(pgrep acommdkp) > /dev/null 2>&1")
    for i in range(1, num_machines+1):
        generate_test_data(64,256,i,"reliable",distribution,corr,0)

    quality_mdra(num_machines,distribution,corr)
#    os.system("sudo python3 aco-mmdkp/quality_test.py "+distribution + " "+corr)
    
def draw_quality(num_machines, distribution, corr):

    x = list(range(1,21))
    x.append(30)
    x.append(40)
    x.append(50)
    x.append(60)
    x.append(70)
    x.append(80)
    x.append(90)
    x.append(100)
    
    sw1 = []
    sw2 = []
    with open('/home/augustin/docklet/test_result/quality_mdra_'+distribution +'_'+corr+'_'+str(num_machines)+'.txt','r') as f:
        for line in f.readlines()[0:num_machines]:
            arr = line.split()
            sw1.append(arr[1])

    with open('/home/augustin/docklet/test_result/quality_opt_'+distribution +'_'+corr+'_'+str(num_machines)+'.txt','r') as f:
        for line in f.readlines()[0:num_machines]:
            arr = line.split()
            sw2.append(arr[1])

    plt.clf()
    plt.plot(x,sw1,'k-', label='MDRA', color='red')
    plt.plot(x,sw2,'k--', label='Upper Bound', color='blue')
    plt.xlabel('number of machines')
    plt.ylabel('social welfare')
    plt.legend(loc='lower right')
    plt.savefig('quality_1_'+distribution +'_'+corr+'_'+str(num_machines)+".png")

    ratios = []
    for i,v in enumerate(x):
        ratios.append(float(sw1[i]) / float(sw2[i]))

    plt.clf()
    plt.plot(x,ratios,'k-')
    plt.xlabel('number of machines')
    plt.ylabel('ratio of social welfare of MDRA to Upper Bound')
    plt.ylim(0,1)
    plt.savefig('quality_2_'+distribution +'_'+corr+'_'+str(num_machines)+".png")

    with open('/home/augustin/docklet/test_result/quality_mdra_opt_'+distribution +'_'+corr+'_'+str(num_machines)+'.txt','w') as f:
        for i,v in enumerate(x):
            f.write(str(sw1[i-1])+' '+str(sw2[i-1])+'\n')
        f.flush()
        os.fsync(f)

    return

def draw_quality_all():
    x = list(range(1,21))
    x.append(30)
    x.append(40)
    x.append(50)
    x.append(60)
    x.append(70)
    x.append(80)
    x.append(90)
    x.append(100)
    swr1 = []
    swr2 = []
    swr3 = []
    with open('/home/augustin/docklet/test_result/quality_mdra_opt_uniform_corr0_100.txt','r') as f:
        for line in f.readlines()[0:100]:
            arr = line.split()
            swr1.append(float(arr[0]) / float(arr[1]))

    with open('/home/augustin/docklet/test_result/quality_mdra_opt_uniform_corr1_100.txt','r') as f:
        for line in f.readlines()[0:100]:
            arr = line.split()
            swr2.append(float(arr[0]) / float(arr[1]))

    with open('/home/augustin/docklet/test_result/quality_mdra_opt_uniform_corr_opt_100.txt','r') as f:
        for line in f.readlines()[0:100]:
            arr = line.split()
            swr3.append(float(arr[0]) / float(arr[1]))


    plt.clf()
    plt.plot(x,swr1,'k-', label='bids_type_0', color='red')
    plt.plot(x,swr2,'k--', label='bids_type_1', color='blue')
    plt.plot(x,swr3,'k-.', label='bids_type_2', color='purple')
    plt.xlabel('number of machines')
    plt.ylabel('ratio of social welfare of MDRA to Upper Bound')
    plt.ylim(0.9,1)
    plt.legend(loc='lower right')
    plt.savefig('quality_2_all.png')

def test_time_each(num_machines,request_type):
    os.system("kill -9 $(pgrep acommdkp)")
    init_scheduler()
    for i in range(0,num_machines):
        add_machine("m"+str(i),64,256)

    slogger.info("add colonies done!")

    requests = parse_test_data("/home/augustin/docklet/test_data/"+request_type+'_tasks'+str(num_machines)+'.txt',64,256,num_machines,request_type)
    elapsed = 0
    print("begin")
    start = time.time()
    for index,request in requests.items():
        pre_allocate(request)
        allocate(request['id'])

    slogger.info("pre allocate tasks done")
    slogger.info("allocate tasks done")
    print("\n\nallocate done\n\n")
    # generate result quality
    old_total_social_welfare = 0
    new_total_social_welfare = 0
    while True:
        new_total_social_welfare =0
        for i in range(0,num_machines):
            new_total_social_welfare += machines['m'+str(i)].social_welfare
        if old_total_social_welfare == new_total_social_welfare:
            elapsed = time.time()-start
            print("time used:",elapsed)
            break

        else:
            old_total_social_welfare = new_total_social_welfare
            time.sleep(1)
    print("MDRPSPA social_welfare: ",new_total_social_welfare);
    stop_scheduler()
    return elapsed

def test_time():
    x = list(range(1,101))
    times = []
    for i in range(1,101):
        used = test_time_each(i,'uniform')
        times.append(used/8)

    plt.plot(x,times,'k-')
    plt.xlabel('number of machines')
    plt.ylabel('computing time')
    plt.title('Computing time of MDRPSPAA')
    plt.savefig("result3_1.png")

    with open("/home/augustin/docklet/test_result/time_uniform1.txt",'w') as f:
        for i,v in enumerate(x):
            f.write(str(v)+' '+str(times[i])+'\n')
        f.flush()
        os.fsync(f)

def test_time_quality(num_machines,request_type):
    os.system("kill -9 $(pgrep acommdkp)")
    init_scheduler()
    for i in range(0,100):
        add_machine("m"+str(i),64,256)

    slogger.info("add colonies done!")

    requests = parse_test_data("/home/augustin/docklet/test_data/"+request_type+'_tasks'+str(num_machines)+'.txt',64,256,num_machines,request_type)
    elapsed = 0
    print("begin")
    start = time.time()

    times = []
    quality = []
    i = 0
    j=0
    old_total_social_welfare = 0
    for index,request in requests.items():
        pre_allocate(request)
        allocate(request['id'])
        if i == len(requests.items())/num_machines:
            used = time.time()-start
            times.append(used/8)
            old_total_social_welfare = 0
            for i in range(0,num_machines):
                old_total_social_welfare += machines['m'+str(i)].social_welfare
            quality.append(old_total_social_welfare)
            print("part ",j, " done")
            i =0
            j+=1
        i+=1


    while True:
        time.sleep(1)
        new_total_social_welfare =0
        for i in range(0,num_machines):
            new_total_social_welfare += machines['m'+str(i)].social_welfare
        if old_total_social_welfare == new_total_social_welfare:
            break
        else:
            used = time.time()-start
            times.append(used/8)
            quality.append(new_total_social_welfare)
            old_total_social_welfare = new_total_social_welfare
            time.sleep(0.1)

    print("MDRPSPA social_welfare: ",new_total_social_welfare);

    plt.plot(times,quality,'k-')
    plt.xlabel('computing time')
    plt.ylabel('social welfare')
    plt.title('Social welfare changes with time')
    plt.savefig("result3_2.png")
    stop_scheduler()
    return

if __name__ == '__main__':
#    test_pub_socket();
#    test_colony_socket();
#    test_all();
#    generate_multivariate_ca(128,256,100)
#    generate_test_data(128,256,100,"reliable",'ca',0)

# ec2    
#    generate_ec2_1(100,'corr0')
#    generate_ec2_1(100,'corr1')
#    generate_ec2_1(100,'corr_opt')
#    generate_ec2_2(10,'corr1')
#    generate_ec2_1(10,'corr_opt')
#    generate_ec2_2(10,'corr_opt')
#    draw_ec2(100,'corr0')
#    draw_ec2(100,'corr1')
#    draw_ec2(100,'corr_opt')
#    draw_ec2_all(100)

# ca
#    compare_ca_1(100,'ca','corr0')
#    compare_ca_2(10,'ca','corr0')
#    compare_ca_1(100,'ca','corr1')
#    compare_ca_2(10,'ca','corr1')
#    compare_ca_1(100,'ca','corr_opt')
#    compare_ca_2(10,'ca','corr_opt')
#    draw_ca(100,'corr_opt')
#    draw_ca(100,'corr0')
#    draw_ca(100,'corr1')
    draw_ca(100,'ca','corr_opt')
#    draw_ca_all()

# quality
#    generate_quality_data(100,'uniform','corr0')
#    generate_quality_data(100,'uniform','corr1')
#    generate_quality_data(100,'uniform','corr_opt')

#    test_quality(1, 'uniform', 'corr_opt')
#    draw_quality(100,'uniform','corr0')
#    draw_quality(100,'uniform','corr1')
#    draw_quality(100,'uniform','corr_opt')
#    draw_quality_all()

#tmp
#    times = 100
#    sw_i = 0
#    for j in range(times):
#        sw_i += test_quality(1, 'uniform', 'corr_opt')
#    sw_i = sw_i / times
#    print("result", sw_i)
    
#    test_time()
#    test_time_quality(100,'uniform')
#    for i in range(0,10):
#        test_time_each(100,'uniform')
#    generate_test_data(256,480,100,"reliable",'ec2',0)
#    i_sw1,i_sw2 = test_compare_ec2(100,'ec2')
#    generate_multivariate_uniform_optimal(128,256,512)
#    test_compare_ca_stable(50,'ca')
#    i_sw1,i_sw2 = test_compare_ca_stable(1,'ca')
#    for i in range(1,101):
#        print(i)
#        test_generate_test_data(100,'uniform')
#    generate_test_data(64,256,20,"reliable",'uniform',0)
#    test_quality(20,'uniform')
#        generate_test_data(64,256,i,"reliable",'binomial',0)
