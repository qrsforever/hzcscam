/******************************************************************************
* File:             emqc.c
*
* Author:
* Created:          06/06/23
* Description:
*****************************************************************************/

#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <time.h>
#include <syslog.h>
#include "MQTTClient.h"
#include "emqc.h"

#define MAX_MESSAGE_HANDLERS 20

static MQTTClient r_client = 0;
static MQTTClient l_client = 0;
static int CLOUD_TOPIC_PREFIX_LEN = -1;
static int LOCAL_TOPIC_PREFIX_LEN = -1;

struct MessageHandlers
{
    const char* topic;
    void (*fp) (const char* topic, const char* payload);
} s_messageHandlers[MAX_MESSAGE_HANDLERS];

static int on_message(void *context, char *topic, int length, MQTTClient_message *message);

static int _emqc_connect(MQTTClient client, const char* username, const char* password)
{
    int rc = -1;
    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    conn_opts.username = username;
    conn_opts.password = password;
    return MQTTClient_connect(client, &conn_opts);
}

static int on_message(void *context, char *topic, int length, MQTTClient_message *message)
{
    char *payload = (char*)message->payload;
    syslog(LOG_DEBUG, "Received `%s` from `%s` topic \n", payload, topic);
    if (strncmp(topic, "cloud/", 6) == 0) {
        if (strncmp(topic + CLOUD_TOPIC_PREFIX_LEN, "ota", 3) == 0) {
            MQTTClient_deliveryToken token;
            MQTTClient_publishMessage(l_client, topic, message, &token);
            MQTTClient_waitForCompletion(l_client, token, 2000L);
        } else {
            for (int i = 0; i < MAX_MESSAGE_HANDLERS; ++i) {
                if (s_messageHandlers[i].topic != NULL && strcmp(s_messageHandlers[i].topic, topic) == 0) {
                    if (s_messageHandlers[i].fp != NULL) {
                        s_messageHandlers[i].fp(topic, payload);
                    }
                }
            }
        }
    } else { // campi/
        MQTTClient_deliveryToken token;
        MQTTClient_publishMessage(r_client, topic, message, &token);
        MQTTClient_waitForCompletion(r_client, token, 2000L);
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
    MQTTClient_publishMessage(r_client, topic, &message, &token);
    MQTTClient_waitForCompletion(r_client, token, 4000L);
    syslog(LOG_DEBUG, "Send `%s` to topic `%s` \n", payload, topic);
    // printf("Send `%s` to topic `%s` \n", payload, topic);
    return 0;
}

int emqc_sub(const char* topic, void (*cb)(const char*, const char*))
{
    MQTTClient_subscribe(r_client, topic, 0);
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
    int rc = 0;
    char buff[64] = {0};

    MQTTClient_create(&l_client, "tcp://127.0.0.1:1883", "campi_emq", 0, NULL);
    MQTTClient_setCallbacks(l_client, NULL, NULL, on_message, NULL);
    rc = _emqc_connect(l_client, "eqmx", "public");
    if (rc != MQTTCLIENT_SUCCESS) {
        syslog(LOG_ERR, "Failed to connect local emqx, return code %d\n", rc);
        exit(-1);
    }
    syslog(LOG_DEBUG, "Connected to Local MQTT Broker!\n");
    snprintf(buff, 63, "campi/%s/#", client_id);
    LOCAL_TOPIC_PREFIX_LEN = strlen(buff) - 1;
    MQTTClient_subscribe(l_client, buff, 0);

    snprintf(buff, 63, "tcp://%s:%d", host, port);
    MQTTClient_create(&r_client, buff, client_id, 0, NULL);
    MQTTClient_setCallbacks(r_client, NULL, NULL, on_message, NULL);
    rc = _emqc_connect(r_client, username, password);
    if (rc != MQTTCLIENT_SUCCESS) {
        syslog(LOG_ERR, "Failed to connect [%s:%d], return code %d\n", host, port, rc);
        exit(-1);
    }
    syslog(LOG_DEBUG, "Connected to Cloud MQTT Broker!\n");
    snprintf(buff, 63, "cloud/%s/#", client_id);
    MQTTClient_subscribe(r_client, buff, 0);
    CLOUD_TOPIC_PREFIX_LEN = strlen(buff) - 1;
    return 0;
}

void emqc_yield()
{
    MQTTClient_yield();
}
