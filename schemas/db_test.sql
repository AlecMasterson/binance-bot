DROP TABLE IF EXISTS `symbol`;
CREATE TABLE `symbol` (
  `name` VARCHAR(20) NOT NULL,
  `active` TINYINT(1) NOT NULL DEFAULT 0,
  UNIQUE KEY `symbol` (`name`)
);

DROP TABLE IF EXISTS `history`;
CREATE TABLE `history` (
  `symbol` VARCHAR(20) NOT NULL,
  `width` VARCHAR(10) NOT NULL,
  `openTime` DATETIME NOT NULL,
  `openPrice` DECIMAL(32,16) NOT NULL,
  `high` DECIMAL(32,16) NOT NULL,
  `low` DECIMAL(32,16) NOT NULL,
  `closePrice` DECIMAL(32,16) NOT NULL,
  `numberTrades` INT(10) NOT NULL,
  `volume` DECIMAL(16,8) NOT NULL,
  `closeTime` DATETIME NOT NULL,
  UNIQUE KEY `history` (`symbol`,`width`,`openTime`)
);

DROP TABLE IF EXISTS `decision`;
CREATE TABLE `decision` (
  `model` VARCHAR(20) NOT NULL,
  `symbol` VARCHAR(20) NOT NULL,
  `closeTime` DATETIME NOT NULL,
  `choice` VARCHAR(10) NOT NULL,
  UNIQUE KEY `decision` (`model`,`symbol`,`closeTime`)
);

DROP TABLE IF EXISTS `balance`;
CREATE TABLE `balance` (
  `user` VARCHAR(20) NOT NULL,
  `asset` VARCHAR(10) NOT NULL,
  `free` DECIMAL(16,8) NOT NULL,
  `total` DECIMAL(16,8) NOT NULL,
  UNIQUE KEY `balance` (`user`,`asset`)
);

DROP TABLE IF EXISTS `position`;
CREATE TABLE `position` (
  `user` VARCHAR(20) NOT NULL,
  `symbol` VARCHAR(20) NOT NULL,
  `active` TINYINT(1) NOT NULL,
  `buyTime` DATETIME NOT NULL,
  `buyPrice` DECIMAL(32,16) NOT NULL,
  `sellTime` DATETIME DEFAULT NULL,
  `sellPrice` DECIMAL(32,16) DEFAULT NULL,
  `amount` DECIMAL(16,8) NOT NULL,
  `roi` DECIMAL(8,4) NOT NULL,
  UNIQUE KEY `position` (`user`, `symbol`, `buyTime`)
);
