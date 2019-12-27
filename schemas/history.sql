-- MySQL dump 10.17  Distrib 10.3.17-MariaDB, for debian-linux-gnueabihf (armv7l)
--
-- Host: localhost    Database: binance_test
-- ------------------------------------------------------
-- Server version	10.3.17-MariaDB-0+deb10u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `history`
--

DROP TABLE IF EXISTS `history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `history` (
  `symbol` varchar(20) NOT NULL,
  `width` varchar(10) NOT NULL,
  `open_time` datetime NOT NULL,
  `open` decimal(32,16) NOT NULL,
  `high` decimal(32,16) NOT NULL,
  `low` decimal(32,16) NOT NULL,
  `close` decimal(32,16) NOT NULL,
  `number_trades` int(11) NOT NULL,
  `volume` decimal(16,8) NOT NULL,
  `close_time` datetime NOT NULL,
  `momentum_ao` decimal(32,16) DEFAULT NULL,
  `momentum_mfi` decimal(32,16) DEFAULT NULL,
  `momentum_rsi` decimal(32,16) DEFAULT NULL,
  `momentum_stoch` decimal(32,16) DEFAULT NULL,
  `momentum_stoch_signal` decimal(32,16) DEFAULT NULL,
  `momentum_tsi` decimal(32,16) DEFAULT NULL,
  `momentum_uo` decimal(32,16) DEFAULT NULL,
  `momentum_wr` decimal(32,16) DEFAULT NULL,
  `trend_adx_neg` decimal(32,16) DEFAULT NULL,
  `trend_adx_pos` decimal(32,16) DEFAULT NULL,
  `trend_aroon_down` decimal(32,16) DEFAULT NULL,
  `trend_aroon_ind` decimal(32,16) DEFAULT NULL,
  `trend_aroon_up` decimal(32,16) DEFAULT NULL,
  `trend_cci` decimal(32,16) DEFAULT NULL,
  `trend_dpo` decimal(32,16) DEFAULT NULL,
  `trend_ema_fast` decimal(32,16) DEFAULT NULL,
  `trend_ema_slow` decimal(32,16) DEFAULT NULL,
  `trend_ichimoku_a` decimal(32,16) DEFAULT NULL,
  `trend_ichimoku_b` decimal(32,16) DEFAULT NULL,
  `trend_kst` decimal(32,16) DEFAULT NULL,
  `trend_kst_diff` decimal(32,16) DEFAULT NULL,
  `trend_kst_sig` decimal(32,16) DEFAULT NULL,
  `trend_macd` decimal(32,16) DEFAULT NULL,
  `trend_macd_diff` decimal(32,16) DEFAULT NULL,
  `trend_macd_signal` decimal(32,16) DEFAULT NULL,
  `trend_mass_index` decimal(32,16) DEFAULT NULL,
  `trend_trix` decimal(32,16) DEFAULT NULL,
  `trend_visual_ichimoku_a` decimal(32,16) DEFAULT NULL,
  `trend_visual_ichimoku_b` decimal(32,16) DEFAULT NULL,
  `trend_vortex_diff` decimal(32,16) DEFAULT NULL,
  `trend_vortex_ind_neg` decimal(32,16) DEFAULT NULL,
  `trend_vortex_ind_pos` decimal(32,16) DEFAULT NULL,
  `volatility_bbh` decimal(32,16) DEFAULT NULL,
  `volatility_bbhi` decimal(32,16) DEFAULT NULL,
  `volatility_bbl` decimal(32,16) DEFAULT NULL,
  `volatility_bbli` decimal(32,16) DEFAULT NULL,
  `volatility_bbm` decimal(32,16) DEFAULT NULL,
  `volatility_dch` decimal(32,16) DEFAULT NULL,
  `volatility_dchi` decimal(32,16) DEFAULT NULL,
  `volatility_dcl` decimal(32,16) DEFAULT NULL,
  `volatility_dcli` decimal(32,16) DEFAULT NULL,
  `volatility_kcc` decimal(32,16) DEFAULT NULL,
  `volatility_kch` decimal(32,16) DEFAULT NULL,
  `volatility_kchi` decimal(32,16) DEFAULT NULL,
  `volatility_kcl` decimal(32,16) DEFAULT NULL,
  `volatility_kcli` decimal(32,16) DEFAULT NULL,
  PRIMARY KEY (`symbol`,`width`,`open_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `history`
--

LOCK TABLES `history` WRITE;
/*!40000 ALTER TABLE `history` DISABLE KEYS */;
/*!40000 ALTER TABLE `history` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-12-26 21:50:26
