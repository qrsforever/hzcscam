#ifndef __EMQC__
#define __EMQC__

int emqc_connect(const char* host, int port, const char* client_id, const char* username, const char* password);
void emqc_yield();

#endif
