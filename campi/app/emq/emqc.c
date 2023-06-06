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


static int on_message(void *context, char *topic, int length, MQTTClient_message *message)
{
    char *payload = (char*)message->payload;
    syslog(LOG_DEBUG, "Received `%s` from `%s` topic \n", payload, topic);
    // printf("Received `%s` from `%s` topic \n", payload, topic);
    for (int i = 0; i < MAX_MESSAGE_HANDLERS; ++i) {
        if (s_messageHandlers[i].topic != NULL && strcmp(s_messageHandlers[i].topic, topic) == 0) {
            if (s_messageHandlers[i].fp != NULL) {
                s_messageHandlers[i].fp(topic, payload);
            }
        }
    }
    MQTTClient_freeMessage(&message);
    MQTTClient_free(topic);
    return 0;
}

int emqc_connect(const char* host, int port, const char* client_id, const char* username, const char* password)
{
    int rc = 0;
    char address[64] = {0};
    snprintf(address, 64, "tcp://%s:%d", host, port);
    MQTTClient_create(&s_mqttc, address, client_id, 0, NULL);
    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    conn_opts.username = username;
    conn_opts.password = password;
    MQTTClient_setCallbacks(s_mqttc, NULL, NULL, on_message, NULL);
    if ((rc = MQTTClient_connect(s_mqttc, &conn_opts)) != MQTTCLIENT_SUCCESS) {
        syslog(LOG_ERR, "Failed to connect, return code %d\n", rc);
        // printf("Failed to connect, return code %d\n", rc);
        exit(-1);
    } else {
        syslog(LOG_DEBUG, "Connected to MQTT Broker!\n");
        // printf("Connected to MQTT Broker!\n");
    }
    return 0;
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

void emqc_yield()
{
    MQTTClient_yield();
}
