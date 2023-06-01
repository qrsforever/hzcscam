1. https://www.emqx.io/docs/zh/v5.0/security/authn/mysql.html

添加用户名为 user123、密码为 secret、盐值为 salt 和超级用户标志为 true 的用户示例：
```
INSERT INTO mqtt_user(username, password_hash, salt, is_superuser) VALUES ('user123', 'bede90386d450cea8b77b822f8887065e4e5abf132c2f9dccfcc7fbd4cba5e35', 'salt', 1);
```

2. https://www.emqx.io/docs/zh/v5.0/security/authz/mysql.html#%E9%85%8D%E7%BD%AE

为用户 user123 添加允许发布到主题 data/user123/# 的权限规则的示例：
```
INSERT INTO mqtt_acl(username, permission, action, topic) VALUES ('user123', 'allow', 'publish', 'data/user123/#');
```

3. demo

```
{
    "username":"campi",
    "topic":"campi/c-test",
    "timestamp":1685543875692,
    "qos":0,
    "publish_received_at":1685543875692,
    "pub_props":{
        "User-Property":{

        }
    },
    "peerhost":"192.168.16.1",
    "payload":"message-204",
    "node":"emqx@127.0.0.1",
    "metadata":{
        "rule_id":"hook_campi"
    },
    "id":"0005FCFE43F6C838F44200004BFD00CE",
    "flags":{
        "retain":false,
        "dup":false
    },
    "event":"message.publish",
    "clientid":"localhost"
}
```

```
{
    "username": "campi",
    "timestamp": 1685620198222,
    "sockname": "192.168.48.3:1883",
    "receive_maximum": 32,
    "proto_ver": 4,
    "proto_name": "MQTT",
    "peername": "192.168.48.1:48254",
    "node": "emqx@127.0.0.1",
    "mountpoint": "undefined",
    "metadata": {
        "rule_id": "hook_campi"
    },
    "keepalive": 60,
    "is_bridge": false,
    "expiry_interval": 0,
    "event": "client.connected",
    "connected_at": 1685620198222,
    "conn_props": {
        "User-Property": {}
    },
    "clientid": "localhost",
    "clean_start": true
}
```

```
{
    "username": "campi",
    "timestamp": 1685620199596,
    "sockname": "192.168.48.3:1883",
    "reason": "tcp_closed",
    "proto_ver": 4,
    "proto_name": "MQTT",
    "peername": "192.168.48.1:48254",
    "node": "emqx@127.0.0.1",
    "metadata": {
        "rule_id": "hook_campi"
    },
    "event": "client.disconnected",
    "disconnected_at": 1685620199596,
    "disconn_props": {
        "User-Property": {}
    },
    "clientid": "localhost"
}
```
