CREATE DATABASE IF NOT EXISTS mqtt;
USE mqtt;

CREATE TABLE IF NOT EXISTS `mqtt_user` (
  `id` INT(11) unsigned NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(100) DEFAULT NULL,
  `password_hash` VARCHAR(100) DEFAULT NULL,
  `salt` VARCHAR(35) DEFAULT NULL,
  `is_superuser` tinyint(1) DEFAULT 0,
  `created` DATETIME DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `mqtt_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE IF NOT EXISTS `mqtt_acl` (
  `id` INT(11) unsigned NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(100) NOT NULL,
  `permission` VARCHAR(5) NOT NULL,
  `action` VARCHAR(9) NOT NULL,
  `topic` VARCHAR(100) NOT NULL,
  INDEX username_idx(username),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
