/******************************************************************************
* File:             emqc.c
*
* Author:
* Created:          06/06/23
* Description:
*****************************************************************************/

#include "string.h"
#include "unistd.h"
#include "MQTTClient.h"
#include "emqc.h"
#include <stdlib.h>
#include <time.h>
#include <syslog.h>

#define MAX_MESSAGE_HANDLERS 20

static MQTTClient s_mqttc = 0;

struct MessageHandlers
{
    const char* topic;
    void (*fp) (const char* topic, const char* payload);
} s_messageHandlers[MAX_MESSAGE_HANDLERS];

static int on_message(void *context, char *topic, int length, MQTTClient_message *message);

static int _emqc_connect(MQTTClient *client, const char* host, int port, const char* client_id, const char* username, const char* password)
{
    int rc = 0;
    char address[64] = {0};
    snprintf(address, 63, "tcp://%s:%d", host, port);
    MQTTClient_create(client, address, client_id, 0, NULL);
    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    conn_opts.username = username;
    conn_opts.password = password;
    MQTTClient_setCallbacks(*client, NULL, NULL, on_message, NULL);
    if ((rc = MQTTClient_connect(*client, &conn_opts)) != MQTTCLIENT_SUCCESS) {
        syslog(LOG_ERR, "Failed to connect [%s:%d], return code %d\n", host, port, rc);
        return -1;
    }
    syslog(LOG_DEBUG, "Connected to MQTT Broker!\n");
    return 0;
}

static int on_message(void *context, char *topic, int length, MQTTClient_message *message)
{
    char *payload = (char*)message->payload;
    syslog(LOG_DEBUG, "Received `%s` from `%s` topic \n", payload, topic);
    if (strncmp(topic, "/cloud/", 7) == 0) {
        // MQTTClient client;
        // int rc = _emqc_connect(&client, "127.0.0.1", 1883, "emqc", "emqx", "public");
        // if (rc < 0) {
        //     syslog(LOG_ERR, "emqc connect local emqx [%d] fail!\n", rc);
        // } else {
        //     MQTTClient_message message = MQTTClient_message_initializer;
        //     message.payload = (void*)payload;
        //     message.payloadlen = strlen(payload);
        //     MQTTClient_deliveryToken token;
        //     MQTTClient_publishMessage(client, topic, &message, &token);
        //     MQTTClient_waitForCompletion(client, token, 2000L);
        // }
    } else {
        for (int i = 0; i < MAX_MESSAGE_HANDLERS; ++i) {
            if (s_messageHandlers[i].topic != NULL && strcmp(s_messageHandlers[i].topic, topic) == 0) {
                if (s_messageHandlers[i].fp != NULL) {
                    s_messageHandlers[i].fp(topic, payload);
                }
            }
        }
    }
    MQTTClient_freeMessage(&message);
    MQTTClient_free(topic);
    return 1;
}

int emqc_pub(const char* topic, const char* payload)
{
    MQTTClient_message message = MQTTClient_message_initializer;
    message.payload = (void*)payload;
    message.payloadlen = strlen(payload);
    message.qos = 0;
    message.retained = 0;
    MQTTClient_deliveryToken token;
    MQTTClient_publishMessage(s_mqttc, topic, &message, &token);
    MQTTClient_waitForCompletion(s_mqttc, token, 4000L);
    syslog(LOG_DEBUG, "Send `%s` to topic `%s` \n", payload, topic);
    // printf("Send `%s` to topic `%s` \n", payload, topic);
    return 0;
}

int emqc_sub(const char* topic, void (*cb)(const char*, const char*))
{
    MQTTClient_subscribe(s_mqttc, topic, 0);
    for (int i = 0; i < MAX_MESSAGE_HANDLERS; ++i) {
        if (s_messageHandlers[i].topic == NULL) {
            s_messageHandlers[i].topic = topic;
            s_messageHandlers[i].fp = cb;
            break;
        }
    }
    return 0;
}

int emqc_init(const char* host, int port, const char* client_id, const char* username, const char* password)
{
    int rc = _emqc_connect(&s_mqttc, host, port, client_id, username, password);
    if (rc < 0)
        exit(-1);
    MQTTClient_subscribe(s_mqttc, "/cloud/#", 0);
    return 0;
}

void emqc_yield()
{
    MQTTClient_yield();
}
