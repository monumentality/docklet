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
from dmachine_test import AllocationOfMachine
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

def generate_multivariate_uniform(cpu,mem,num_tasks):
    mean = [0, 0, 0]
    cov = [[1, -0.5, 0.5], [-0.5, 1, 0.5], [0.5, 0.5, 1]]
    x, y, z = np.random.multivariate_normal(mean, cov, num_tasks).T

    cpus = []
    mems = []
    values = []
    for ix in x:
        cpus.append(norm.cdf(ix)*(cpu/4-1)+1)

    for iy in y:
        mems.append(norm.cdf(iy)*(mem/4-1)+1)

    for iz in z:
        values.append(norm.cdf(iz)*(100-1)+1)

    return cpus,mems,values

def generate_multivariate_binomial(cpu,mem,num_tasks):
    mean = [0, 0, 0]
    cov = [[1, -0.5, -0.5], [-0.5, 1, -0.5], [-0.5, -0.5, 1]]
    x, y, z = np.random.multivariate_normal(mean, cov, num_tasks).T

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

def generate_multivariate_ec2(cpu,mem,num_tasks):
    mean = [0, 0, 0]
    cov = [[1, -0.5, 0.5], [-0.5, 1, 0.5], [0.5, 0.5, 1]]
    x, y, z = np.random.multivariate_normal(mean, cov, num_tasks).T

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

def generate_test_data(cpu,mem,machines,request_type,distribution,id_base):
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
        cpu_arr, mem_arr,bids = generate_multivariate_uniform(cpu,mem,num_tasks)
    elif distribution == 'ec2':
        num_tasks = int(cpu/4 * machines)
#        cpu_arr = np.random.uniform(1,cpu,cpu*machines)
#        mem_arr = np.random.uniform(1,mem,cpu*machines)
        cpu_arr, mem_arr,bids = generate_multivariate_ec2(cpu,mem,num_tasks)

    elif distribution == 'ca':
        num_tasks = int(32 * machines)
        cpu_arr,mem_arr,bids = generate_multivariate_uniform(cpu,mem,num_tasks)

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
#            print(task)
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
    global queue_lock
    if 'bid' in task and task['bid']!='0':
        queue_lock.acquire()
        machine = heapq.heappop(machine_queue)

        task['machineid'] = machine.machineid

        task['allocation_type'] = 'none'
        task['allocation_cpus'] = str(int(task['cpus'])*1000)
        task['allocation_mems'] = task['mems']
        task['allocation_mems_sw'] = str( 2 * int(task['mems']) )
        task['allocation_mems_soft'] = str( 2 * int(task['mems']) )
        tasks[task['id']] = task

        machine.pre_cpus_wanted += int(task['cpus'])
        machine.pre_mems_wanted += int(task['mems'])

        if(machine.pre_cpus_wanted <= machine.reliable_cpus and machine.pre_mems_wanted <= machine.reliable_mems):
            machine.placement_heu +=int(task['bid'])
        else:
            if machine.mem_value == 0:
                machine.mem_value = machine.placement_heu/(machine.rareness_ratio * machine.reliable_cpus + machine.reliable_mems)
                machine.cpu_value = machine.mem_value * machine.rareness_ratio
            heu_incre = int(task['bid']) - int(task['cpus'])* machine.cpu_value - int(task['mems'])*machine.mem_value
            if heu_incre > 0:
                machine.placement_heu += heu_incre

        heapq.heappush(machine_queue,machine)
#        time.sleep(0.1)
        queue_lock.release()
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
    print("stop scheduler")
    queue_lock.acquire()
    os.system("kill -9 $(pgrep acommdkp)")
    time.sleep(3)
    print("close sockets")
    close_sync_socket()
    close_colony_socket()
    close_task_socket()
    import dconnection
    dconnection.recv_run = False
    queue_lock.release()
    time.sleep(1)

def init_scheduler():
    global queue_lock
    #启动c程序，后台运行
    os.system("rm -rf /home/augustin/docklet/src/aco-mmdkp.log")
    os.system("/home/augustin/docklet/src/aco-mmdkp/acommdkp >/home/augustin/docklet/src/aco-mmdkp.log 2>&1 &")
    time.sleep(3)
    slogger.setLevel(logging.INFO)
    slogger.info("init scheduler!")
    print("init scheduler")
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

def test_quality(num_machines,request_type):
    os.system("kill -9 $(pgrep acommdkp)")
    init_scheduler()
    for i in range(0,num_machines):
        add_machine("m"+str(i),64,256)

#    Time.sleep(1)
    slogger.info("add colonies done!")

#    requests = generate_test_data(64,256,2,"reliable",'uniform',0)
#    generate_test_data(64,256,1,"restricted",192)

    requests = parse_test_data("/home/augustin/docklet/test_data/"+request_type+'_tasks'+str(num_machines)+'.txt',64,256,num_machines,request_type)

    i = 0
    j=0
    for index,request in requests.items():
        pre_allocate(request)
        allocate(request['id'])
        if i == len(requests.items())/num_machines/2:
            time.sleep(1)
            print("part ",j, " done")
            i =0
            j+=1
        i+=1

    slogger.info("pre allocate tasks done")
    slogger.info("allocate tasks done")

    time.sleep(10)

    # generate result quality
    total_social_welfare = 0
    for i in range(0,num_machines):
        total_social_welfare += machines['m'+str(i)].social_welfare
    stop_scheduler()
    print("MDRPSPA social_welfare: ",total_social_welfare);

    return total_social_welfare
