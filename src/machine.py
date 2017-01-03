# coding = UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-

import string
from connection import *
import logging

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

        self.total_value += task['price']

        self.cpus_wanted += task['cpus']
        self.mems_wanted += task['mems']
        if(self.cpus_wanted < self.cpus and self.mems_wanted < self.mems):
            self.reliable_allocations.append(task['id'])
#            create_reliable(task)

    def add_restricted_task(self, task):
        task['machine'] = self
        self.tasks[task['id']] = task

        # to-do:
        # if resource utilization is not higher then threshold, then allocate!
        if(True):
            self.restricted_allocations.append(task['id'])
#            create_restricted(task)

    def release_reliable_task(self,task):
        self.tasks[task['id']] = task

        self.total_value -= task['price']
        self.cpus_wanted -= task['cpus']
        self.mems_wanted -= task['mems']

        if task['id'] in self.reliable_allocations:
            self.reliable_allocations.remove(task['id'])
        if task['id'] in self.restricted_allocations:
            self.restricted_allocations.remove(task['id'])

        send_task(self,task,"delete")
#        release_reliable(task)

    def release_restricted_task(self,task):
        self.tasks[task['id']] = task

        # to-do:
        # if resource utilization is not higher then threshold, then allocate!
        self.restricted_allocations.remove(task['id'])
#            delete_restricted(task)

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
#to-do
#            change_to_restricted(self.tasks[out])
            self.tasks[out]['allocated']="restricted"
            self.restricted_allocations.append(out)
            self.reliable_allocations.remove(out)

        for into in to_add_into_reliable:

            if self.tasks[into]["allocated"]=="none":
                self
#to-do
#                create_reliable(tasks)
            else:

#to-do
#                change_to_reliable(self.tasks[into])
                self.restricted_allocations.remove(into)

            self.reliable_allocations.append(into)
            self.tasks[into]["allocated"]=="reliable"


        return

    def parse_result(self, result):
        return

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
