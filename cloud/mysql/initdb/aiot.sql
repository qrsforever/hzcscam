CREATE DATABASE IF NOT EXISTS aiot;
USE aiot;

-- DROP TABLE message_publish;

CREATE TABLE IF NOT EXISTS `message_publish` (
    `id` VARCHAR(36) NOT NULL,
    `clientid` VARCHAR(100) NOT NULL,
    `username` VARCHAR(100) NOT NULL,
    `topic` VARCHAR(100) NOT NULL,
    `peerhost` VARCHAR(32) NOT NULL,
    `node` VARCHAR(64) NOT NULL,
    `payload` JSON NOT NULL,
    `flags` JSON NOT NULL,
    `qos` TINYINT NOT NULL,
    `publish_received_at` DATETIME NOT NULL,
    `create_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE IF NOT EXISTS `client_connected` (
    `id` BIGINT unsigned NOT NULL AUTO_INCREMENT,
    `clientid` VARCHAR(100) NOT NULL,
    `username` VARCHAR(100) NOT NULL,
    `sockname` VARCHAR(32) NOT NULL,
    `peername` VARCHAR(32) NOT NULL,
    `node` VARCHAR(64) NOT NULL,
    `receive_maximum` TINYINT NOT NULL,
    `keepalive` TINYINT NOT NULL,
    `expiry_interval` TINYINT NOT NULL,
    `is_bridge` TINYINT(1) NOT NULL,
    `clean_start` TINYINT(1) NOT NULL,
    `proto_name` VARCHAR(16) NOT NULL,
    `proto_var` TINYINT(2) NOT NULL,
    `connected_at` DATETIME NOT NULL,
    `create_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE IF NOT EXISTS `client_disconnected` (
    `id` BIGINT unsigned NOT NULL AUTO_INCREMENT,
    `clientid` VARCHAR(100) NOT NULL,
    `username` VARCHAR(100) NOT NULL,
    `reason` VARCHAR NOT NULL,
    `disconnected_at` DATETIME NOT NULL,
    `create_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