#    upper = relax_mdp(requests,64,256,num_machines)
#    print("upper bound: ", upper)


def test_generate_test_data(num,request_type):
    for i in range(1,num+1):
        print(i)
        generate_test_data(64,256,i,"reliable",request_type,0)

def test_compare_ec2(num_machines, request_type):
    os.system("kill -9 $(pgrep acommdkp)")
    time.sleep(3)
    init_scheduler()
    for i in range(0,num_machines):
        add_machine("m"+str(i),256,480)
    slogger.info("add colonies done!")
    time.sleep(1)
    requests = parse_test_data("/home/augustin/docklet/test_data/"+request_type+'_tasks'+str(num_machines)+'.txt',256,480,num_machines,request_type)

    i = 0
    j=0
    for index,request in requests.items():
        pre_allocate(request)
        allocate(request['id'])
        if i == len(requests.items())/num_machines*2:
            time.sleep(0.5)
            print("part ",j, " done")
            i =0
            j+=1
        i+=1

    slogger.info("pre allocate tasks done")
    slogger.info("allocate tasks done")

    time.sleep(10)

    # generate result quality
    total_social_welfare = 0
    for i in range(0,num_machines):
        print('m'+str(i)+": social_welfare", machines['m'+str(i)].social_welfare)
        print('m'+str(i)+": heu", machines['m'+str(i)].placement_heu)
        total_social_welfare += machines['m'+str(i)].social_welfare

    print("MDRPSPA social_welfare: ",total_social_welfare);
    ec2_social_welfare = 0
    newlist = sorted(list(requests.values()), key=lambda k: k['bid'],reverse=True)
    for i in range(0,32*num_machines):
        ec2_social_welfare += int(newlist[i]['bid'])

    print("ec2 social_welfare: ",ec2_social_welfare)
#    upper = relax_mdp(requests,256,480,num_machines)
#    print("upper bound: ", upper)

    stop_scheduler()
    return total_social_welfare, ec2_social_welfare

def test_compare_ca(num_machines, request_type):
    os.system("kill -9 $(pgrep acommdkp)")
    time.sleep(3)
    init_scheduler()
    for i in range(0,num_machines):
        add_machine("m"+str(i),128,256)
    slogger.info("add colonies done!")
    time.sleep(1)
    requests = parse_test_data("/home/augustin/docklet/test_data/"+request_type+'_tasks'+str(num_machines)+'.txt',128,256,num_machines,request_type)

    i = 0
    j=0
    for index,request in requests.items():
        pre_allocate(request)
        allocate(request['id'])
        if i == len(requests.items())/num_machines*2:
            time.sleep(0.5)
            print("part ",j, " done")
            i =0
            j+=1
        i+=1

    slogger.info("pre allocate tasks done")
    slogger.info("allocate tasks done")

    time.sleep(10)

    # generate result quality
    total_social_welfare = 0
    for i in range(0,num_machines):
        print('m'+str(i)+": social_welfare", machines['m'+str(i)].social_welfare)
        print('m'+str(i)+": heu", machines['m'+str(i)].placement_heu)
        total_social_welfare += machines['m'+str(i)].social_welfare

    print("MDRA social_welfare: ",total_social_welfare);

    # calculate ca-provision social welfare
    ca_social_welfare = 0
    vmbids = []
    for index,request in requests.items():
        vmbid = {}
        num_vm = max(int(request['cpus']), math.ceil(int(request['mems'])/2))
        vmbid['vms'] = num_vm
        vmbid['bid'] = int(request['bid'])/num_vm
        vmbids.append(vmbid)
    newlist = sorted(vmbids, key=lambda k: k['bid'],reverse=True)
    total_capacity = 128*num_machines
    utilized = 0
    for index, vmbid in newlist:
        utilized += vmbids[i]['vms']
        if utilized <= total_capacity:
            ca_social_welfare += vmbids[i]['bid']* vmbids[i]['vms']
        else:
            break

    print("ca social_welfare: ",ca_social_welfare)
#    upper = relax_mdp(requests,256,480,num_machines)
#    print("upper bound: ", upper)

    stop_scheduler()
    return total_social_welfare, ec2_social_welfare

def generate_test11_result(num):
    sw1 = []
    sw2 = []
    for i in range(1,num):
        generate_test_data(256,480,i,"reliable",'ec2',0)
        i_sw1,i_sw2 = test_compare_ec2(i,'ec2')
        sw1.append(i_sw1)
        sw2.append(i_sw2)
    plt.plot(range(1,num),sw1,color='red')
    plt.plot(range(1,num),sw2,color='blue')
    plt.xlabel('number of machines')
    plt.ylabel('social welfare')
    plt.title('Compare Social Welfare of  MDRPSPA with EC2')
    plt.legend()
    plt.savefig("result1.png")

    with open("/home/augustin/docklet/test_result/compare_with_ec2.txt",'w') as f:
        for i in range(1,num):
            f.write(str(sw1[i-1])+' '+str(sw2[i-1])+'\n')
        f.flush()
        os.fsync(f)

