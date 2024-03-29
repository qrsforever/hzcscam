#ifndef __EMQC__
#define __EMQC__

int emqc_init(const char* host, int port, const char* client_id, const char* username, const char* password);

int neza_pub(const char* topic, const char* payload);
int emqc_pub(const char* topic, const char* payload);
int emqc_sub(const char* topic, void (*cb)(const char*, const char*));

void emqc_yield();

#endif
