CREATE DATABASE IF NOT EXISTS aiot;
USE aiot;

CREATE TABLE IF NOT EXISTS `message_publish` (
    `id` varchar(36) NOT NULL,
    `username` varchar(100) NOT NULL,
    `clientid` varchar(100) NOT NULL,
    `qos` int(8) NOT NULL,
    `topic` varchar(100) NOT NULL,
    `payload` varchar(512) NOT NULL,
    `peerhost` varchar(32) NOT NULL,
    `publish_received_at` int(64) NOT NULL,
    `timestamp` int(64) NOT NULL,
    `node` varchar(64) NOT NULL,
    `flags` varchar(64) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
