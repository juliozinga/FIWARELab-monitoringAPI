SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `monitoring` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci ;
USE `monitoring` ;

-- -----------------------------------------------------
-- Table `monitoring`.`host`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `monitoring`.`host` ;

CREATE  TABLE IF NOT EXISTS `monitoring`.`host` (
  `entityId` VARCHAR(64) NOT NULL ,
  `region` VARCHAR(16) NOT NULL ,
  `host_name` VARCHAR(32) NOT NULL ,
  `role` VARCHAR(16) NOT NULL ,
  `aggregationType` VARCHAR(8) NOT NULL ,
  `timestampId` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP ,
  `avg_usedMemPct` FLOAT NOT NULL DEFAULT '0' ,
  `avg_freeSpacePct` FLOAT NOT NULL DEFAULT '0' ,
  `avg_cpuLoadPct` FLOAT NOT NULL DEFAULT '0' ,
  `host_id` VARCHAR(16) NOT NULL ,
  `sysUptime` FLOAT NOT NULL DEFAULT '0' ,
  PRIMARY KEY (`entityId`, `region`, `aggregationType`, `timestampId`) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `monitoring`.`host_service`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `monitoring`.`host_service` ;

CREATE  TABLE IF NOT EXISTS `monitoring`.`host_service` (
  `entityId` VARCHAR(64) NOT NULL ,
  `region` VARCHAR(32) NOT NULL ,
  `entityType` VARCHAR(32) NOT NULL ,
  `serviceType` VARCHAR(32) NOT NULL ,
  `aggregationType` VARCHAR(8) NOT NULL ,
  `timestampId` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
  `avg_Uptime` FLOAT NOT NULL DEFAULT '0' ,
  PRIMARY KEY (`entityId`, `region`, `entityType`, `serviceType`, `aggregationType`, `timestampId`) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `monitoring`.`region`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `monitoring`.`region` ;

CREATE  TABLE IF NOT EXISTS `monitoring`.`region` (
  `entityId` VARCHAR(16) NOT NULL ,
  `entityType` VARCHAR(16) NOT NULL ,
  `aggregationType` VARCHAR(8) NOT NULL ,
  `timestampId` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP ,
  `avg_ram_used` FLOAT NOT NULL DEFAULT '0' ,
  `avg_ram_tot` FLOAT NOT NULL DEFAULT '0' ,
  `avg_core_enabled` FLOAT NOT NULL DEFAULT '0' ,
  `avg_core_used` FLOAT NOT NULL DEFAULT '0' ,
  `avg_core_tot` FLOAT NOT NULL DEFAULT '0' ,
  `avg_hd_used` FLOAT NOT NULL DEFAULT '0' ,
  `avg_hd_tot` FLOAT NOT NULL DEFAULT '0' ,
  `avg_vm_tot` FLOAT NOT NULL DEFAULT '0' ,
  PRIMARY KEY (`entityId`, `aggregationType`, `timestampId`) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `monitoring`.`vm`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `monitoring`.`vm` ;

CREATE  TABLE IF NOT EXISTS `monitoring`.`vm` (
  `entityId` VARCHAR(64) NOT NULL ,
  `region` VARCHAR(16) NOT NULL ,
  `entityType` VARCHAR(16) NOT NULL ,
  `aggregationType` VARCHAR(8) NOT NULL ,
  `timestampId` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
  `avg_usedMemPct` FLOAT NOT NULL DEFAULT '0' ,
  `avg_freeSpacePct` FLOAT NOT NULL DEFAULT '0' ,
  `avg_cpuLoadPct` FLOAT NOT NULL DEFAULT '0' ,
  `host_name` VARCHAR(32) NOT NULL ,
  `sysUptime` FLOAT NOT NULL DEFAULT '0' ,
  PRIMARY KEY (`entityId`, `region`, `aggregationType`, `timestampId`) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
