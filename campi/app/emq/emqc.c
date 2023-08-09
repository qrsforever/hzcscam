/******************************************************************************
* File:             emqc.c
*
* Author:
* Created:          06/06/23
* Description:
*****************************************************************************/

#include <string.h>
#include <sys/syslog.h>
#include <unistd.h>
#include <stdlib.h>
#include <time.h>
#include <syslog.h>
#include "MQTTClient.h"
#include "emqc.h"

#define TOPIC_MAX_LENGTH 64
#define MAX_MESSAGE_HANDLERS 20

static MQTTClient r_client = 0;
static MQTTClient l_client = 0;
static int CLOUD_TOPIC_PREFIX_LEN = -1;
static int LOCAL_TOPIC_PREFIX_LEN = -1;

struct MessageHandlers
{
    char topic[TOPIC_MAX_LENGTH];
    void (*fp) (const char* topic, const char* payload);
} s_messageHandlers[MAX_MESSAGE_HANDLERS];

static int on_message(void *context, char *topic, int length, MQTTClient_message *message);

static int _emqc_connect(MQTTClient client, const char* username, const char* password)
{
    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    conn_opts.username = username;
    conn_opts.password = password;
    return MQTTClient_connect(client, &conn_opts);
}

static void on_connection_lost(void *context, char *cause)
{
    syslog(LOG_ERR, "connect lost: %s", cause);
    exit(-1);
}

static int on_message(void *context, char *topic, int length, MQTTClient_message *message)
{
    int rc = -1;
    char *payload = (char*)message->payload;
    if (strncmp(topic, "cloud/", 6) == 0) {
        syslog(LOG_DEBUG, "From Cloud to Campi Received `%s` from `%s` topic \n", payload, topic);
        if (strncmp(topic + CLOUD_TOPIC_PREFIX_LEN, "sensor", 6) == 0) {
            for (int i = 0; i < MAX_MESSAGE_HANDLERS; ++i) {
                if (s_messageHandlers[i].topic[0] != 0 && strcmp(s_messageHandlers[i].topic, topic) == 0) {
                    if (s_messageHandlers[i].fp != NULL) {
                        s_messageHandlers[i].fp(topic, payload);
                    }
                }
            }
        } else {
            MQTTClient_deliveryToken token;
            MQTTClient_publishMessage(l_client, topic, message, &token);
            MQTTClient_waitForCompletion(l_client, token, 2000L);
        }
    } else { // campi/
        syslog(LOG_DEBUG, "From Campi to Cloud: Received `%s` from `%s` topic \n", payload, topic);
        if (strncmp(topic + LOCAL_TOPIC_PREFIX_LEN, "sensor", 6) == 0) {
            for (int i = 0; i < MAX_MESSAGE_HANDLERS; ++i) {
                if (s_messageHandlers[i].topic[0] != 0 && strcmp(s_messageHandlers[i].topic, topic) == 0) {
                    if (s_messageHandlers[i].fp != NULL) {
                        s_messageHandlers[i].fp(topic, payload);
                    }
                }
            }
        } else {
            MQTTClient_deliveryToken token;
            rc = MQTTClient_publishMessage(r_client, topic, message, &token);
            if (rc < 0) {
                syslog(LOG_ERR, "Failed to publish, return code %d\n", rc);
                exit(-1);
            }
            MQTTClient_waitForCompletion(r_client, token, 2000L);
        }
    }
    MQTTClient_freeMessage(&message);
    MQTTClient_free(topic);
    return 1;
}

static int _emqc_pub(MQTTClient mqtt, const char* topic, const char* payload)
{
    MQTTClient_message message = MQTTClient_message_initializer;
    message.payload = (void*)payload;
    message.payloadlen = strlen(payload);
    message.qos = 0;
    message.retained = 0;
    MQTTClient_deliveryToken token;
    MQTTClient_publishMessage(mqtt, topic, &message, &token);
    MQTTClient_waitForCompletion(mqtt, token, 4000L);
    syslog(LOG_DEBUG, "Send `%s` to topic `%s` \n", payload, topic);
    return 0;
}

int neza_pub(const char* topic, const char* payload)
{
    return _emqc_pub(l_client, topic, payload);
}

int emqc_pub(const char* topic, const char* payload)
{
    return _emqc_pub(r_client, topic, payload);
}

int emqc_sub(const char* topic, void (*cb)(const char*, const char*))
{
    // MQTTClient_subscribe(r_client, topic, 0);
    for (int i = 0; i < MAX_MESSAGE_HANDLERS; ++i) {
        if (s_messageHandlers[i].topic[0] == 0) {
            strncpy(s_messageHandlers[i].topic, topic, TOPIC_MAX_LENGTH);
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
    memset(s_messageHandlers, 0, sizeof(s_messageHandlers));

    // cloud emq
    snprintf(buff, 63, "tcp://%s:%d", host, port);
    MQTTClient_create(&r_client, buff, client_id, 0, NULL);

    MQTTClient_setCallbacks(r_client, NULL, on_connection_lost, on_message, NULL);
    rc = _emqc_connect(r_client, username, password);
    if (rc != MQTTCLIENT_SUCCESS) {
        syslog(LOG_ERR, "Failed to connect [%s:%d], return code %d\n", host, port, rc);
        exit(-1);
    }
    syslog(LOG_DEBUG, "Connected to Cloud MQTT Broker!\n");
    snprintf(buff, 63, "cloud/%s/#", client_id);
    MQTTClient_subscribe(r_client, buff, 0);
    MQTTClient_subscribe(r_client, "cloud/all/#", 0);
    CLOUD_TOPIC_PREFIX_LEN = strlen(buff) - 1;
    syslog(LOG_DEBUG, "cloud sub: %s: %d\n", buff, CLOUD_TOPIC_PREFIX_LEN);

    // local emq
    MQTTClient_create(&l_client, "tcp://127.0.0.1:1883", "campi_emq", 0, NULL);
    MQTTClient_setCallbacks(l_client, NULL, NULL, on_message, NULL);
    rc = _emqc_connect(l_client, "eqmx", "public");
    if (rc != MQTTCLIENT_SUCCESS) {
        syslog(LOG_ERR, "Failed to connect local emqx, return code %d\n", rc);
        exit(-1);
    }
    syslog(LOG_DEBUG, "Connected to Local MQTT Broker!\n");
    snprintf(buff, 63, "campi/%s/#", client_id);
    MQTTClient_subscribe(l_client, buff, 0);
    LOCAL_TOPIC_PREFIX_LEN = strlen(buff) - 1;
    syslog(LOG_DEBUG, "campi sub: %s: %d\n", buff, LOCAL_TOPIC_PREFIX_LEN);

    return 0;
}

void emqc_yield()
{
    MQTTClient_yield();
}
