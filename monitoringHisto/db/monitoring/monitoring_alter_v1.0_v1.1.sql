SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

DROP SCHEMA IF EXISTS `default_schema` ;

USE `monitoring`;

-- -----------------------------------------------------
-- Table `monitoring`.`host` alter
-- -----------------------------------------------------
ALTER TABLE `monitoring`.`host` MODIFY `timestampId` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- -----------------------------------------------------
-- Table `monitoring`.`region` alter
-- -----------------------------------------------------
ALTER TABLE `monitoring`.`region` MODIFY `timestampId` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
