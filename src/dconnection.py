# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-

import zmq
import time
from log import slogger
import heapq
import sys
import threading

task_ctx = None
task_s = None

colony_ctx = None
colony_s = None

result_ctx = None
result_s = None

sync_ctx = None
sync_s = None

recv_stop = False

def init_task_socket():
    global task_ctx
    global task_s
    bind_to = "tcp://*:5000"
    task_ctx = zmq.Context().instance()
    task_s = task_ctx.socket(zmq.PUB)
    task_s.bind(bind_to)

def close_task_socket():
    global task_ctx
    global task_s
    if not task_ctx.closed:
        task_ctx.destroy(0)
    if not task_s.closed:
        task_s.setsockopt( zmq.LINGER, 0 )
        task_s.close(0)

    
def init_sync_socket():
    global sync_ctx
    global sync_s

    sync_with = "tcp://*:5001"
    sync_ctx = zmq.Context.instance()
    slogger.debug("ctx max_sockets: %d",sync_ctx.get(zmq.MAX_SOCKETS))
    sync_ctx.set(zmq.MAX_SOCKETS, 65536)
    slogger.debug("ctx max_sockets: %d",sync_ctx.get(zmq.MAX_SOCKETS))
    sync_s = sync_ctx.socket(zmq.REP)
    sync_s.bind(sync_with)
    slogger.debug("Waiting for subscriber to connect...")

def close_sync_socket():
    global sync_ctx
    global sync_s
    if not sync_ctx.closed:
        sync_ctx.destroy(0)
    if not sync_s.closed:
        sync_s.setsockopt( zmq.LINGER, 0 )
        sync_s.close(0)

def sync_colony():
    id = sync_s.recv_string()
    slogger.debug("done sync with %s", id)
    sync_s.send_string("sync success")
    slogger.info("colony %s synced",id);

def send_task(machineid,task, oper):
    global task_s
#    print("send task: %s %s:" % (machineid, task['id']))
#    slogger.debug("Sending new task %s to machine %s, operation:%s  ... " ,task['id'],  machine.machineid, oper)
    task_s.send_string(machineid + " ",zmq.SNDMORE)
    task_s.send_string(str(task['id']),zmq.SNDMORE)
    task_s.send_string(str(task['cpus']),zmq.SNDMORE)
    task_s.send_string(str(task['mems']),zmq.SNDMORE)
    task_s.send_string(str(task['bid']),zmq.SNDMORE)
    task_s.send_string(oper)

#    slogger.debug("Done.")

def init_colony_socket():
    global colony_ctx
    global colony_s
    colony_ctx = zmq.Context.instance()
    colony_s = colony_ctx.socket(zmq.REQ)
    colony_s.connect("tcp://localhost:5002")
    slogger.debug("colony socket ready")
    colony_s.send_string("colony socket ready")
    sync_result = colony_s.recv_string()
    slogger.info("colony sync_result: %s",sync_result)

def close_colony_socket():
    global colony_ctx
    global colony_s
    if not colony_ctx.closed:
        colony_ctx.destroy(0)
    if not colony_s.closed:
        colony_s.setsockopt( zmq.LINGER, 0 )
        colony_s.close(0)
    
def send_colony(oper, id, cpus, mems,):
    colony_s.send_string(oper,zmq.SNDMORE)
    colony_s.send_string(id,zmq.SNDMORE)
    colony_s.send_string(cpus,zmq.SNDMORE);
    colony_s.send_string(mems);
    reply = colony_s.recv_string()
    slogger.debug("create colony %s reply: %s",id,reply)

def init_result_socket():
    global result_ctx
    global result_s
    result_ctx = zmq.Context.instance()

    slogger.debug("ctx max_sockets: %d",result_ctx.get(zmq.MAX_SOCKETS))
    result_ctx.set(zmq.MAX_SOCKETS, 65536)
    slogger.debug("ctx max_sockets: %d",result_ctx.get(zmq.MAX_SOCKETS))

    result_s = result_ctx.socket(zmq.REP)
    result_s.bind("tcp://*:5003")
    slogger.info("result recv socklet created!")

def close_result_socket():
    global result_ctx
    global result_s
    if not result_ctx.closed:
        result_ctx.destroy(0)
    if not result_s.closed:
        result_s.setsockopt( zmq.LINGER, 0 )
        result_s.close(0)


def recv_result(machines,machine_queue,lock):
    global result_s
    global result_ctx
    global recv_stop
    
    while(not recv_stop):
        try:
#            print("stop: ", recv_stop)
            slogger.debug("waiting for result!")
            machineid = result_s.recv_string()
            solution_str = result_s.recv_string()
            mem_value_str = result_s.recv_string()
            ratio_str = result_s.recv_string()
            
            mem_value = float(mem_value_str)
            ratio = float(ratio_str)
            slogger.info("recv_string result of machine %s: %s %e %e", machineid, solution_str, mem_value, ratio)
            
            result_s.send_string("success")
            machine = machines[machineid]
            machine.mem_value = mem_value
            machine.cpu_value = mem_value * ratio
            machine.rareness_ratio = ratio
            machine.change_reliable_allocations(solution_str);
            print("recv result machineid: %s %e" % (machineid, machine.social_welfare))

            print("machine queue length: ", len(machine_queue))
#            for m in listmachine_queue:
#                if m.machineid == machine.machineid:
#                    machine_queue.remove(m)
#                    print("change")
#                    break
#            print("machine queue length: ", len(machine_queue))
            lock.acquire()
            machine_queue.remove(machine)
            heapq.heappush(machine_queue,machine)
            lock.release()
            print("machine queue length: ", len(machine_queue))
#            print("change machine_queue done!")
        except Exception as e:
            print("except: ",e)
            recv_stop = True
#            close_result_socket()
            break
    return

#    print("stop: ", recv_stop)
#    result_s.setsockopt( zmq.LINGER, 0 )
#    result_s.close()
#    result_ctx.term()
#    print("recv closed")
    
def test_pub_socket():
    generate_test_data(64,256,1)
#    tasks = parse_test_data()
    init_machines(64, 256, 1)
    dispatch(tasks);
#    test3()

def test_colony_socket():
    init_mmdkp_socket()
    send_colony("add","0","64","256")
