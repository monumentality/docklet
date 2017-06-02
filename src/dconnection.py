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
result_sub = None
result_poller = None

sync_ctx = None
sync_s = None

recv_run = True

def init_task_socket():
    global task_ctx
    global task_s
    bind_to = "tcp://*:5000"
    task_ctx = zmq.Context().instance()
    task_s = task_ctx.socket(zmq.PUB)
    task_s.setsockopt(zmq.LINGER,0)
    task_s.bind(bind_to)

def close_task_socket():
    global task_ctx
    global task_s
    
    if not task_s.closed:
        task_s.setsockopt( zmq.LINGER, 0 )
        task_s.close(0)
    if not task_ctx.closed:
        task_ctx.term()


    
def init_sync_socket():
    global sync_ctx
    global sync_s

    sync_with = "tcp://*:5001"
    sync_ctx = zmq.Context.instance()
    slogger.debug("ctx max_sockets: %d",sync_ctx.get(zmq.MAX_SOCKETS))
    sync_ctx.set(zmq.MAX_SOCKETS, 65536)
    slogger.debug("ctx max_sockets: %d",sync_ctx.get(zmq.MAX_SOCKETS))
    sync_s = sync_ctx.socket(zmq.REP)
    sync_s.setsockopt(zmq.LINGER,0)
    sync_s.bind(sync_with)
    slogger.debug("Waiting for subscriber to connect...")

def close_sync_socket():
    global sync_ctx
    global sync_s
    if not sync_s.closed:
        sync_s.setsockopt(zmq.LINGER,0)
        sync_s.close(0)
    if not sync_ctx.closed:
        sync_ctx.destroy(0)


def sync_colony():
    global sync_ctx
    global sync_s
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
    colony_s.setsockopt(zmq.LINGER,0)
    colony_s.connect("tcp://localhost:5002")
    slogger.debug("colony socket ready")
    colony_s.send_string("colony socket ready")
    sync_result = colony_s.recv_string()
    slogger.info("colony sync_result: %s",sync_result)

def close_colony_socket():
    global colony_ctx
    global colony_s
    if not colony_s.closed:
        colony_s.setsockopt( zmq.LINGER, 0 )
        colony_s.close(0)
    if not colony_ctx.closed:
        colony_ctx.term()
    
def send_colony(oper, id, cpus, mems,):
    colony_s.send_string(oper,zmq.SNDMORE)
    colony_s.send_string(id,zmq.SNDMORE)
    colony_s.send_string(cpus,zmq.SNDMORE);
    colony_s.send_string(mems);
    reply = colony_s.recv_string()
    slogger.debug("create colony %s reply: %s",id,reply)

def init_result_socket():
    global result_ctx
    global result_sub
    global result_poller
    global recv_run

    recv_run = True
    result_ctx = zmq.Context.instance()

    slogger.debug("ctx max_sockets: %d",result_ctx.get(zmq.MAX_SOCKETS))
    result_ctx.set(zmq.MAX_SOCKETS, 65536)
    slogger.debug("ctx max_sockets: %d",result_ctx.get(zmq.MAX_SOCKETS))
    
    result_sub = result_ctx.socket(zmq.REP)
    result_sub.bind("tcp://*:5003")
#    result_sub.setsockopt_string(zmq.SUBSCRIBE, u"result ")
    result_poller = zmq.Poller()
    result_poller.register(result_sub,zmq.POLLIN)
    
    slogger.info("result recv socklet created!")

def close_result_socket():
    global result_ctx
    global result_sub
    global result_poller
    result_poller.unregister(result_sub)
    result_poller = None
    if not result_sub.closed:
        result_sub.setsockopt( zmq.LINGER, 0 )
        result_sub.close(0)
    if not result_ctx.closed:
        result_ctx.term()

    
def recv_result(machines,machine_queue,lock):
    global result_sub
    global result_ctx
    global recv_run
    global result_poller
    global recv_stop
    while recv_run:
#        print("recv_run:",recv_run)
        try:
            lock.acquire()
            if not recv_run:
                lock.release()
                break;
            sockets = dict(result_poller.poll(0))
            if result_sub in sockets:
                slogger.debug("waiting for result!")
                topic = result_sub.recv_string()
                machineid = result_sub.recv_string()
                solution_str = result_sub.recv_string()
                mem_value_str = result_sub.recv_string()
                ratio_str = result_sub.recv_string()
                
                mem_value = float(mem_value_str)
                ratio = float(ratio_str)
                slogger.info("recv_string result of machine %s: %s %e %e", machineid, solution_str, mem_value, ratio)
                
                machine = machines[machineid]
                machine.mem_value = mem_value
                machine.cpu_value = mem_value * ratio
                machine.rareness_ratio = ratio
                machine.change_reliable_allocations(solution_str);
                print("recv result machineid: %s %e" % (machineid, machine.social_welfare))

                result_sub.send_string("success")
                 

                machine_queue.remove(machine)
                heapq.heappush(machine_queue,machine)
                lock.release()

            else:
                lock.release()
                time.sleep(0.1)
        except Exception as e:
            lock.release()
            print("recv thread except: ",e)
            recv_run = False
            break
    print("recv stop")
    close_result_socket()
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
