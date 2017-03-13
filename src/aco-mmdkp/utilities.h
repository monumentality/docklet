#include <glib.h>

extern int s_interrupted;

void s_signal_handler();

void s_catch_signals(void);

void free_key(gpointer data);
void free_value(gpointer value);

int test_glist();
int test_gtable();
