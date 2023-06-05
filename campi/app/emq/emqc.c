#include "stdlib.h"
#include "string.h"
#include "unistd.h"
#include "MQTTClient.h"
#include "emqc.h"

static MQTTClient s_mqttc = 0;


static int on_message(void *context, char *topic, int length, MQTTClient_message *message)
{
    char *payload = (char*)message->payload;
    printf("Received `%s` from `%s` topic \n", payload, topic);
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
        printf("Failed to connect, return code %d\n", rc);
        exit(-1);
    } else {
        printf("Connected to MQTT Broker!\n");
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
    printf("Send `%s` to topic `%s` \n", payload, topic);
    return 0;
}

int emqc_sub(const char* topic, void *(cb)(const char*))
{
    return 0;
}

void emqc_loop()
{
    while (1) {
        MQTTClient_yield();
    }
}
