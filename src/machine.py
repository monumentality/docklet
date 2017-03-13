# coding = UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-

import string
from connection import *
import logging
import nodemgr

slogger = logging.getLogger("scheduler")

class AllocationOfMachine(object):
    # total_value: sum of the value of reliable resource request
    __slots__ = ['machineid',"resources","reliable_available",
                 'reliable_allocations', 'restricted_allocations',
                 'cpus','mems','total_value','tasks','colony','total_value_invert',
                 'cpus_wanted','mems_wanted']

    # if not full, allocate tasks derectly
    def add_reliable_task(self,task):

        task['machine']=self
        self.tasks[task['id']] = task



        self.cpus_wanted += task['cpus']
        self.mems_wanted += task['mems']

        if(self.cpus_wanted < self.cpus and self.mems_wanted < self.mems):
            self.allocate_reliable(task)
            self.reliable_allocations.append(task['id'])
        else:
            self.allocate_restricted(task)
            self.restricted_allocations.append(task['id'])
        return task

    def allocate_reliable(self,task):
        task['allocation_type'] = 'reliable'
        task['allocation_cpus'] = task['cpus']
        task['allocation_mems'] = task['mems']
        task['allocation_mems_sw'] = str( 2 * int(task['mems']) )
        task['allocation_mems_soft'] = str( 2 * int(task['mems']) )


    def allocate_restricted(self,task):
        task['allocation_type'] = 'restricted'
        task['allocation_cpus'] = task['cpus']
        task['allocation_mems'] = task['mems']
        task['allocation_mems_sw'] = str( 2 * int(task['mems']) )
        task['allocation_mems_soft'] = str( 2 * int(task['mems']) )

    def add_restricted_task(self, task):
        task['machine'] = self
        self.tasks[task['id']] = task

        # to-do:
        # if resource utilization is not higher then threshold, then allocate!
        self.restricted_allocations.append(task['id'])
        self.allocate_restricted(task)

        return task

    def release_reliable_task(self,id):

        self.cpus_wanted -= self.tasks[id]['cpus']
        self.mems_wanted -= self.tasks[id]['mems']

        if id in self.reliable_allocations:
            self.reliable_allocations.remove(id)
        if id in self.restricted_allocations:
            self.restricted_allocations.remove(id)

        del self.tasks[id]
        



    def release_restricted_task(self,id):
        del self.tasks[id]
        self.restricted_allocations.remove(id)

    def change_reliable_allocations(self,result_str):
#        slogger.debug("change result! new result: %s" % result_str)
        result_arr = result_str.split(" ")

        to_move_out_reliable = []
        to_add_into_reliable = result_arr[:]

        for old in self.reliable_allocations:
            if old in result_arr:
                to_add_into_reliable.remove(old)
            else:
                to_move_out_reliable.append(old)


        for out in to_move_out_reliable:

            self.allocate_restricted(self.tasks[out])
            self.change_cgroup_settings(self.tasks[out])
            self.tasks[out]['allocation_type']="restricted"
            self.restricted_allocations.append(out)
            self.reliable_allocations.remove(out)

        for into in to_add_into_reliable:
            # not used yet
            if self.tasks[into]["allocation_type"]=="none":
#                self.create_reliable(self.tasks[into])
                slogger.info('\n\nshould not be here\n\n')
            else:
                self.restricted_allocations.remove(into)

                self.allocate_reliable(self.tasks[into])
                self.change_cgroup_settings(self.tasks[into])

            self.reliable_allocations.append(into)
            self.tasks[into]["allocation_type"]=="reliable"

    def change_cgroup_settings(self,task):
        global node_manager
#        node_manager.ip_to_rpc(self.id).change_cgroup_settings(task)

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
