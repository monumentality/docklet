# coding = UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-

import string
import logging
from log import slogger
import math

class AllocationOfMachine(object):
    # total_value: sum of the value of reliable resource request
#    __slots__ = ['machineid',"resources","reliable_available",
#                 'reliable_allocations', 'restricted_allocations',
#                 'cpus','mems','total_value','tasks','colony','total_value_invert',
#                 'reliable_cpus', 'reliable_mems','restricted_cpus','restricted_mems',
#                 'reliable_cpus_wanted','reliable_mems_wanted']

    def __init__(self, id, cpus =24, mems=240000, reliable_ratio = 0.5):
        self.machineid = id
        self.cpus = int(cpus)
        self.mems = int(mems)
        self.reliable_cpus = math.ceil(self.cpus * reliable_ratio)
        self.reliable_mems = math.ceil(self.mems * reliable_ratio)
        self.restricted_cpus = self.cpus - self.reliable_cpus
        self.restricted_mems = self.mems - self.reliable_mems

        self.tasks = {}
        self.total_value = 0
        
        self.reliable_cpus_wanted = 0
        self.reliable_mems_wanted = 0

        # init allocation data
        self.reliable_allocations = []
        self.restricted_allocations = []


    def add_reliable_task(self,task):

        self.tasks[task['id']] = task

        self.reliable_cpus_wanted += int(task['cpus'])
        self.reliable_mems_wanted += int(task['mems'])
#        slogger.info("reliable_cpus/mems: %d %d %d %d", self.reliable_cpus, self.reliable_mems, self.reliable_cpus_wanted, self.reliable_mems_wanted)
        # if not full, allocate reliable, else allocate restricted directly
        if(self.reliable_cpus_wanted <= self.reliable_cpus and self.reliable_mems_wanted <= self.reliable_mems):
#            slogger.info("allocate reliable resource to task, id: %s",task['id'])
            self.allocate_reliable(task)
            self.reliable_allocations.append(task['id'])
        else:
#            slogger.info("allocate restricted resource to task, id: %s",task['id'])
            self.restricted_allocations.append(task['id'])
            self.reallocate_restricted()
        return task

    def allocate_reliable(self,task):

        task['allocation_type'] = 'reliable'
        task['allocation_cpus'] = str(int(task['cpus'])*1000)
        task['allocation_mems'] = task['mems']
        task['allocation_mems_sw'] = str( 2 * int(task['mems']) )
        task['allocation_mems_soft'] = task['mems']


    def reallocate_restricted(self):
        if not self.restricted_allocations:
            return

        import dscheduler
        total_restricted_cpus = 0
        total_restricted_mems = 0
        for id in self.restricted_allocations:
            total_restricted_cpus += int(self.tasks[id]['cpus'])
            total_restricted_mems += int(self.tasks[id]['mems'])
        for id in self.restricted_allocations:
            task = self.tasks[id]
            task['allocation_type'] = 'restricted'

            weighted_cpus  = math.floor(float(task['cpus']) * 1000/ total_restricted_cpus * self.restricted_cpus)
            task['allocation_cpus'] = str(min(int(task['cpus'])* 1000, weighted_cpus))

            weighted_mems  = math.floor(float(task['mems']) / total_restricted_mems * self.restricted_mems)
            task['allocation_mems_soft'] = str(min(int(task['mems']), weighted_mems))

            task['allocation_mems'] = task['mems']
            task['allocation_mems_sw'] = str( 2 * int(task['mems']))

#            slogger.info("change cgroup settings of restricted task: %s", id)
            self.change_cgroup_settings(task)
            

    def add_restricted_task(self, task):

        self.tasks[task['id']] = task
        # to-do:
        # if resource utilization is not higher then threshold, then allocate!
#        slogger.info("allocate restricted resource to task, id: %s",task['id'])
        self.restricted_allocations.append(task['id'])
        self.reallocate_restricted()

        return task

    def release_reliable_task(self,id):

        self.reliable_cpus_wanted -= int(self.tasks[id]['cpus'])
        self.reliable_mems_wanted -= int(self.tasks[id]['mems'])

        if id in self.reliable_allocations:
#            slogger.info("release reliable resources of task:%s",id)
            self.reliable_allocations.remove(id)

        if id in self.restricted_allocations:
#            slogger.info("release restricted resources of task:%s",id)
            self.restricted_allocations.remove(id)
            self.reallocate_restricted()
        del self.tasks[id]
        
        # if not full, change restricted to reliable, and change mem_value/cpu_value
        if self.reliable_cpus_wanted <= self.reliable_cpus and self.reliable_mems_wanted <= self.reliable_mems:
            for id in self.restricted_allocations:
                task = self.tasks[id]
                if 'bid' in task and task['bid']!='0':
#                    slogger.info("change task %s from restricted to reliable", id)
                    self.restricted_allocations.remove(id)
                    
                    self.allocate_reliable(task)
                    self.reliable_allocations.append(task['id'])
#                    slogger.info("change cgroup settings of reliable task:%s", id)

                    self.change_cgroup_settings(task)

            self.reallocate_restricted()

        
    def release_restricted_task(self,id):
#        slogger.info("release restricted resources of task:%s", id)
        self.restricted_allocations.remove(id)
        self.reallocate_restricted()
        del self.tasks[id]

    def change_reliable_allocations(self,result_str):
#        slogger.debug("change result! new result: %s", result_str)
        result_arr = result_str.split(" ")

        to_move_out_reliable = []
        to_add_into_reliable = result_arr[:]

        for old in self.reliable_allocations:
            if old in result_arr:
                to_add_into_reliable.remove(old)
            else:
                to_move_out_reliable.append(old)


        # change out to restricted 
        for out in to_move_out_reliable:
#            slogger.info("change task %s from reliable to restricted",out)
#            self.tasks[out]['allocation_type']="restricted"
            self.restricted_allocations.append(out)
            self.reliable_allocations.remove(out)

            
        # change into to reliable
        for into in to_add_into_reliable:
            # not used yet
            if self.tasks[into]["allocation_type"]=="none":
#                self.create_reliable(self.tasks[into])
                slogger.info('\n\nshould not be here\n\n')
            else:
#                slogger.info("change task %s from restricted to reliable", into) 
                self.restricted_allocations.remove(into)

                
                self.allocate_reliable(self.tasks[into])
#                slogger.info("change cgroup settings of reliable task:%s", into)
                self.change_cgroup_settings(self.tasks[into])
                
            self.reliable_allocations.append(into)
#            self.tasks[into]["allocation_type"]=="reliable"

        self.reallocate_restricted()

    def change_cgroup_settings(self,task):
        import dscheduler
        dscheduler.node_manager.ip_to_rpc(self.machineid).change_cgroup_settings(task)


    def __lt__(self, other):
        if self.total_value < other.total_value:
            return True
        else:
            return False
    def __le__(self, other):
        if self.total_value <= other.total_value:
            return True
        else:
            return False
    def __eq__(self, other):
        if self.total_value == other.total_value:
            return True
        else:
            return False
    def __ne__(self, other):
        if self.total_value != other.total_value:
            return True
        else:
            return False
    def __gt__(self, other):
        if self.total_value > other.total_value:
            return True
        else:
            return False
    def __ge__(self, other):
        if self.total_value >=  other.total_value:
            return True
        else:
            return False
