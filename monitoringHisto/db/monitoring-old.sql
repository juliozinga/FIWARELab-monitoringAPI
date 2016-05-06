-- MySQL dump 10.13  Distrib 5.7.10, for osx10.11 (x86_64)
--
-- Host: 127.0.0.1    Database: monitoring
-- ------------------------------------------------------
-- Server version	5.1.73

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `host`
--

DROP TABLE IF EXISTS `host`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service`
--

DROP TABLE IF EXISTS `host_service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Berlin`
--

DROP TABLE IF EXISTS `host_service_stage_Berlin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Berlin` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Berlin2`
--

DROP TABLE IF EXISTS `host_service_stage_Berlin2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Berlin2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Budapest`
--

DROP TABLE IF EXISTS `host_service_stage_Budapest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Budapest` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Budapest2`
--

DROP TABLE IF EXISTS `host_service_stage_Budapest2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Budapest2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Crete`
--

DROP TABLE IF EXISTS `host_service_stage_Crete`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Crete` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Gent`
--

DROP TABLE IF EXISTS `host_service_stage_Gent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Gent` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Karlskrona`
--

DROP TABLE IF EXISTS `host_service_stage_Karlskrona`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Karlskrona` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Lannion`
--

DROP TABLE IF EXISTS `host_service_stage_Lannion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Lannion` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Lannion2`
--

DROP TABLE IF EXISTS `host_service_stage_Lannion2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Lannion2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_PiraeusN`
--

DROP TABLE IF EXISTS `host_service_stage_PiraeusN`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_PiraeusN` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_PiraeusU`
--

DROP TABLE IF EXISTS `host_service_stage_PiraeusU`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_PiraeusU` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Poznan`
--

DROP TABLE IF EXISTS `host_service_stage_Poznan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Poznan` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Prague`
--

DROP TABLE IF EXISTS `host_service_stage_Prague`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Prague` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_RegionOne`
--

DROP TABLE IF EXISTS `host_service_stage_RegionOne`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_RegionOne` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_SophiaAntipolis`
--

DROP TABLE IF EXISTS `host_service_stage_SophiaAntipolis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_SophiaAntipolis` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Spain`
--

DROP TABLE IF EXISTS `host_service_stage_Spain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Spain` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Spain2`
--

DROP TABLE IF EXISTS `host_service_stage_Spain2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Spain2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Stockholm`
--

DROP TABLE IF EXISTS `host_service_stage_Stockholm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Stockholm` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Stockholm2`
--

DROP TABLE IF EXISTS `host_service_stage_Stockholm2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Stockholm2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Trento`
--

DROP TABLE IF EXISTS `host_service_stage_Trento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Trento` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Volos`
--

DROP TABLE IF EXISTS `host_service_stage_Volos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Volos` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Waterford`
--

DROP TABLE IF EXISTS `host_service_stage_Waterford`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Waterford` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_service_stage_Zurich`
--

DROP TABLE IF EXISTS `host_service_stage_Zurich`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_service_stage_Zurich` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(32) NOT NULL,
  `entityType` varchar(32) NOT NULL,
  `serviceType` varchar(32) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_Uptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`entityType`,`serviceType`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Berlin`
--

DROP TABLE IF EXISTS `host_stage_Berlin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Berlin` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Berlin2`
--

DROP TABLE IF EXISTS `host_stage_Berlin2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Berlin2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Budapest`
--

DROP TABLE IF EXISTS `host_stage_Budapest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Budapest` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Budapest2`
--

DROP TABLE IF EXISTS `host_stage_Budapest2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Budapest2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Crete`
--

DROP TABLE IF EXISTS `host_stage_Crete`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Crete` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Gent`
--

DROP TABLE IF EXISTS `host_stage_Gent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Gent` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Karlskrona`
--

DROP TABLE IF EXISTS `host_stage_Karlskrona`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Karlskrona` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Lannion`
--

DROP TABLE IF EXISTS `host_stage_Lannion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Lannion` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Lannion2`
--

DROP TABLE IF EXISTS `host_stage_Lannion2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Lannion2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_PiraeusN`
--

DROP TABLE IF EXISTS `host_stage_PiraeusN`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_PiraeusN` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_PiraeusU`
--

DROP TABLE IF EXISTS `host_stage_PiraeusU`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_PiraeusU` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Poznan`
--

DROP TABLE IF EXISTS `host_stage_Poznan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Poznan` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Prague`
--

DROP TABLE IF EXISTS `host_stage_Prague`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Prague` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_SophiaAntipolis`
--

DROP TABLE IF EXISTS `host_stage_SophiaAntipolis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_SophiaAntipolis` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Spain`
--

DROP TABLE IF EXISTS `host_stage_Spain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Spain` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Spain2`
--

DROP TABLE IF EXISTS `host_stage_Spain2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Spain2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Stockholm`
--

DROP TABLE IF EXISTS `host_stage_Stockholm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Stockholm` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Stockholm2`
--

DROP TABLE IF EXISTS `host_stage_Stockholm2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Stockholm2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Trento`
--

DROP TABLE IF EXISTS `host_stage_Trento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Trento` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Volos`
--

DROP TABLE IF EXISTS `host_stage_Volos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Volos` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Waterford`
--

DROP TABLE IF EXISTS `host_stage_Waterford`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Waterford` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `host_stage_Zurich`
--

DROP TABLE IF EXISTS `host_stage_Zurich`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `host_stage_Zurich` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `host_name` varchar(32) NOT NULL,
  `role` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_id` varchar(16) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region`
--

DROP TABLE IF EXISTS `region`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Berlin`
--

DROP TABLE IF EXISTS `region_stage_Berlin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Berlin` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Berlin2`
--