def generate_test12_result():
    ratios = []
    with open("/home/augustin/docklet/test_result/compare_with_ec2.txt",'r') as f:
        for line in f.readlines()[0:99]:
            arr = line.split()
            ratio = float(arr[0])/float(arr[1])
            ratios.append(ratio)

    print(len(ratios))
    plt.plot(np.array(range(1,100)),np.array(ratios),'k-')
    plt.xlabel('number of machines')
    plt.ylabel('Ratio of Social welfare of MDRPSPA to EC2')
    plt.title('Ratio of Social Welfare of  MDRPSPA to EC2')
    plt.savefig("result12.png")

def draw_test1_result():
    ratios = []
    sw1 = []
    sw2 = []
    with open("/home/augustin/docklet/test_result/compare_with_ec2.txt",'r') as f:
        for line in f.readlines()[0:99]:
            arr = line.split()
            ratio = float(arr[0])/float(arr[1])
            ratios.append(ratio)
            sw1.append(float(arr[0]))
            sw2.append(float(arr[1]))

    plt.figure(1)
    plt.plot(range(1,100),sw1,'k-',label='MDRPSPA')
    plt.plot(range(1,100),sw2,'k--',label='EC2')
    plt.xlabel('number of machines')
    plt.ylabel('social welfare')
    plt.title('Compare Social Welfare of  MDRPSPA with EC2')
    plt.legend(loc ='upper left')
    plt.savefig("result1_1.png")


    plt.figure(2)
    plt.plot(np.array(range(1,100)),np.array(ratios),'k-')
    plt.xlabel('number of machines')
    plt.ylabel('Ratio of Social welfare of MDRPSPA to EC2')
    plt.title('Ratio of Social Welfare of  MDRPSPA to EC2')
    plt.savefig("result1_2.png")


def generate_test21_result():
    arr = list(range(1,21))
    arr.append(30)
    arr.append(40)
    arr.append(50)
    arr.append(100)
    result = {}
    for i in arr:
        result[i] =test_quality(i,'uniform')

    # write to a file
    with open("/home/augustin/docklet/test_result/quality_uniform_mdrpspa1.txt",'w') as f:
        for key, task in result.items():
            f.write(str(key) + ' '+ str(result[key]) + '\n')

        f.flush()
        os.fsync(f)
    return

def draw_test2_result():
    x = list(range(1,21))
    x.append(30)
    x.append(40)
    x.append(50)
    x.append(100)
    sw1 = []
    sw2 = []
    with open('/home/augustin/docklet/test_result/quality_uniform_mdrpspa1.txt','r') as f:
        for line in f.readlines()[0:24]:
            arr = line.split()
            sw1.append(arr[1])

    with open('/home/augustin/docklet/test_result/quality_uniform_opt1.txt','r') as f:
        for line in f.readlines()[0:24]:
            arr = line.split()
            sw2.append(arr[1])

    plt.figure(1)
    plt.plot(x,sw1,'k-', label='MDRPSPAA')
    plt.plot(x,sw2,'k--', label='Upper Bound')
    plt.xlabel('number of machines')
    plt.ylabel('social welfare')
    plt.title('Compare Social Welfare of  MDRPSPAA with Upper Bound')
    plt.legend(loc='upper left')
    plt.savefig("result2_1.png")

    ratios = []
    for i,v in enumerate(x):
        ratios.append(float(sw1[i]) / float(sw2[i]))

    plt.figure(2)
    plt.plot(x,ratios,'k-')
    plt.xlabel('number of machines')
    plt.ylabel('ratio of MDRPSPAA to Upper Bound')
    plt.title('Ratio of  Social Welfare of  MDRPSPA to Upper Bound')
    plt.savefig("result2_2.png")

    with open("/home/augustin/docklet/test_result/quality_uniform1.txt",'w') as f:
        for i,v in enumerate(x):
            f.write(str(sw1[i-1])+' '+str(sw2[i-1])+'\n')
        f.flush()
        os.fsync(f)

    return

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
#    generate_multivariate_ec2(64,256,10)
#    generate_test_data(256,480,10,"reliable",'ec2',0)
#    generate_test11_result()
#    generate_test12_result()
#    draw_test2_result()
#    draw_test1_result()
#    test_time()
    test_time_quality(100,'uniform')
#    for i in range(0,10):
#        test_time_each(100,'uniform')
#    generate_test_data(256,480,100,"reliable",'ec2',0)
#    i_sw1,i_sw2 = test_compare_ec2(100,'ec2')
#    for i in range(1,101):
#        print(i)
#        test_generate_test_data(100,'uniform')
#    generate_test_data(64,256,20,"reliable",'uniform',0)
#    test_quality(20,'uniform')
#        generate_test_data(64,256,i,"reliable",'binomial',0)
