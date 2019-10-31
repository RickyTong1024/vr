/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50724
Source Host           : localhost:3306
Source Database       : vrlibao

Target Server Type    : MYSQL
Target Server Version : 50724
File Encoding         : 65001

Date: 2019-03-05 20:55:37
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `libao`
-- ----------------------------
DROP TABLE IF EXISTS `libao`;
CREATE TABLE `libao` (
  `code` varchar(20) NOT NULL,
  `type` varchar(4) NOT NULL,
  `used` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`code`),
  KEY `code_index` (`code`(4)) USING BTREE,
  KEY `type_index` (`type`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of libao
-- ----------------------------

-- ----------------------------
-- Table structure for `libao_type`
-- ----------------------------
DROP TABLE IF EXISTS `libao_type`;
CREATE TABLE `libao_type` (
  `code` varchar(4) NOT NULL,
  `name` varchar(50) DEFAULT NULL,
  `num` int(11) DEFAULT NULL,
  `gongxiang` int(11) NOT NULL,
  `type` blob,
  `value1` blob,
  `value2` blob,
  `value3` blob,
  `dt` datetime DEFAULT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of libao_type
-- ----------------------------