DROP TABLE IF EXISTS `region_stage_Berlin2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Berlin2` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Budapest`
--

DROP TABLE IF EXISTS `region_stage_Budapest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Budapest` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Budapest2`
--

DROP TABLE IF EXISTS `region_stage_Budapest2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Budapest2` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Crete`
--

DROP TABLE IF EXISTS `region_stage_Crete`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Crete` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Gent`
--

DROP TABLE IF EXISTS `region_stage_Gent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Gent` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Karlskrona`
--

DROP TABLE IF EXISTS `region_stage_Karlskrona`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Karlskrona` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Lannion`
--

DROP TABLE IF EXISTS `region_stage_Lannion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Lannion` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Lannion2`
--

DROP TABLE IF EXISTS `region_stage_Lannion2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Lannion2` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_PiraeusN`
--

DROP TABLE IF EXISTS `region_stage_PiraeusN`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_PiraeusN` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_PiraeusU`
--

DROP TABLE IF EXISTS `region_stage_PiraeusU`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_PiraeusU` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Poznan`
--

DROP TABLE IF EXISTS `region_stage_Poznan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Poznan` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Prague`
--

DROP TABLE IF EXISTS `region_stage_Prague`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Prague` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_SophiaAntipolis`
--

DROP TABLE IF EXISTS `region_stage_SophiaAntipolis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_SophiaAntipolis` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Spain`
--

DROP TABLE IF EXISTS `region_stage_Spain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Spain` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Spain2`
--

DROP TABLE IF EXISTS `region_stage_Spain2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Spain2` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Stockholm`
--

DROP TABLE IF EXISTS `region_stage_Stockholm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Stockholm` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Stockholm2`
--

DROP TABLE IF EXISTS `region_stage_Stockholm2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Stockholm2` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Trento`
--

DROP TABLE IF EXISTS `region_stage_Trento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Trento` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Volos`
--

DROP TABLE IF EXISTS `region_stage_Volos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Volos` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Waterford`
--

DROP TABLE IF EXISTS `region_stage_Waterford`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Waterford` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region_stage_Zurich`
--

DROP TABLE IF EXISTS `region_stage_Zurich`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `region_stage_Zurich` (
  `entityId` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_ram_used` float NOT NULL DEFAULT '0',
  `avg_ram_tot` float NOT NULL DEFAULT '0',
  `avg_core_enabled` float NOT NULL DEFAULT '0',
  `avg_core_used` float NOT NULL DEFAULT '0',
  `avg_core_tot` float NOT NULL DEFAULT '0',
  `avg_hd_used` float NOT NULL DEFAULT '0',
  `avg_hd_tot` float NOT NULL DEFAULT '0',
  `avg_vm_tot` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm`
--

DROP TABLE IF EXISTS `vm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Berlin`
--

DROP TABLE IF EXISTS `vm_stage_Berlin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Berlin` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Berlin2`
--

DROP TABLE IF EXISTS `vm_stage_Berlin2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Berlin2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Budapest`
--

DROP TABLE IF EXISTS `vm_stage_Budapest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Budapest` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Budapest2`
--

DROP TABLE IF EXISTS `vm_stage_Budapest2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Budapest2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Crete`
--

DROP TABLE IF EXISTS `vm_stage_Crete`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Crete` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Gent`
--

DROP TABLE IF EXISTS `vm_stage_Gent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Gent` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Karlskrona`
--

DROP TABLE IF EXISTS `vm_stage_Karlskrona`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Karlskrona` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Lannion`
--

DROP TABLE IF EXISTS `vm_stage_Lannion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Lannion` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Lannion2`
--

DROP TABLE IF EXISTS `vm_stage_Lannion2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Lannion2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_PiraeusN`
--

DROP TABLE IF EXISTS `vm_stage_PiraeusN`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_PiraeusN` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_PiraeusU`
--

DROP TABLE IF EXISTS `vm_stage_PiraeusU`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_PiraeusU` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Poznan`
--

DROP TABLE IF EXISTS `vm_stage_Poznan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Poznan` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Prague`
--

DROP TABLE IF EXISTS `vm_stage_Prague`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Prague` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_SophiaAntipolis`
--

DROP TABLE IF EXISTS `vm_stage_SophiaAntipolis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_SophiaAntipolis` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Spain`
--

DROP TABLE IF EXISTS `vm_stage_Spain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Spain` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Spain2`
--

DROP TABLE IF EXISTS `vm_stage_Spain2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Spain2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Stockholm`
--

DROP TABLE IF EXISTS `vm_stage_Stockholm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Stockholm` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Stockholm2`
--

DROP TABLE IF EXISTS `vm_stage_Stockholm2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Stockholm2` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Trento`
--

DROP TABLE IF EXISTS `vm_stage_Trento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Trento` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Volos`
--

DROP TABLE IF EXISTS `vm_stage_Volos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Volos` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Waterford`
--

DROP TABLE IF EXISTS `vm_stage_Waterford`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Waterford` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vm_stage_Zurich`
--

DROP TABLE IF EXISTS `vm_stage_Zurich`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_stage_Zurich` (
  `entityId` varchar(64) NOT NULL,
  `region` varchar(16) NOT NULL,
  `entityType` varchar(16) NOT NULL,
  `aggregationType` varchar(8) NOT NULL,
  `timestampId` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `avg_usedMemPct` float NOT NULL DEFAULT '0',
  `avg_freeSpacePct` float NOT NULL DEFAULT '0',
  `avg_cpuLoadPct` float NOT NULL DEFAULT '0',
  `host_name` varchar(32) NOT NULL,
  `sysUptime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityId`,`region`,`aggregationType`,`timestampId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-05-09 18:05:21
