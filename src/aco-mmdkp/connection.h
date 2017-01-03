#include "czmq.h"
#include "colony.h"

int init_sockets(Colony *colony);

int destroy_sockets(Colony *colony);

int sync_sockets(Colony *colony);

int recv_tasks(Colony *colony);

int send_result(Colony *colony);

int test_sub();
