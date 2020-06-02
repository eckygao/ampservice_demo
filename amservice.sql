-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- 主机： 100.121.190.3:3658
-- 生成日期： 2020-06-01 15:09:12
-- 服务器版本： 5.6.28-cdb2016-log
-- PHP 版本： 5.6.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;

CREATE DATABASE IF NOT EXISTS `demodb` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `demodb`;
COMMIT;

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `amservice`
--

-- --------------------------------------------------------

--
-- 表的结构 `aggregate_data`
--

CREATE TABLE `aggregate_data` (
  `clientid` int(11) NOT NULL,
  `utype` int(11) NOT NULL COMMENT '0-NULL;1-10min;2-30min;3-1hour;4-1day',
  `starttime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updatecount` int(11) NOT NULL COMMENT '上报次数',
  `pm1` int(11) NOT NULL,
  `pm2d5` int(11) NOT NULL,
  `pm10` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `base_data`
--

CREATE TABLE `base_data` (
  `uid` int(11) NOT NULL,
  `clientid` int(11) NOT NULL DEFAULT '0',
  `spaceid` int(11) NOT NULL DEFAULT '0',
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `PM1_CF1` int(11) NOT NULL,
  `PM2d5_CF1` int(11) NOT NULL,
  `PM10_CF1` int(11) NOT NULL,
  `PM1` int(11) NOT NULL,
  `PM2d5` int(11) NOT NULL,
  `PM10` int(11) NOT NULL,
  `particles_0d3` int(11) NOT NULL,
  `particles_0d5` int(11) NOT NULL,
  `particles_1` int(11) NOT NULL,
  `particles_2d5` int(11) NOT NULL,
  `particles_5` int(11) NOT NULL,
  `particles_10` int(11) NOT NULL,
  `version` int(11) NOT NULL,
  `Error` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `client`
--

CREATE TABLE `client` (
  `uid` int(11) NOT NULL,
  `devicename` varchar(64) NOT NULL,
  `spaceid` int(11) NOT NULL,
  `latitude` decimal(10,7) NOT NULL COMMENT '纬度',
  `longitude` decimal(10,7) NOT NULL COMMENT '经度',
  `activetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `astatus` int(11) DEFAULT '0' COMMENT '运行状态',
  `mstatus` int(11) DEFAULT '0' COMMENT '管理状态',
  `PM1` int(11) NOT NULL DEFAULT '0',
  `PM2d5` int(11) NOT NULL DEFAULT '0',
  `PM10` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `config`
--

CREATE TABLE `config` (
  `skey` varchar(128) NOT NULL,
  `uvalue` int(11) DEFAULT NULL,
  `svalue` varchar(128) DEFAULT NULL,
  `dtime` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `config`
--

INSERT INTO `config` (`skey`, `uvalue`, `svalue`, `dtime`) VALUES
('uptime_day', NULL, NULL, '2020-06-01 00:00:00'),
('uptime_hour', NULL, NULL, '2020-06-01 00:00:00');

-- --------------------------------------------------------

--
-- 表的结构 `space`
--

CREATE TABLE `space` (
  `uid` int(11) NOT NULL,
  `typeid` int(11) NOT NULL COMMENT '1小区2街道',
  `latitude` decimal(10,7) NOT NULL COMMENT '纬度',
  `longitude` decimal(10,7) NOT NULL COMMENT '经度',
  `country` varchar(64) NOT NULL,
  `province` varchar(64) NOT NULL,
  `city` varchar(64) NOT NULL,
  `spacename` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `temp_base_data`
--

CREATE TABLE `temp_base_data` (
  `uid` int(11) NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `devicename` varchar(16) NOT NULL,
  `PM1_CF1` int(11) NOT NULL,
  `PM2d5_CF1` int(11) NOT NULL,
  `PM10_CF1` int(11) NOT NULL,
  `PM1` int(11) NOT NULL,
  `PM2d5` int(11) NOT NULL,
  `PM10` int(11) NOT NULL,
  `particles_0d3` int(11) NOT NULL,
  `particles_0d5` int(11) NOT NULL,
  `particles_1` int(11) NOT NULL,
  `particles_2d5` int(11) NOT NULL,
  `particles_5` int(11) NOT NULL,
  `particles_10` int(11) NOT NULL,
  `version` int(11) NOT NULL,
  `Error` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 转储表的索引
--

--
-- 表的索引 `aggregate_data`
--
ALTER TABLE `aggregate_data`
  ADD PRIMARY KEY (`clientid`,`utype`,`starttime`);

--
-- 表的索引 `base_data`
--
ALTER TABLE `base_data`
  ADD PRIMARY KEY (`uid`),
  ADD KEY `time_2` (`time`,`clientid`);

--
-- 表的索引 `client`
--
ALTER TABLE `client`
  ADD PRIMARY KEY (`uid`),
  ADD UNIQUE KEY `devicename` (`devicename`);

--
-- 表的索引 `config`
--
ALTER TABLE `config`
  ADD UNIQUE KEY `skey` (`skey`);

--
-- 表的索引 `space`
--
ALTER TABLE `space`
  ADD PRIMARY KEY (`uid`);

--
-- 表的索引 `temp_base_data`
--
ALTER TABLE `temp_base_data`
  ADD PRIMARY KEY (`uid`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `base_data`
--
ALTER TABLE `base_data`
  MODIFY `uid` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `client`
--
ALTER TABLE `client`
  MODIFY `uid` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `space`
--
ALTER TABLE `space`
  MODIFY `uid` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `temp_base_data`
--
ALTER TABLE `temp_base_data`
  MODIFY `uid` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
