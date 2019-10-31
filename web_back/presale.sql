/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50724
Source Host           : localhost:3306
Source Database       : presale

Target Server Type    : MYSQL
Target Server Version : 50724
File Encoding         : 65001

Date: 2019-01-03 15:59:21
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `presale`
-- ----------------------------
DROP TABLE IF EXISTS `presale`;
CREATE TABLE `presale` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `txid` text NOT NULL,
  `type` int(11) NOT NULL,
  `address` text NOT NULL,
  `tm` int(11) NOT NULL,
  `state` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of presale
-- ----------------------------
