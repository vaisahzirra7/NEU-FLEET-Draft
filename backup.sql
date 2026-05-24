-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: vanara_fleets
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_name` varchar(150) NOT NULL,
  `action` varchar(20) NOT NULL,
  `module` varchar(50) NOT NULL,
  `record_id` varchar(50) NOT NULL,
  `detail` longtext NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `audit_logs_user_id_752b0e2b_fk_users_id` (`user_id`),
  CONSTRAINT `audit_logs_user_id_752b0e2b_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=214 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
INSERT INTO `audit_logs` VALUES (1,'Vaisah Peter Zirra','create','vehicles','1','Created vehicle GMB-217-AA','2026-04-21 00:06:38.543536',1),(2,'Vaisah Peter Zirra','edit','vehicles','1','Updated vehicle GMB-217-AA','2026-04-21 00:08:17.503279',1),(3,'Vaisah Peter Zirra','create','vehicles','2','Created vehicle GMB-310-AA','2026-04-21 00:12:59.291857',1),(4,'Vaisah Peter Zirra','create','drivers','1','Registered driver Abba','2026-04-21 00:15:20.698421',1),(5,'Vaisah Peter Zirra','edit','drivers','1','Updated driver Abba Demo','2026-04-21 00:15:42.286042',1),(6,'Vaisah Peter Zirra','edit','vehicles','2','Updated vehicle GMB-310-AA','2026-04-21 00:16:05.702302',1),(7,'Vaisah Peter Zirra','create','vendors','1','Added vendor NNPC Mega Station','2026-04-21 00:16:42.753151',1),(8,'Vaisah Peter Zirra','create','vendors','2','Added vendor NNPC Mega Station, Gombe','2026-04-21 00:17:31.247812',1),(9,'Vaisah Peter Zirra','create','drivers','2','Registered driver Musa Demo','2026-04-21 00:18:15.254274',1),(10,'Vaisah Peter Zirra','edit','drivers','1','Updated driver Abba Demo','2026-04-21 00:20:48.274120',1),(11,'Vaisah Peter Zirra','create','vendors','3','Added vendor NNPC Mega Station Gombe','2026-04-21 00:21:59.933879',1),(12,'Vaisah Peter Zirra','edit','vendors','1','Updated vendor NNPC Mega Station','2026-04-21 12:54:01.901387',1),(13,'Vaisah Peter Zirra','create','maintenance','1','Logged Routine Service for GMB-217-AA','2026-04-22 21:15:28.871086',1),(14,'Vaisah Peter Zirra','edit','vehicles','1','Updated vehicle GMB-217-AA','2026-04-22 21:15:48.746031',1),(15,'Vaisah Peter Zirra','coupon_issue','coupons','1','Issued coupon FMS-2026-00001 for GMB-217-AA','2026-04-23 02:15:35.555561',1),(16,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','1','Redeemed coupon FMS-2026-00001 for GMB-217-AA','2026-04-23 02:19:18.865196',1),(17,'Vaisah Peter Zirra','coupon_issue','coupons','2','Issued coupon FMS-2026-00002 for GMB-310-AA','2026-04-23 02:19:59.032856',1),(18,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','2','Redeemed coupon FMS-2026-00002 for GMB-310-AA','2026-04-23 21:39:44.583297',1),(19,'Vaisah Peter Zirra','coupon_issue','coupons','3','Issued coupon FMS-2026-00003 for GMB-217-AA','2026-04-23 21:47:35.309136',1),(20,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','3','Redeemed coupon FMS-2026-00003 for GMB-217-AA','2026-04-23 21:50:55.166568',1),(21,'Vaisah Peter Zirra','coupon_issue','coupons','4','Issued coupon FMS-2026-00004 for GMB-217-AA','2026-04-24 13:47:10.158236',1),(22,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','4','Redeemed coupon FMS-2026-00004 for GMB-217-AA','2026-04-24 13:48:15.544749',1),(23,'Vaisah Peter Zirra','coupon_issue','coupons','5','Issued coupon FMS-2026-00005 for GMB-217-AA','2026-04-24 20:52:09.451042',1),(24,'Vaisah Peter Zirra','coupon_issue','coupons','6','Issued coupon NEU-FMS-2026-00001 for GMB-217-AA','2026-04-24 20:57:00.385221',1),(25,'Vaisah Peter Zirra','coupon_issue','coupons','9','Issued coupon NEU/FMS/2026/00001 for GMB-310-AA','2026-04-24 21:00:24.963817',1),(26,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','5','Redeemed coupon NEU/FMS/2026/00001 for GMB-310-AA','2026-04-24 21:01:07.463116',1),(27,'Vaisah Peter Zirra','coupon_issue','coupons','12','Issued coupon FMS-2026-00008 for GMB-217-AA','2026-04-26 06:35:31.576839',1),(28,'Vaisah Peter Zirra','coupon_issue','coupons','13','Issued coupon FMS-2026-00009 for GMB-217-AA','2026-04-26 06:36:34.240355',1),(29,'Vaisah Peter Zirra','coupon_cancel','coupons','13','Cancelled coupon FMS-2026-00009. Reason: DEMO','2026-04-26 06:41:46.410177',1),(30,'Vaisah Peter Zirra','coupon_issue','coupons','14','Issued coupon FMS-2026-00010 for GMB-310-AA','2026-04-26 06:42:57.158458',1),(31,'Vaisah Peter Zirra','coupon_issue','coupons','16','Issued coupon NEU/FMS/2026/00001 for GMB-217-AA','2026-04-26 07:03:36.444002',1),(32,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','6','Redeemed coupon NEU/FMS/2026/00001 for GMB-217-AA','2026-04-26 07:04:00.003275',1),(33,'Vaisah Peter Zirra','coupon_issue','coupons','18','Issued coupon NEU/FMS/2026/00001 for GMB-217-AA','2026-04-27 15:39:31.802697',1),(34,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','7','Redeemed coupon NEU/FMS/2026/00001 for GMB-217-AA','2026-04-27 15:42:48.491331',1),(35,'Vaisah Peter Zirra','create','maintenance','2','Logged Other for GMB-217-AA','2026-04-27 15:47:17.494925',1),(36,'Vaisah Peter Zirra','coupon_issue','coupons','21','Issued coupon FMS-2026-00002 for GMB-217-AA','2026-04-28 02:53:47.752323',1),(37,'Vaisah Peter Zirra','coupon_issue','coupons','22','Issued coupon NEU/FMS/CP/111273 for GMB-217-AA','2026-04-29 15:34:59.356191',1),(38,'Vaisah Peter Zirra','coupon_issue','coupons','23','Issued coupon NEU/FMS/CP/CKRFZKC5 for GMB-217-AA','2026-04-29 18:38:30.997802',1),(39,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','8','Redeemed coupon NEU/FMS/CP/CKRFZKC5 for GMB-217-AA','2026-05-01 01:14:40.564014',1),(40,'Vaisah Peter Zirra','delete','vendors','3','Deleted vendor NNPC Mega Station Gombe','2026-05-01 01:32:02.718028',1),(41,'Vaisah Peter Zirra','delete','vendors','2','Deleted vendor NNPC Mega Station, Gombe','2026-05-01 01:32:05.978543',1),(42,'Test User 1','coupon_issue','coupons','24','Issued coupon NEU/FMS/CP/NL9EA01J for GMB-217-AA','2026-05-02 00:01:29.237431',2),(43,'Test User 1','coupon_redeem','fuel_logs','9','Redeemed coupon NEU/FMS/CP/NL9EA01J for GMB-217-AA','2026-05-02 00:05:02.246029',2),(44,'Test User 1','logout','accounts','2','Test User 1 logged out.','2026-05-02 00:13:12.464691',2),(45,'Vaisah Peter Zirra','logout','accounts','1','Vaisah Peter Zirra logged out.','2026-05-02 00:17:41.186408',1),(46,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-02 00:20:17.980398',1),(47,'Vaisah Peter Zirra','create','vendors','4','Added vendor Total Energies Repair','2026-05-02 00:21:53.610584',1),(48,'Vaisah Peter Zirra','coupon_issue','coupons','25','Issued coupon NEU/FMS/CP/7OSA14Z5 for GMB-217-AA','2026-05-02 00:22:41.282068',1),(49,'Vaisah Peter Zirra','create','maintenance','3','Logged Routine Service for GMB-217-AA','2026-05-02 00:24:26.895896',1),(50,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-02 21:10:03.104087',1),(51,'Vaisah Peter Zirra','coupon_issue','coupons','26','Issued coupon NEU/FMS/CP/EY377ZDP for GMB-217-AA','2026-05-02 21:13:43.469374',1),(52,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','10','Redeemed coupon NEU/FMS/CP/EY377ZDP for GMB-217-AA','2026-05-02 21:26:58.382824',1),(53,'Vaisah Peter Zirra','create','maintenance','4','Logged Other for GMB-217-AA','2026-05-02 21:31:33.985712',1),(54,'Test User 1','login','accounts','2','Test User 1 logged in.','2026-05-02 21:41:18.547404',2),(55,'Test User 1','coupon_issue','coupons','27','Issued coupon NEU/FMS/CP/6M0WWVW4 for GMB-310-AA','2026-05-02 21:44:08.524916',2),(56,'Test User 1','logout','accounts','2','Test User 1 logged out.','2026-05-02 23:09:42.708981',2),(57,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-02 23:14:16.798726',1),(58,'Vaisah Peter Zirra','logout','accounts','1','Vaisah Peter Zirra logged out.','2026-05-02 23:14:52.269661',1),(59,'Vaisah Peter Zirra','edit','drivers','1','Renewed licence for Abba Demo — new expiry 2026-05-04','2026-05-03 03:27:52.500673',1),(60,'Vaisah Peter Zirra','edit','vehicles','2','Updated vehicle GMB-310-AA','2026-05-03 03:28:34.766626',1),(61,'Vaisah Peter Zirra','edit','vehicles','1','Updated vehicle GMB-217-AA','2026-05-03 03:30:53.845682',1),(62,'Vaisah Peter Zirra','coupon_issue','coupons','28','Issued coupon NEU/FMS/CP/8BKTTFUL for GMB-310-AA','2026-05-03 03:31:17.007507',1),(63,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','11','Redeemed coupon NEU/FMS/CP/8BKTTFUL for GMB-310-AA','2026-05-03 03:32:57.945228',1),(64,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-04 00:41:14.587099',1),(65,'Vaisah Peter Zirra','edit','vehicles','fleet_licence','Updated fleet licence expiry to 2026-05-05','2026-05-04 00:44:00.380632',1),(66,'Vaisah Peter Zirra','edit','vehicles','fleet_licence','Updated fleet licence expiry to 2026-05-06','2026-05-04 00:44:13.102577',1),(67,'Vaisah Peter Zirra','coupon_issue','coupons','29','Issued coupon NEU/FMS/CP/A7QFF5QT for GMB-217-AA','2026-05-04 00:44:42.164854',1),(68,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','12','Redeemed coupon NEU/FMS/CP/A7QFF5QT for GMB-217-AA','2026-05-04 00:45:29.543723',1),(69,'Vaisah Peter Zirra','edit','vehicles','2','Updated vehicle GMB-310-AA','2026-05-04 00:48:29.035912',1),(70,'Vaisah Peter Zirra','edit','vehicles','2','Updated vehicle GMB-310-AA','2026-05-04 00:48:34.007518',1),(71,'Vaisah Peter Zirra','create','vehicles','3','Created vehicle GMB-358-AA','2026-05-04 00:49:25.225170',1),(72,'Vaisah Peter Zirra','coupon_issue','coupons','30','Issued coupon NEU/FMS/CP/D72OLSH3 for GMB-358-AA','2026-05-04 00:50:30.592276',1),(73,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','13','Redeemed coupon NEU/FMS/CP/D72OLSH3 for GMB-358-AA','2026-05-04 00:51:12.323728',1),(74,'Vaisah Peter Zirra','edit','vehicles','3','Updated vehicle GMB-358-AA','2026-05-04 00:51:30.667967',1),(75,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-04 10:37:04.354764',1),(76,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','14','Redeemed coupon NEU/FMS/CP/6M0WWVW4 for GMB-310-AA','2026-05-04 13:56:42.676075',1),(77,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','15','Redeemed coupon NEU/FMS/CP/7OSA14Z5 for GMB-217-AA','2026-05-04 13:57:41.568894',1),(78,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-04 22:28:21.111667',1),(79,'Vaisah Peter Zirra','edit','vehicles','1','Updated vehicle GMB-217-AA','2026-05-05 04:53:02.536272',1),(80,'Vaisah Peter Zirra','coupon_issue','coupons','31','Bulk issued coupon NEU/FMS/CP/QIO13WN8 for vehicle #1','2026-05-05 04:58:15.493233',1),(81,'Vaisah Peter Zirra','coupon_issue','coupons','32','Bulk issued coupon NEU/FMS/CP/LZNTI3XS for vehicle #2','2026-05-05 04:58:15.504314',1),(82,'Vaisah Peter Zirra','coupon_issue','coupons','33','Issued coupon NEU/FMS/CP/JZBB5AX4 for GMB-217-AA','2026-05-05 04:58:39.970515',1),(83,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-05 11:43:21.892493',1),(84,'Muhammad Bala Abdullahi','login','accounts','3','Muhammad Bala Abdullahi logged in.','2026-05-05 11:48:25.921658',3),(85,'Muhammad Bala Abdullahi','logout','accounts','3','Muhammad Bala Abdullahi logged out.','2026-05-05 11:49:45.915745',3),(86,'Muhammad Bala Abdullahi','login','accounts','3','Muhammad Bala Abdullahi logged in.','2026-05-05 11:49:53.433625',3),(87,'Muhammad Bala Abdullahi','login','accounts','3','Muhammad Bala Abdullahi logged in.','2026-05-05 11:51:13.346425',3),(88,'Muhammad Bala Abdullahi','edit','accounts','3','Muhammad Bala Abdullahi reset their password via OTP.','2026-05-05 11:52:55.035570',3),(89,'Muhammad Bala Abdullahi','login','accounts','3','Muhammad Bala Abdullahi logged in.','2026-05-05 11:53:07.725344',3),(90,'Muhammad Bala Abdullahi','login','accounts','3','Muhammad Bala Abdullahi logged in.','2026-05-05 11:54:49.361235',3),(91,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-05 13:42:04.714144',1),(92,'Vaisah Peter Zirra','edit','vehicles','fleet_licence','Updated fleet licence expiry to 2026-05-07','2026-05-05 13:44:37.304720',1),(93,'Vaisah Peter Zirra','edit','drivers','1','Renewed licence for Abba Demo — new expiry 2026-05-06','2026-05-05 13:46:12.353000',1),(94,'Vaisah Peter Zirra','edit','vehicles','2','Updated vehicle GMB-310-AA','2026-05-05 13:46:44.919758',1),(95,'Muhammad Bala Abdullahi','login','accounts','3','Muhammad Bala Abdullahi logged in.','2026-05-05 13:47:35.807644',3),(96,'Vaisah Peter Zirra','logout','accounts','1','Vaisah Peter Zirra logged out.','2026-05-05 13:48:57.848751',1),(97,'Abubakar Sadiq Ibrahim','login','accounts','4','Abubakar Sadiq Ibrahim logged in.','2026-05-05 13:49:14.517275',4),(98,'Abubakar Sadiq Ibrahim','logout','accounts','4','Abubakar Sadiq Ibrahim logged out.','2026-05-05 13:49:35.730796',4),(99,'Muhammad Bala Abdullahi','login','accounts','3','Muhammad Bala Abdullahi logged in.','2026-05-05 23:13:10.102611',3),(100,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-05 23:15:09.052179',1),(101,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-06 21:40:23.104064',1),(102,'Vaisah Peter Zirra','logout','accounts','1','Vaisah Peter Zirra logged out.','2026-05-06 21:57:59.322344',1),(103,'Muhammad Bala Abdullahi','login','accounts','3','Muhammad Bala Abdullahi logged in.','2026-05-06 21:58:14.169323',3),(104,'Muhammad Bala Abdullahi','edit','accounts','3','Updated own profile','2026-05-06 21:59:15.004738',3),(105,'Muhammad Bala Abdullahi','logout','accounts','3','Muhammad Bala Abdullahi logged out.','2026-05-06 22:01:20.837001',3),(106,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-06 22:01:31.101993',1),(107,'Muhammad Bala Abdullahi','login','accounts','3','Muhammad Bala Abdullahi logged in.','2026-05-07 19:25:43.670298',3),(108,'Muhammad Bala Abdullahi','logout','accounts','3','Muhammad Bala Abdullahi logged out.','2026-05-07 19:26:02.896774',3),(109,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-07 19:26:11.935940',1),(110,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-08 00:50:43.338316',1),(111,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-09 16:11:52.022028',1),(112,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-11 23:17:38.922753',1),(113,'Vaisah Peter Zirra','edit','vehicles','fleet_licence','Updated fleet licence expiry to 2026-05-13','2026-05-11 23:17:56.781532',1),(114,'Vaisah Peter Zirra','edit','drivers','1','Renewed licence for Abba Demo — new expiry 2026-05-13','2026-05-11 23:18:16.332860',1),(115,'Vaisah Peter Zirra','logout','accounts','1','Vaisah Peter Zirra logged out.','2026-05-11 23:50:54.887203',1),(116,'Zirra Vaisah Peter','login','accounts','5','Zirra Vaisah Peter logged in.','2026-05-11 23:51:01.472702',5),(117,'Zirra Vaisah Peter','coupon_issue','coupons','34','Issued coupon NEU/FMS/CP/5128W7E3 for GMB-217-AA','2026-05-11 23:51:44.386575',5),(118,'Zirra Vaisah Peter','logout','accounts','5','Zirra Vaisah Peter logged out.','2026-05-11 23:52:44.489887',5),(119,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-11 23:52:53.535588',1),(120,'Zirra Vaisah Peter','login','accounts','5','Zirra Vaisah Peter logged in.','2026-05-11 23:54:38.431673',5),(121,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-12 14:11:29.536827',1),(122,'Vaisah Peter Zirra','coupon_issue','coupons','35','Issued coupon NEU/FMS/CP/HE9T0A5G for GMB-217-AA','2026-05-12 14:12:42.969296',1),(123,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-13 10:41:16.222334',1),(124,'Vaisah Peter Zirra','coupon_issue','coupons','36','Issued coupon NEU/FMS/CP/CPUVKPC4 for GMB-217-AA','2026-05-13 10:41:44.394603',1),(125,'Vaisah Peter Zirra','create','maintenance','5','Logged maintenance for GMB-217-AA: 2 items, total ₦7400.00','2026-05-13 11:13:52.468053',1),(126,'Vaisah Peter Zirra','coupon_issue','coupons','37','Issued coupon NEU/FMS/CP/BYEB9836 for GMB-358-AA','2026-05-13 12:03:07.660698',1),(127,'Vaisah Peter Zirra','coupon_issue','coupons','38','Bulk issued coupon NEU/FMS/CP/2T48Z7GC for vehicle #1','2026-05-13 12:09:11.216067',1),(128,'Vaisah Peter Zirra','approve','coupons','38','Approved coupon NEU/FMS/CP/2T48Z7GC (edited: litres 5.00 → 10) [SELF-APPROVED]','2026-05-13 12:09:33.967558',1),(129,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','16','Redeemed coupon NEU/FMS/CP/2T48Z7GC for GMB-217-AA','2026-05-13 16:59:38.815300',1),(130,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','17','Redeemed coupon NEU/FMS/CP/BYEB9836 for GMB-358-AA','2026-05-13 17:00:02.840092',1),(131,'Vaisah Peter Zirra','create','destinations','1','Created destination \'Kalshingi\'','2026-05-13 17:08:29.755197',1),(132,'Vaisah Peter Zirra','create','destinations','2','Created destination \'Haja Mowa (Faculty of Law)\'','2026-05-13 17:08:51.702630',1),(133,'Vaisah Peter Zirra','create','trips','1','Logged trip for Abba Demo: Kalshingi → Haja Mowa (Faculty of Law), ₦49999.99','2026-05-13 17:09:14.681648',1),(134,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-13 22:51:55.353968',1),(135,'Vaisah Peter Zirra','create','generators','1','Registered generator GEN-FOL (Faculty of Law Generator)','2026-05-13 23:24:33.653063',1),(136,'Vaisah Peter Zirra','delete','generators','1','Decommissioned generator GEN-FOL','2026-05-13 23:24:54.482086',1),(137,'Vaisah Peter Zirra','edit','generators','1','Updated generator GEN-FOL','2026-05-13 23:25:01.253459',1),(138,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-14 12:51:22.447546',1),(139,'Vaisah Peter Zirra','create','generators','2','Registered generator GEN-FSC (Jauro Complex (Faculty of Science and Computing))','2026-05-14 20:13:52.678926',1),(140,'Vaisah Peter Zirra','edit','vehicles','fleet_licence','Updated fleet licence expiry to 2026-05-15','2026-05-14 20:47:00.340932',1),(141,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-14 23:36:11.037234',1),(142,'Vaisah Peter Zirra','edit','vehicles','1','Updated vehicle GMB-217-AA','2026-05-14 23:38:04.684441',1),(143,'Vaisah Peter Zirra','coupon_issue','coupons','39','Issued coupon NEU/FMS/CP/5KQHCQWK for GEN-FSC','2026-05-15 00:48:55.373876',1),(144,'Vaisah Peter Zirra','approve','coupons','39','Approved coupon NEU/FMS/CP/5KQHCQWK [SELF-APPROVED]','2026-05-15 00:49:30.437336',1),(145,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','18','Redeemed coupon NEU/FMS/CP/5KQHCQWK for GEN-FSC','2026-05-15 00:50:21.354931',1),(146,'Vaisah Peter Zirra','edit','generators','1','Updated generator GEN-FOL','2026-05-15 00:53:38.126235',1),(147,'Vaisah Peter Zirra','edit','generators','2','Updated generator GEN-FSC','2026-05-15 00:53:58.759947',1),(148,'Vaisah Peter Zirra','create','maintenance','6','Logged maintenance for GEN-FOL: 1 item, total ₦2000.00','2026-05-15 01:10:22.004522',1),(149,'Vaisah Peter Zirra','create','maintenance','7','Logged maintenance for GEN-FOL: 2 items, total ₦7600.00','2026-05-15 01:34:32.707098',1),(150,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-15 22:35:42.433301',1),(151,'Vaisah Peter Zirra','coupon_issue','coupons','40','Issued coupon NEU/FMS/CP/QZPT7DVQ for GEN-FOL','2026-05-15 22:42:08.542797',1),(152,'Vaisah Peter Zirra','approve','coupons','40','Approved coupon NEU/FMS/CP/QZPT7DVQ [SELF-APPROVED]','2026-05-15 22:44:15.994638',1),(153,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','19','Redeemed coupon NEU/FMS/CP/QZPT7DVQ for GEN-FOL','2026-05-15 22:44:48.563181',1),(154,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-16 21:50:29.079905',1),(155,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-18 04:00:57.161101',1),(156,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-19 17:40:44.523967',1),(157,'Vaisah Peter Zirra','edit','settings','1','Saved system settings (no changes)','2026-05-19 17:50:48.046475',1),(158,'Vaisah Peter Zirra','edit','settings','1','Updated system settings: institution_subtitle','2026-05-19 17:50:51.706822',1),(159,'Vaisah Peter Zirra','edit','settings','1','Updated system settings: institution_subtitle','2026-05-19 17:50:58.534376',1),(160,'Vaisah Peter Zirra','logout','accounts','1','Vaisah Peter Zirra logged out.','2026-05-19 17:51:08.988469',1),(161,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-19 18:03:04.851004',1),(162,'Vaisah Peter Zirra','edit','users','4','Resent invite to \'Abubakar Sadiq Ibrahim\' (abubakarsadiqibrahim4321@gmail.com) — email failed (SMTP error).','2026-05-19 18:03:36.408988',1),(163,'Vaisah Peter Zirra','edit','users','5','Resent invite to \'Zirra Vaisah Peter\' (vaisah.zirra@student.neu.edu.ng) — email failed (SMTP error).','2026-05-19 18:04:13.386773',1),(164,'Vaisah Peter Zirra','edit','users','5','Resent invite to \'Zirra Vaisah Peter\' (vaisah.zirra@student.neu.edu.ng) — email failed (SMTP error).','2026-05-19 18:06:44.338592',1),(165,'Vaisah Peter Zirra','edit','users','5','Resent invite to \'Zirra Vaisah Peter\' (vaisah.zirra@student.neu.edu.ng) — email failed (SMTP error).','2026-05-19 18:09:34.846550',1),(166,'Vaisah Peter Zirra','edit','users','5','Resent invite to \'Zirra Vaisah Peter\' (vaisah.zirra@student.neu.edu.ng) — email failed (SMTP error).','2026-05-19 18:10:05.539365',1),(167,'Vaisah Peter Zirra','edit','users','5','Resent invite to \'Zirra Vaisah Peter\' (vaisah.zirra@student.neu.edu.ng) — email failed: SMTPDataError: (553, b\'Sender is not allowed to relay emails\').','2026-05-20 00:20:23.127887',1),(168,'Vaisah Peter Zirra','edit','settings','1','Updated system settings: email_from','2026-05-20 01:04:40.483853',1),(169,'Vaisah Peter Zirra','edit','users','5','Resent invite to \'Zirra Vaisah Peter\' (vaisah.zirra@student.neu.edu.ng) — email sent.','2026-05-20 01:04:58.646351',1),(170,'Vaisah Peter Zirra','edit','users','5','Resent invite to \'Zirra Vaisah Peter\' (vaisah.zirra@student.neu.edu.ng) — email failed: SMTPServerDisconnected: Connection unexpectedly closed: [WinError 10053] An established connection was aborted by the software in your host machine.','2026-05-20 04:32:05.527480',1),(171,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-20 14:08:50.959651',1),(172,'Vaisah Peter Zirra','edit','settings_email','1','Saved SMTP config (no changes)','2026-05-20 14:10:06.147621',1),(173,'Vaisah Peter Zirra','edit','settings_email','1','SMTP test send to vaisahzirra7@gmail.com - OK','2026-05-20 14:27:50.513230',1),(174,'Vaisah Peter Zirra','edit','settings_email','1','Updated SMTP config: smtp_host, smtp_port, smtp_user, smtp_password (updated)','2026-05-20 14:35:32.473253',1),(175,'Vaisah Peter Zirra','edit','settings_email','1','SMTP test send to vaisahzirra7@gmail.com - OK','2026-05-20 14:35:48.824200',1),(176,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-21 11:21:46.670528',1),(177,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-21 12:16:34.800794',1),(178,'Vaisah Peter Zirra','edit','settings_email','1','SMTP test send to vaisahzirra7@gmail.com - failed: SMTPSenderRefused: (530, b\'5.5.1 Authentication Required.\', \'vaisah.zirra@whoisvaisah.name.ng\')','2026-05-21 12:19:40.641496',1),(179,'Vaisah Peter Zirra','edit','settings_email','1','Updated SMTP config: smtp_password (updated)','2026-05-21 12:20:01.574147',1),(180,'Vaisah Peter Zirra','edit','settings_email','1','SMTP test send to vaisahzirra7@gmail.com - OK','2026-05-21 12:20:10.860980',1),(181,'Vaisah Peter Zirra','logout','accounts','1','Vaisah Peter Zirra logged out.','2026-05-21 16:06:21.996308',1),(182,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-21 16:06:33.744227',1),(183,'Vaisah Peter Zirra','coupon_issue','coupons','41','Issued coupon NEU/FMS/CP/D61ZVB27 for GEN-FOL','2026-05-21 16:10:55.947333',1),(184,'Vaisah Peter Zirra','approve','coupons','41','Approved coupon NEU/FMS/CP/D61ZVB27 [SELF-APPROVED]','2026-05-21 16:11:14.368264',1),(185,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-21 21:44:21.226721',1),(186,'Vaisah Peter Zirra','coupon_issue','coupons','42','Issued coupon NEU/FMS/CP/9RTLA6JV for GMB-217-AA','2026-05-21 21:56:35.908041',1),(187,'Vaisah Peter Zirra','approve','coupons','42','Approved coupon NEU/FMS/CP/9RTLA6JV [SELF-APPROVED]','2026-05-21 21:56:41.982716',1),(188,'Vaisah Peter Zirra','create','station_deposits','1','Recorded deposit of ₦100,000.00 to NNPC Mega Station dated 2026-05-21 (ref: test001refbank)','2026-05-21 22:30:22.747167',1),(189,'Vaisah Peter Zirra','coupon_issue','coupons','43','Issued coupon NEU/FMS/CP/7B5RG0SB for GMB-217-AA','2026-05-21 22:30:56.320052',1),(190,'Vaisah Peter Zirra','approve','coupons','43','Bulk-approved coupon NEU/FMS/CP/7B5RG0SB [SELF-APPROVED]','2026-05-21 22:31:24.864018',1),(191,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','1','Redeemed coupon NEU/FMS/CP/7B5RG0SB for GMB-217-AA','2026-05-21 22:40:00.902792',1),(192,'Vaisah Peter Zirra','create','station_deposits','2','Recorded deposit of ₦100,000.00 to NNPC Mega Station dated 2026-05-21','2026-05-21 22:44:06.680641',1),(193,'Vaisah Peter Zirra','coupon_issue','coupons','44','Issued coupon NEU/FMS/CP/WEYZRJU1 for GEN-FOL','2026-05-21 22:44:24.803884',1),(194,'Vaisah Peter Zirra','approve','coupons','44','Approved coupon NEU/FMS/CP/WEYZRJU1 [SELF-APPROVED]','2026-05-21 22:44:29.422331',1),(195,'Vaisah Peter Zirra','delete','station_deposits','2','Deleted deposit #2: ₦100,000.00 to NNPC Mega Station dated 2026-05-21. Original recorder: Vaisah Peter Zirra.','2026-05-21 22:48:53.994222',1),(196,'Vaisah Peter Zirra','coupon_issue','coupons','45','Issued coupon NEU/FMS/CP/7DHCXBNY for GMB-217-AA','2026-05-22 02:49:53.429587',1),(197,'Vaisah Peter Zirra','approve','coupons','45','Approved coupon NEU/FMS/CP/7DHCXBNY [SELF-APPROVED]','2026-05-22 02:51:19.786232',1),(198,'Vaisah Peter Zirra','coupon_issue','coupons','46','Issued coupon NEU/FMS/CP/VEH26ZKK for GMB-217-AA — BALANCE OVERRIDE used by Super Admin (coupon ₦69,000.00 > available ₦26,200.00 at NNPC Mega Station)','2026-05-22 02:52:10.525804',1),(199,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','2','Redeemed coupon NEU/FMS/CP/7DHCXBNY for GMB-217-AA','2026-05-22 02:56:13.150097',1),(200,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','3','Redeemed coupon NEU/FMS/CP/WEYZRJU1 for GEN-FOL','2026-05-22 02:56:25.056084',1),(201,'Vaisah Peter Zirra','approve','coupons','46','Approved coupon NEU/FMS/CP/VEH26ZKK [SELF-APPROVED]','2026-05-22 02:56:44.432964',1),(202,'Vaisah Peter Zirra','coupon_redeem','fuel_logs','4','Redeemed coupon NEU/FMS/CP/VEH26ZKK for GMB-217-AA','2026-05-22 02:56:57.214843',1),(203,'Vaisah Peter Zirra','create','station_deposits','3','Recorded deposit of ₦25,000.00 to NNPC Mega Station dated 2026-05-22 (ref: test003refbank)','2026-05-22 02:57:28.585823',1),(204,'Vaisah Peter Zirra','delete','station_deposits','3','Deleted deposit #3: ₦25,000.00 to NNPC Mega Station dated 2026-05-22 (ref: test003refbank). Original recorder: Vaisah Peter Zirra.','2026-05-22 02:57:48.686300',1),(205,'Vaisah Peter Zirra','create','station_deposits','4','Recorded deposit of ₦250,000.00 to NNPC Mega Station dated 2026-05-01 (ref: test002refbank)','2026-05-22 02:58:02.842042',1),(206,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-22 03:48:24.103469',1),(207,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-22 03:49:36.281800',1),(208,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-22 03:52:42.188847',1),(209,'Vaisah Peter Zirra','coupon_issue','coupons','47','Issued coupon NEU/FMS/CP/DRBOMLZN for GMB-217-AA','2026-05-22 03:53:42.190370',1),(210,'Vaisah Peter Zirra','create','maintenance','8','Logged maintenance for GMB-217-AA: 3 items, total ₦81000.00','2026-05-22 03:56:10.474804',1),(211,'Vaisah Peter Zirra','edit','vehicles','1','Updated vehicle GMB-217-AA','2026-05-22 03:56:22.757551',1),(212,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-22 13:57:11.349221',1),(213,'Vaisah Peter Zirra','login','accounts','1','Vaisah Peter Zirra logged in.','2026-05-24 01:26:11.386799',1);
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=117 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add department',6,'add_department'),(22,'Can change department',6,'change_department'),(23,'Can delete department',6,'delete_department'),(24,'Can view department',6,'view_department'),(25,'Can add role',7,'add_role'),(26,'Can change role',7,'change_role'),(27,'Can delete role',7,'delete_role'),(28,'Can view role',7,'view_role'),(29,'Can add user',8,'add_user'),(30,'Can change user',8,'change_user'),(31,'Can delete user',8,'delete_user'),(32,'Can view user',8,'view_user'),(33,'Can add role module permission',9,'add_rolemodulepermission'),(34,'Can change role module permission',9,'change_rolemodulepermission'),(35,'Can delete role module permission',9,'delete_rolemodulepermission'),(36,'Can view role module permission',9,'view_rolemodulepermission'),(37,'Can add vehicle',10,'add_vehicle'),(38,'Can change vehicle',10,'change_vehicle'),(39,'Can delete vehicle',10,'delete_vehicle'),(40,'Can view vehicle',10,'view_vehicle'),(41,'Can add driver',11,'add_driver'),(42,'Can change driver',11,'change_driver'),(43,'Can delete driver',11,'delete_driver'),(44,'Can view driver',11,'view_driver'),(45,'Can add vendor',12,'add_vendor'),(46,'Can change vendor',12,'change_vendor'),(47,'Can delete vendor',12,'delete_vendor'),(48,'Can view vendor',12,'view_vendor'),(49,'Can add fuel coupon',13,'add_fuelcoupon'),(50,'Can change fuel coupon',13,'change_fuelcoupon'),(51,'Can delete fuel coupon',13,'delete_fuelcoupon'),(52,'Can view fuel coupon',13,'view_fuelcoupon'),(53,'Can add fuel log',14,'add_fuellog'),(54,'Can change fuel log',14,'change_fuellog'),(55,'Can delete fuel log',14,'delete_fuellog'),(56,'Can view fuel log',14,'view_fuellog'),(57,'Can add maintenance record',15,'add_maintenancerecord'),(58,'Can change maintenance record',15,'change_maintenancerecord'),(59,'Can delete maintenance record',15,'delete_maintenancerecord'),(60,'Can view maintenance record',15,'view_maintenancerecord'),(61,'Can add audit log',16,'add_auditlog'),(62,'Can change audit log',16,'change_auditlog'),(63,'Can delete audit log',16,'delete_auditlog'),(64,'Can view audit log',16,'view_auditlog'),(65,'Can add password reset otp',17,'add_passwordresetotp'),(66,'Can change password reset otp',17,'change_passwordresetotp'),(67,'Can delete password reset otp',17,'delete_passwordresetotp'),(68,'Can view password reset otp',17,'view_passwordresetotp'),(69,'Can add Fleet Licence Expiry',18,'add_fleetlicenceexpiry'),(70,'Can change Fleet Licence Expiry',18,'change_fleetlicenceexpiry'),(71,'Can delete Fleet Licence Expiry',18,'delete_fleetlicenceexpiry'),(72,'Can view Fleet Licence Expiry',18,'view_fleetlicenceexpiry'),(73,'Can add monthly fuel dismissal',19,'add_monthlyfueldismissal'),(74,'Can change monthly fuel dismissal',19,'change_monthlyfueldismissal'),(75,'Can delete monthly fuel dismissal',19,'delete_monthlyfueldismissal'),(76,'Can view monthly fuel dismissal',19,'view_monthlyfueldismissal'),(77,'Can add driver licence renewal',20,'add_driverlicencerenewal'),(78,'Can change driver licence renewal',20,'change_driverlicencerenewal'),(79,'Can delete driver licence renewal',20,'delete_driverlicencerenewal'),(80,'Can view driver licence renewal',20,'view_driverlicencerenewal'),(81,'Can add driver vehicle assignment',21,'add_drivervehicleassignment'),(82,'Can change driver vehicle assignment',21,'change_drivervehicleassignment'),(83,'Can delete driver vehicle assignment',21,'delete_drivervehicleassignment'),(84,'Can view driver vehicle assignment',21,'view_drivervehicleassignment'),(85,'Can add report schedule',22,'add_reportschedule'),(86,'Can change report schedule',22,'change_reportschedule'),(87,'Can delete report schedule',22,'delete_reportschedule'),(88,'Can view report schedule',22,'view_reportschedule'),(89,'Can add maintenance item',23,'add_maintenanceitem'),(90,'Can change maintenance item',23,'change_maintenanceitem'),(91,'Can delete maintenance item',23,'delete_maintenanceitem'),(92,'Can view maintenance item',23,'view_maintenanceitem'),(93,'Can add destination',24,'add_destination'),(94,'Can change destination',24,'change_destination'),(95,'Can delete destination',24,'delete_destination'),(96,'Can view destination',24,'view_destination'),(97,'Can add trip',25,'add_trip'),(98,'Can change trip',25,'change_trip'),(99,'Can delete trip',25,'delete_trip'),(100,'Can view trip',25,'view_trip'),(101,'Can add generator',26,'add_generator'),(102,'Can change generator',26,'change_generator'),(103,'Can delete generator',26,'delete_generator'),(104,'Can view generator',26,'view_generator'),(105,'Can add System Settings',27,'add_systemsettings'),(106,'Can change System Settings',27,'change_systemsettings'),(107,'Can delete System Settings',27,'delete_systemsettings'),(108,'Can view System Settings',27,'view_systemsettings'),(109,'Can add user invite',28,'add_userinvite'),(110,'Can change user invite',28,'change_userinvite'),(111,'Can delete user invite',28,'delete_userinvite'),(112,'Can view user invite',28,'view_userinvite'),(113,'Can add station deposit',29,'add_stationdeposit'),(114,'Can change station deposit',29,'change_stationdeposit'),(115,'Can delete station deposit',29,'delete_stationdeposit'),(116,'Can view station deposit',29,'view_stationdeposit');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `departments`
--

DROP TABLE IF EXISTS `departments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `departments` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `code` varchar(20) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `departments`
--

LOCK TABLES `departments` WRITE;
/*!40000 ALTER TABLE `departments` DISABLE KEYS */;
INSERT INTO `departments` VALUES (1,'General','GENERAL',1,'2026-04-21 00:05:33.853904'),(2,'Vice Chancellor','VC',1,'2026-04-21 00:11:52.829070'),(3,'SIWES','SIWES',1,'2026-05-02 21:36:00.879182');
/*!40000 ALTER TABLE `departments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `destinations`
--

DROP TABLE IF EXISTS `destinations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `destinations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `code` varchar(20) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `destinations_created_by_id_112a226b_fk_users_id` (`created_by_id`),
  CONSTRAINT `destinations_created_by_id_112a226b_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `destinations`
--

LOCK TABLES `destinations` WRITE;
/*!40000 ALTER TABLE `destinations` DISABLE KEYS */;
INSERT INTO `destinations` VALUES (1,'Kalshingi','KLS',1,'','2026-05-13 17:08:29.749037','2026-05-13 17:08:29.749058',1),(2,'Haja Mowa (Faculty of Law)','HM-FOL',1,'','2026-05-13 17:08:51.698943','2026-05-13 17:08:51.698959',1);
/*!40000 ALTER TABLE `destinations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_users_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (6,'accounts','department'),(17,'accounts','passwordresetotp'),(7,'accounts','role'),(9,'accounts','rolemodulepermission'),(8,'accounts','user'),(28,'accounts','userinvite'),(1,'admin','logentry'),(16,'audit','auditlog'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(13,'coupons','fuelcoupon'),(11,'drivers','driver'),(20,'drivers','driverlicencerenewal'),(14,'fuel_logs','fuellog'),(26,'generators','generator'),(23,'maintenance','maintenanceitem'),(15,'maintenance','maintenancerecord'),(22,'reports','reportschedule'),(5,'sessions','session'),(29,'station_deposits','stationdeposit'),(27,'system_settings','systemsettings'),(24,'trips','destination'),(25,'trips','trip'),(21,'vehicles','drivervehicleassignment'),(18,'vehicles','fleetlicenceexpiry'),(19,'vehicles','monthlyfueldismissal'),(10,'vehicles','vehicle'),(12,'vendors','vendor');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-04-19 01:40:58.074520'),(2,'contenttypes','0002_remove_content_type_name','2026-04-19 01:40:58.335117'),(3,'auth','0001_initial','2026-04-19 01:40:58.756719'),(4,'auth','0002_alter_permission_name_max_length','2026-04-19 01:40:58.855734'),(5,'auth','0003_alter_user_email_max_length','2026-04-19 01:40:58.863031'),(6,'auth','0004_alter_user_username_opts','2026-04-19 01:40:58.871280'),(7,'auth','0005_alter_user_last_login_null','2026-04-19 01:40:58.880871'),(8,'auth','0006_require_contenttypes_0002','2026-04-19 01:40:58.887649'),(9,'auth','0007_alter_validators_add_error_messages','2026-04-19 01:40:58.901985'),(10,'auth','0008_alter_user_username_max_length','2026-04-19 01:40:58.915440'),(11,'auth','0009_alter_user_last_name_max_length','2026-04-19 01:40:58.933120'),(12,'auth','0010_alter_group_name_max_length','2026-04-19 01:40:58.963053'),(13,'auth','0011_update_proxy_permissions','2026-04-19 01:40:58.973552'),(14,'auth','0012_alter_user_first_name_max_length','2026-04-19 01:40:58.981750'),(15,'accounts','0001_initial','2026-04-19 01:41:00.075339'),(16,'admin','0001_initial','2026-04-19 01:41:00.330350'),(17,'admin','0002_logentry_remove_auto_add','2026-04-19 01:41:00.343791'),(18,'admin','0003_logentry_add_action_flag_choices','2026-04-19 01:41:00.359111'),(19,'audit','0001_initial','2026-04-19 01:41:00.492414'),(20,'vendors','0001_initial','2026-04-19 01:41:00.552795'),(21,'drivers','0001_initial','2026-04-19 01:41:00.599022'),(22,'vehicles','0001_initial','2026-04-19 01:41:00.870731'),(23,'coupons','0001_initial','2026-04-19 01:41:01.360734'),(24,'fuel_logs','0001_initial','2026-04-19 01:41:01.900360'),(25,'maintenance','0001_initial','2026-04-19 01:41:02.243371'),(26,'sessions','0001_initial','2026-04-19 01:41:02.307000'),(27,'coupons','0002_alter_fuelcoupon_coupon_id_and_more','2026-04-29 15:29:48.077546'),(28,'coupons','0003_remove_fuelcoupon_fuel_coupon_coupon__08ca11_idx_and_more','2026-04-29 23:55:35.315004'),(29,'accounts','0002_user_must_change_password','2026-05-01 23:43:37.842460'),(30,'accounts','0003_passwordresetotp','2026-05-02 20:51:35.566837'),(31,'drivers','0002_driverlicencerenewal','2026-05-03 03:26:46.226222'),(32,'vehicles','0002_fleetlicenceexpiry_vehicle_needs_monthly_fuel_and_more','2026-05-03 03:26:46.512561'),(33,'reports','0001_initial','2026-05-05 04:52:08.545209'),(34,'vehicles','0003_drivervehicleassignment','2026-05-05 04:52:08.807320'),(35,'reports','0002_alter_reportschedule_id_alter_reportschedule_name_and_more','2026-05-11 23:17:01.678327'),(36,'accounts','0004_rolemodulepermission_can_approve_and_more','2026-05-13 10:40:53.383996'),(37,'audit','0002_auditlog_approve_reject_actions','2026-05-13 10:40:53.420036'),(38,'audit','0003_alter_auditlog_action','2026-05-13 10:40:53.442186'),(39,'coupons','0004_fuelcoupon_approved_at_fuelcoupon_approved_by_and_more','2026-05-13 10:40:54.364328'),(40,'drivers','0003_driver_payment_type','2026-05-13 10:40:54.511458'),(41,'maintenance','0002_alter_maintenancerecord_description_and_more','2026-05-13 10:40:54.782796'),(42,'maintenance','0003_backfill_maintenance_items','2026-05-13 10:40:54.854359'),(43,'trips','0001_initial','2026-05-13 10:40:56.175796'),(44,'audit','0004_alter_auditlog_action','2026-05-13 15:33:58.542621'),(45,'accounts','0005_add_generators_module','2026-05-13 23:17:25.473991'),(46,'generators','0001_initial','2026-05-13 23:17:25.847358'),(47,'generators','0002_generator_needs_monthly_fuel','2026-05-13 23:17:26.014802'),(48,'generators','0003_replace_department_with_building','2026-05-14 20:02:24.089610'),(49,'coupons','0005_coupon_generator_support','2026-05-15 00:47:59.673311'),(50,'fuel_logs','0002_fuellog_generator_support','2026-05-15 00:48:00.699433'),(51,'fuel_logs','0003_alter_fuellog_coupon_alter_fuellog_fuel_date','2026-05-15 00:48:00.770067'),(52,'maintenance','0004_maintenance_generator_support','2026-05-15 01:08:09.330408'),(53,'reports','0003_add_generator_spending_to_schedule','2026-05-18 04:17:11.969843'),(54,'accounts','0006_add_settings_module','2026-05-19 17:47:16.504209'),(55,'system_settings','0001_initial','2026-05-19 17:47:16.742472'),(56,'accounts','0007_userinvite','2026-05-19 18:02:45.037405'),(57,'accounts','0008_add_settings_email_module','2026-05-20 14:08:21.003026'),(58,'system_settings','0002_smtp_fields','2026-05-20 14:08:21.845806'),(59,'accounts','0009_add_station_deposits_module','2026-05-21 21:44:07.880441'),(60,'accounts','0010_alter_rolemodulepermission_module','2026-05-21 21:44:07.891933'),(61,'station_deposits','0001_initial','2026-05-21 21:44:08.171638'),(62,'station_deposits','0002_rename_station_dep_vendor_d_idx_station_dep_vendor__94be3a_idx','2026-05-21 21:44:08.216860'),(63,'system_settings','0003_low_balance_threshold','2026-05-21 21:44:08.278466'),(64,'coupons','0006_fuelcoupon_issued_with_override','2026-05-22 02:40:28.048110');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('0xce93ly5lwi2v1basyhh68w93btpeyo','.eJxVjMsOgjAQAP9lz6bptrZ0OXrnG8huH4IamlA4Gf_dkHDQ68xk3jDyvk3j3vI6zgl6QLj8MuH4zMsh0oOXe1WxLts6izoSddqmhpry63a2f4OJ2wQ96M5FQ146SvaKUkIhywWdjkZYk0Gdk9EByQvHErrkXfBYjJAYcrbA5wvRjTd4:1wQxbX:etCtR9edYxN3fYmVAZfqmgT1GdnWZazG-Z5ePrKqCSs','2026-05-24 09:26:11.391108'),('0z5b4fz3dlsg1v4d1lcnj2fdd44bnwnr','.eJxVjDkOwjAQAP-yNbJ8xFdKet5g7dprHECJFCcV4u8oUgpoZ0bzhoT71tLeeU1TgREMXH4ZYX7yfIjywPm-iLzM2zqROBJx2i5uS-HX9Wz_Bg17gxEU1moccdXB6jBwQJTFaRu1DERx8J4UmjKgVcSepY1VM_rCwSnCbODzBe-COF8:1wKOww:SN4n0WaeO4hA1eZDKJ-QZSZ4l2P6iYzyMS5ZGZ7A9Bs','2026-05-06 07:13:10.111353'),('14u2m2xhnvrc5g9gyjk6lt9iug25iqxu','.eJxVjMsOgjAQAP9lz6bptrZ0OXrnG8huH4IamlA4Gf_dkHDQ68xk3jDyvk3j3vI6zgl6QLj8MuH4zMsh0oOXe1WxLts6izoSddqmhpry63a2f4OJ2wQ96M5FQ146SvaKUkIhywWdjkZYk0Gdk9EByQvHErrkXfBYjJAYcrbA5wvRjTd4:1wQBBl:_p9X4X25mbCS7ZvGFXTwNbCShki3Z0CKgdFk5IRaOlA','2026-05-22 05:44:21.230850'),('1sqhrlu16r2scx9bleizd792pxqbj5l2','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wEyT8:ZMdS9_VyyCXdwZmuj0KfqzcYDh64poFsY0EuIcwQA6Q','2026-04-21 07:55:58.987386'),('2d9pxqp1yek408e234l453g8vpmaq92j','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wK1m1:HgerFicIdkR--9_gY_URtluFrGdsRSWASRuVonzD7Ok','2026-05-05 06:28:21.117171'),('2kas7n85qzfnz1b4zcwn8bkb0w71e7pt','.eJxVjMsOgjAQAP9lz6bptrZ0OXrnG8huH4IamlA4Gf_dkHDQ68xk3jDyvk3j3vI6zgl6QLj8MuH4zMsh0oOXe1WxLts6izoSddqmhpry63a2f4OJ2wQ96M5FQ146SvaKUkIhywWdjkZYk0Gdk9EByQvHErrkXfBYjJAYcrbA5wvRjTd4:1wQ5ur:oXI31CQv4BZVUeNVdLsnZAbT14nyuavZRFZoYDxNTrY','2026-05-22 00:06:33.748117'),('39qw9kdlhwy3g55zh7oohujrb4suzu4q','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wOMtx:w_eA1FUWXMl1AOGlwKB0UCgepQTrgejQF2nd4csy-og','2026-05-17 05:50:29.083831'),('4w6j1l9s4p7hdbqbanar6119uf6dcazs','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wFeml:3OHMxZfw8cXmyslFo0qoBf5c7SW4BCJymW-7Z3y5ZAI','2026-04-23 05:07:03.943861'),('4z8st19dt9luphjqglj88x85plt2rvbt','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wGnR6:wAgYCKuTcF_CtLBEb0tAiAsoDbgLh9QjZ-Pjaev_OrM','2026-04-26 08:33:24.475154'),('6pv643ls1xuq8jtnuhqhh6gl7wkn9cpi','.eJxVjMsKwjAQAP9lzxLIo9lsj979hrDJJqYqLTTtSfx3KfSg15lh3hB531rce1njJDCChcsvS5yfZT6EPHi-Lyov87ZOSR2JOm1Xt0XK63q2f4PGvcEIGR0mg-TRp-oRs5YgyRVCa4z1mMmyHUp1lYlEp-BILJOuRVMOg4PPF9deN6Q:1wKEIz:8t8OjOqMn9xXZbRJcaP1k3gi7oxmb0hBUNdw7l-wSxM','2026-05-05 19:51:13.351551'),('79gdhh47jjr8hgzu4an4gdgkrt35850v','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wNfb9:H2IKt8AZNyrRsgfOateYCD4bWhX--T1cRw6u5LnuMC8','2026-05-15 07:36:11.062304'),('7fcaf56hpw2c9zmwl0545njq816kppko','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wL9QR:vWrp1zby5VUZvFhdbTgPLcy3owDkD0OYvJKc76a7N8I','2026-05-08 08:50:43.342544'),('7l5xe4neehfeajkhyillgmbe95pr12cb','.eJxVjDkOwjAQAP-yNbJ8xFdKet5g7dprHECJFCcV4u8oUgpoZ0bzhoT71tLeeU1TgREMXH4ZYX7yfIjywPm-iLzM2zqROBJx2i5uS-HX9Wz_Bg17gxEU1moccdXB6jBwQJTFaRu1DERx8J4UmjKgVcSepY1VM_rCwSnCbODzBe-COF8:1wKEMT:qXiB30FT9NP-glZ2rahZvnJFqcTaBTbTeUZ7lY6ktqA','2026-05-05 19:54:49.366764'),('8cgrwfgw99u6ofa6shl5tgh48b20aqd7','.eJxVjMsOgjAQAP9lz6bptrZ0OXrnG8huH4IamlA4Gf_dkHDQ68xk3jDyvk3j3vI6zgl6QLj8MuH4zMsh0oOXe1WxLts6izoSddqmhpry63a2f4OJ2wQ96M5FQ146SvaKUkIhywWdjkZYk0Gdk9EByQvHErrkXfBYjJAYcrbA5wvRjTd4:1wQGs4:0Uf1J33TairQROE2q3MgYEP1cyvICG9mB1PJxvA6So4','2026-05-22 11:48:24.107054'),('8mv0tvw1rhcv9pybhyjgw9b461wvpbor','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wNVX8:uimC2exwnKi7Xi1g-TMpcvNL6DdGZxKdwHYMixwO0tw','2026-05-14 20:51:22.451292'),('8pbi8v3cnetj5ykjdhdz5tkhx3p9pwh9','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wKOyr:-G5woZFIiyDQ-IKP__4yewsv1QrNAu1FqBlWMd5893I','2026-05-06 07:15:09.057791'),('901rdjb0jen13txylrsx1ykwyddddh23','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wOpA1:MG9R1-81TAoucfX_SoneT5id8UNN9VbXHCMlUJBdR98','2026-05-18 12:00:57.164937'),('95x4jswut40omeq07m1o1xv3zwbkvulr','.eJxVjMsKwjAQAP9lzxLIo9lsj979hrDJJqYqLTTtSfx3KfSg15lh3hB531rce1njJDCChcsvS5yfZT6EPHi-Lyov87ZOSR2JOm1Xt0XK63q2f4PGvcEIGR0mg-TRp-oRs5YgyRVCa4z1mMmyHUp1lYlEp-BILJOuRVMOg4PPF9deN6Q:1wKEHh:4NcyHHXtPXtG-VTavYFW9huerpbX6ews-9_suRCdvek','2026-05-05 19:49:53.440138'),('9c6n8p9ba86n46fycemo1xwpp86iv86p','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wIElW:ENIVLm2t8mMeBWd7wdEGjky0lLLBhRaAWDNfjSyqhxk','2026-04-30 07:56:26.453576'),('9ocrwvb0he0z9dx20fnqiokgdza40cup','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wPhbO:J4HayqAhEnXhRERQtu08t37lfJ7Lxv3P1mtT8gtDFeo','2026-05-20 22:08:50.971801'),('ay4wtodzhjgg2cjiewxst7xzl27ya06u','.eJxVjDkOwjAQAP-yNbJ8xFdKet5g7dprHECJFCcV4u8oUgpoZ0bzhoT71tLeeU1TgREMXH4ZYX7yfIjywPm-iLzM2zqROBJx2i5uS-HX9Wz_Bg17gxEU1moccdXB6jBwQJTFaRu1DERx8J4UmjKgVcSepY1VM_rCwSnCbODzBe-COF8:1wKG7b:TksOJZI4AvLIdimU3JGWnyIRvOSAj3WH3p7CILQG9hU','2026-05-05 21:47:35.811944'),('cb8l2cwey2yd04jeoqnler20invx1xss','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wI5I4:ewusjIb-g-DtaNnqoGsyi4IqhC-Rgm6xZGrXQFRT7vY','2026-04-29 21:49:24.445761'),('cjwpk67jwyixhxr6hxgm8x3mz8io9nml','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wEnxC:gSN7RcXCoRWJD1J83Be-RAcJ9vj69piHIBXMuKDcxoY','2026-04-20 20:42:18.291024'),('cp1ink39obzwz7ggbhkhs3vh14p0nbww','.eJxVjDkOwjAQAP-yNbJ8xFdKet5g7dprHECJFCcV4u8oUgpoZ0bzhoT71tLeeU1TgREMXH4ZYX7yfIjywPm-iLzM2zqROBJx2i5uS-HX9Wz_Bg17gxEU1moccdXB6jBwQJTFaRu1DERx8J4UmjKgVcSepY1VM_rCwSnCbODzBe-COF8:1wKEKp:g8CIDVQ2OZRs6vmzqc5Um5sDqAMO7G8rqtF6QQK-abA','2026-05-05 19:53:07.730614'),('ctcu8enhgrigg2f7yjvaje9x50x8lcn0','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wLkHQ:HEYmEwzlVq9Jhcth3eNs88cpE34Lr5w18HV5oInZsYo','2026-05-10 00:11:52.028015'),('dfzd7jblt41w77z111n8jipqz9q3inwy','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wO18A:_45AG2dpNcOmlkwYWz0rh74S4Tcv5eSmqn4jsjKPSak','2026-05-16 06:35:42.441170'),('doyfqym525bhlco30t1s9ue92egghmbw','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wHkJX:KtBG43pVKbHkPF8LJTMky8FB-WbH3tvmWHVU9lV5dng','2026-04-28 23:25:31.903674'),('drzd6ktxtrbctreetkwc4l0prcv4swuz','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wPOmW:2viysfnyI58S475R36qJyJh8zNWEW2ct6zcPXvyBQiU','2026-05-20 02:03:04.870730'),('eoalsg7q3t6bw3zg6715bekzl15xsque','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wH4Xt:pL42BB4qPt6JEMinon-ttT1-0nPFbbM9DzAYdD1qPW0','2026-04-27 02:49:33.590190'),('gxtbv52zifaiv0t4dug7jdlm2k79m9kr','eyJyZXNldF9lbWFpbCI6ImFidWJha2Fyc2FkaXFpYnJhaGltNDMyMUBnbWFpbC5jb20ifQ:1wKG9g:HqC-SZZ3G_up5fIegbnzsN6Y8TR5M3M_pAt8OSu52bE','2026-05-05 21:49:44.097462'),('huqemele38qf4q9sreo9a55zxqky0c1k','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wKkJ9:6g2imMa4OKcCccDbI6nh1CzTbG4gffMEfL-AePzLnwA','2026-05-07 06:01:31.107130'),('i8ll8bxiw103gl09dwc53ec48ncvdp95','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wG1lB:pAOeQugxzYs_KWoxp7AQs6djxSz-vFghlIv-SbA0XWU','2026-04-24 05:38:57.740996'),('iiqllwjj2yrria3ft8khvc5ki3aobmm3','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wI6w2:yum7qUCWjJpQI0Jks94ANRQcg_NgViGTSGYa79uzqAY','2026-04-29 23:34:46.252143'),('ijdw2d4kcuy8ry5da9k4mz3ag8no9ojs','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wN71g:DndcViHUk8SgcNhuygNZRTm9Dr9RkBPdvycZSZFR_OQ','2026-05-13 18:41:16.228390'),('j2pkve4yuoaas4n5ozttlvjiic67m2j9','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wKEBN:ZP3zXjy0h1B0FG6XjEGYzW42uiFf868hMbJnyJEdCcY','2026-05-05 19:43:21.897607'),('jtcug8p3sp9maqea4wze8lu4ifldbxti','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wIy5h:Blpmz8t5FREqmy69HCpOx_MzZAzloVthn3E1DFpguyw','2026-05-02 08:20:17.986526'),('k39fhi11gscin5gi18ocwx2rl0hr1h1e','.eJxVjEEOgkAMAP_Ss9nspu0qHL37BtLS4qIGEhZOxr8bEg56nZnMGzrZ1tJt1ZduNGiB4fTLVPqnT7uwh0z3OfTztC6jhj0Jh63hNpu_rkf7NyhSC7RAMZkk0kFowKTsqoQWnR2FKUdC84RR8UKNZyZi7E3YPUuTTc_w-QLs6Tgc:1wMaSM:4iYzSflakbBNmqQQyY4byMstPyqVM-9n1FNobxyqfyY','2026-05-12 07:54:38.442428'),('k8omulotsvd0tk75t8qr6ctuxedziluz','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wMnpZ:un42Rt7YaiNgES9fOyknD4rMA7ITOlisGiQVJ9TnDYg','2026-05-12 22:11:29.545670'),('kcue8nd0ht54sx2vx61oliw27b9lots9','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wGmu1:J9QdcvWmJNYE68AVXnR2PkXhoC7mqnOygOwsiGhFAe8','2026-04-26 07:59:13.011651'),('n79d0n7tvramzfuonwmgl6la7l5bz5vj','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wL4MN:wcyB9vNvpVe11xXxO7S30R9k82UYonOBTHjn2OQ-fSY','2026-05-08 03:26:11.943188'),('nd3eu3tz7fsxerd4q1pxpacefihvxh0n','eyJyZXNldF9lbWFpbCI6InZhaXNhaC56aXJyYUBzdHVkZW50Lm5ldS5lZHUubmcifQ:1wPOto:6K0RA0tT3ODXZVVveuDVz8EFdhKsBlXm2Gobn4uGvGA','2026-05-20 02:10:36.425472'),('o9c5muel3ty4e2mzqixynwxfzylg3k6s','.eJxVjMsOgjAQAP9lz6bptrZ0OXrnG8huH4IamlA4Gf_dkHDQ68xk3jDyvk3j3vI6zgl6QLj8MuH4zMsh0oOXe1WxLts6izoSddqmhpry63a2f4OJ2wQ96M5FQ146SvaKUkIhywWdjkZYk0Gdk9EByQvHErrkXfBYjJAYcrbA5wvRjTd4:1wQGtE:6ynLq59HBGsWAkTPzz1DLEGxP2nH3D8kv695qo4KOLM','2026-05-22 11:49:36.285362'),('ogdxddczzl66yz9p47vpd1cq7kpfahba','.eJxVjMsOgjAQAP9lz6bptrZ0OXrnG8huH4IamlA4Gf_dkHDQ68xk3jDyvk3j3vI6zgl6QLj8MuH4zMsh0oOXe1WxLts6izoSddqmhpry63a2f4OJ2wQ96M5FQ146SvaKUkIhywWdjkZYk0Gdk9EByQvHErrkXfBYjJAYcrbA5wvRjTd4:1wQGwE:ecTkwEIfKvZMsqZ7y0yptUQoN3euXoHyCkoxgNbSwZA','2026-05-22 11:52:42.193026'),('q5yzqhlyjjd42sskyif6udv285jc6eoy','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wGNV2:38YqwsAj8U67VMh_3cBlqToYGiar8Ke8KsY5tZUVkqQ','2026-04-25 04:51:44.442614'),('rel9qp7ei2widd2o8oceq8kyx0fv28u7','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wEZDj:47wHsGTiJrXVWKvv9bs_3-qctBSdzrdL835lNo2zYy4','2026-04-20 04:58:23.087534'),('rpjlyhbbflgzufk60kc62gb6irb05e9y','.eJxVjDsOgkAUAO_yarPhIQtIZew9A3k_ZJVPsgsWGu9uSGhoZybzhWjJltZGCgM08KaQqP-EGKm6PjboZB7hBC2tS9-uyWIbFBrAI2OSl02b0CdNj9nJPC0xsNsSt9vk7rPacNvbw6Cn1EMDnFXMnUe8ZDkj0ZmKmq0mKeXsDcUq9ZhnueaiXNbo_aUrpUAlVC2F4fcHe0FGpg:1wJHb9:HY0Us0SMAvHrAUGVwyKRlFVGZaeQM1QxzMX2Gp7P2Is','2026-05-03 05:10:03.109217'),('rtvnr582y7oziehavqdlivgluohrgpol','eyJyZXNldF9lbWFpbCI6InZhaXNhaC56aXJyYUBzdHVkZW50Lm5ldS5lZHUubmcifQ:1wJJZD:qZnQ5_QN86wD0i9EzFLwMCzoCys0ExZGcQpkRPc1XXM','2026-05-03 07:16:11.513049'),('ttw9alv36r88qebhp5uftaz6otyzub3b','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wNIQl:9HUf7ES3QTz6btO_udZwkI1Jg6uA_6bo4idihI0AHyE','2026-05-14 06:51:55.364178'),('vq77iuzsa53aqu8e79kzuqqt2k6yns0m','.eJxVjDsOgkAUAO_yarPhIQtIZew9A3k_ZJVPsgsWGu9uSGhoZybzhWjJltZGCgM08KaQqP-EGKm6PjboZB7hBC2tS9-uyWIbFBrAI2OSl02b0CdNj9nJPC0xsNsSt9vk7rPacNvbw6Cn1EMDnFXMnUe8ZDkj0ZmKmq0mKeXsDcUq9ZhnueaiXNbo_aUrpUAlVC2F4fcHe0FGpg:1wJqfg:uDGHP9g7-Sxuzl5KxMkCY_UXjdfbg19d67MD1S94OVg','2026-05-04 18:37:04.361287'),('vs3x0ibgi2yopodze06oojmxp9l0zdbr','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wIcRz:UKeaZNKi7VERoe0dIeDq7yXgqPB_T_zkxJIELKbdjzw','2026-05-01 09:13:51.975909'),('x2wjcealwyo5o0ur6tpp7yp2m94djbuz','.eJxVjMsOgjAQAP9lz6bptrZ0OXrnG8huH4IamlA4Gf_dkHDQ68xk3jDyvk3j3vI6zgl6QLj8MuH4zMsh0oOXe1WxLts6izoSddqmhpry63a2f4OJ2wQ96M5FQ146SvaKUkIhywWdjkZYk0Gdk9EByQvHErrkXfBYjJAYcrbA5wvRjTd4:1wQQND:GPi98lyrpwgISl1u9V1scocnVQpZwZOCCz8LTn2wwWo','2026-05-22 21:57:11.358295'),('yzzpgb0a2aexckhgcf3bxn2dq1q3l77i','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wMaQf:ZgVv8yQ7dXkc5M57VHJVwe-UrGGxTGcR-rtAcgEz7Sg','2026-05-12 07:52:53.545395'),('z2g9jpjidvoduxe0sjun9dqipt40jn9w','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wHYQ0:YAPwoYgnE5TUT3xE6wVF4F34OSDYingQLqzyH4KwH2s','2026-04-28 10:43:24.655788'),('z34nnzu70ys3q0v2aeabz7am2u6n6ugt','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wJhN4:vgpil5lF6iZQCRvlpZsve4WY7sud4bH7sIxAS1wzBPY','2026-05-04 08:41:14.594308'),('zlcm96d86vzkjpouzoo1pdzplyw7aeru','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wFAbR:GcgIcWDNcFWNbK3P72oqg-5fPV2PLnSF9R9JwOkN6IE','2026-04-21 20:53:21.962995'),('zwe4qa53atc3fv7nbs1z1diaad2j3kdh','.eJxVjEsOgjAUAO_y1qbpK7QUlu49A3mfIqhpEwor490NCQvdzkzmDSPt2zzuNa3jojAAwuWXMckz5UPog_K9GCl5Wxc2R2JOW82taHpdz_ZvMFOdYQC2HfPkEXvrGIkaaiOnSBKk8QklderRWadOlENE7_spSItKqBqE4fMF9kc4nA:1wHNzx:-H47K49KlN7GWIKtJ9trNOkA6ycJRIMnEkcnqfVxiL0','2026-04-27 23:35:49.592375');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `driver_licence_renewals`
--

DROP TABLE IF EXISTS `driver_licence_renewals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `driver_licence_renewals` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `new_license_no` varchar(50) NOT NULL,
  `new_expiry` date NOT NULL,
  `renewed_by` varchar(150) NOT NULL,
  `notes` longtext NOT NULL,
  `renewed_at` datetime(6) NOT NULL,
  `driver_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `driver_licence_renewals_driver_id_db60d98d_fk_drivers_id` (`driver_id`),
  CONSTRAINT `driver_licence_renewals_driver_id_db60d98d_fk_drivers_id` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `driver_licence_renewals`
--

LOCK TABLES `driver_licence_renewals` WRITE;
/*!40000 ALTER TABLE `driver_licence_renewals` DISABLE KEYS */;
INSERT INTO `driver_licence_renewals` VALUES (1,'NA/NUM','2026-05-04','Vaisah Peter Zirra','','2026-05-03 03:27:52.496808',1),(2,'NA/NUM','2026-05-06','Vaisah Peter Zirra','','2026-05-05 13:46:12.348421',1),(3,'NA/NUM','2026-05-13','Vaisah Peter Zirra','','2026-05-11 23:18:16.312124',1);
/*!40000 ALTER TABLE `driver_licence_renewals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `driver_vehicle_assignments`
--

DROP TABLE IF EXISTS `driver_vehicle_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `driver_vehicle_assignments` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `driver_name` varchar(150) NOT NULL,
  `assigned_by` varchar(150) NOT NULL,
  `assigned_at` datetime(6) NOT NULL,
  `notes` longtext NOT NULL,
  `driver_id` bigint DEFAULT NULL,
  `vehicle_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `driver_vehicle_assignments_driver_id_e64334b4_fk_drivers_id` (`driver_id`),
  KEY `driver_vehicle_assignments_vehicle_id_0d6b4963_fk_vehicles_id` (`vehicle_id`),
  CONSTRAINT `driver_vehicle_assignments_driver_id_e64334b4_fk_drivers_id` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`id`),
  CONSTRAINT `driver_vehicle_assignments_vehicle_id_0d6b4963_fk_vehicles_id` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `driver_vehicle_assignments`
--

LOCK TABLES `driver_vehicle_assignments` WRITE;
/*!40000 ALTER TABLE `driver_vehicle_assignments` DISABLE KEYS */;
INSERT INTO `driver_vehicle_assignments` VALUES (1,'Musa Demo','Vaisah Peter Zirra','2026-05-05 04:53:02.532117','Driver changed via vehicle edit form',2,1),(2,'Musa Demo','Vaisah Peter Zirra','2026-05-05 13:46:44.914766','Driver changed via vehicle edit form',2,2);
/*!40000 ALTER TABLE `driver_vehicle_assignments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drivers`
--

DROP TABLE IF EXISTS `drivers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drivers` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `full_name` varchar(150) NOT NULL,
  `staff_id` varchar(50) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `license_no` varchar(50) NOT NULL,
  `license_class` varchar(5) NOT NULL,
  `license_expiry` date NOT NULL,
  `status` varchar(20) NOT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `payment_type` varchar(15) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `staff_id` (`staff_id`),
  UNIQUE KEY `license_no` (`license_no`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drivers`
--

LOCK TABLES `drivers` WRITE;
/*!40000 ALTER TABLE `drivers` DISABLE KEYS */;
INSERT INTO `drivers` VALUES (1,'Abba Demo','NEU/ST/00001','08100000000','NA/NUM','A','2026-05-13','active','','2026-04-21 00:15:20.693886','2026-05-11 23:18:16.281860','salaried'),(2,'Musa Demo','NEU/ST/00002','09160025745','NA/NUM2','A','2029-06-06','active','','2026-04-21 00:18:15.249725','2026-04-21 00:18:15.249746','salaried');
/*!40000 ALTER TABLE `drivers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fleet_licence_expiry`
--

DROP TABLE IF EXISTS `fleet_licence_expiry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fleet_licence_expiry` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `expiry_date` date NOT NULL,
  `notes` longtext NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `updated_by` varchar(150) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fleet_licence_expiry`
--

LOCK TABLES `fleet_licence_expiry` WRITE;
/*!40000 ALTER TABLE `fleet_licence_expiry` DISABLE KEYS */;
INSERT INTO `fleet_licence_expiry` VALUES (1,'2026-05-15','','2026-05-14 20:47:00.336555','Vaisah Peter Zirra');
/*!40000 ALTER TABLE `fleet_licence_expiry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_coupons`
--

DROP TABLE IF EXISTS `fuel_coupons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fuel_coupons` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `coupon_id` varchar(25) NOT NULL,
  `verification_code` varchar(10) NOT NULL,
  `litres` decimal(8,2) NOT NULL,
  `cost_per_litre` decimal(8,2) NOT NULL,
  `total_value` decimal(10,2) NOT NULL,
  `status` varchar(15) NOT NULL,
  `issue_datetime` datetime(6) NOT NULL,
  `expiry_date` date DEFAULT NULL,
  `cancellation_reason` longtext NOT NULL,
  `purpose` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `driver_id` bigint DEFAULT NULL,
  `fuel_station_id` bigint NOT NULL,
  `issued_by_id` bigint NOT NULL,
  `vehicle_id` bigint DEFAULT NULL,
  `approved_at` datetime(6) DEFAULT NULL,
  `approved_by_id` bigint DEFAULT NULL,
  `rejection_reason` longtext NOT NULL DEFAULT (_utf8mb4''),
  `requested_litres` decimal(8,2) DEFAULT NULL,
  `self_approved` tinyint(1) NOT NULL,
  `generator_id` bigint DEFAULT NULL,
  `issued_with_override` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `coupon_id` (`coupon_id`),
  UNIQUE KEY `verification_code` (`verification_code`),
  KEY `fuel_coupons_fuel_station_id_9fa28614_fk_vendors_id` (`fuel_station_id`),
  KEY `fuel_coupons_issued_by_id_63d7f5ed_fk_users_id` (`issued_by_id`),
  KEY `fuel_coupons_vehicle_id_4b66d4a5` (`vehicle_id`),
  KEY `fuel_coupons_approved_by_id_323c4096_fk_users_id` (`approved_by_id`),
  KEY `fuel_coupons_driver_id_1a68c026_fk_drivers_id` (`driver_id`),
  KEY `fuel_coupons_generator_id_22d6df99_fk_generators_id` (`generator_id`),
  CONSTRAINT `fuel_coupons_approved_by_id_323c4096_fk_users_id` FOREIGN KEY (`approved_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fuel_coupons_driver_id_1a68c026_fk_drivers_id` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`id`),
  CONSTRAINT `fuel_coupons_fuel_station_id_9fa28614_fk_vendors_id` FOREIGN KEY (`fuel_station_id`) REFERENCES `vendors` (`id`),
  CONSTRAINT `fuel_coupons_generator_id_22d6df99_fk_generators_id` FOREIGN KEY (`generator_id`) REFERENCES `generators` (`id`),
  CONSTRAINT `fuel_coupons_issued_by_id_63d7f5ed_fk_users_id` FOREIGN KEY (`issued_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fuel_coupons_vehicle_id_4b66d4a5_fk_vehicles_id` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`),
  CONSTRAINT `coupon_driver_only_with_vehicle` CHECK (((`vehicle_id` is not null) or (`driver_id` is null))),
  CONSTRAINT `coupon_one_asset_only` CHECK ((((`generator_id` is null) and (`vehicle_id` is not null)) or ((`generator_id` is not null) and (`vehicle_id` is null))))
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_coupons`
--

LOCK TABLES `fuel_coupons` WRITE;
/*!40000 ALTER TABLE `fuel_coupons` DISABLE KEYS */;
INSERT INTO `fuel_coupons` VALUES (43,'NEU/FMS/CP/7B5RG0SB','KXEJ-6UN1',50.00,1000.00,50000.00,'redeemed','2026-05-21 22:30:56.312295',NULL,'','','2026-05-21 22:30:56.312327','2026-05-21 22:40:00.898847',2,1,1,1,'2026-05-21 22:31:24.853141',1,'',NULL,1,NULL,0),(44,'NEU/FMS/CP/WEYZRJU1','QGBT-77R7',10.00,1000.00,10000.00,'redeemed','2026-05-21 22:44:24.797910',NULL,'','','2026-05-21 22:44:24.797942','2026-05-22 02:56:25.046756',NULL,1,1,NULL,'2026-05-21 22:44:29.416387',1,'',NULL,1,1,0),(45,'NEU/FMS/CP/7DHCXBNY','WK4Y-77UV',10.00,1380.00,13800.00,'redeemed','2026-05-22 02:49:53.419935',NULL,'','','2026-05-22 02:49:53.420011','2026-05-22 02:56:13.139853',2,1,1,1,'2026-05-22 02:51:19.769930',1,'',NULL,1,NULL,0),(46,'NEU/FMS/CP/VEH26ZKK','XF0N-HXQA',50.00,1380.00,69000.00,'redeemed','2026-05-22 02:52:10.517937',NULL,'','','2026-05-22 02:52:10.518012','2026-05-22 02:56:57.201543',2,1,1,1,'2026-05-22 02:56:44.408524',1,'',NULL,1,NULL,1),(47,'NEU/FMS/CP/DRBOMLZN','KU1S-U3LR',10.00,1350.00,13500.00,'pending','2026-05-22 03:53:42.165647','2026-05-30','','','2026-05-22 03:53:42.165815','2026-05-22 03:53:42.165854',2,1,1,1,NULL,NULL,'',NULL,0,NULL,0);
/*!40000 ALTER TABLE `fuel_coupons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_logs`
--

DROP TABLE IF EXISTS `fuel_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fuel_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `actual_litres` decimal(8,2) NOT NULL,
  `actual_cost` decimal(10,2) NOT NULL,
  `fuel_date` date NOT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `coupon_id` bigint NOT NULL,
  `driver_id` bigint DEFAULT NULL,
  `fuel_station_id` bigint DEFAULT NULL,
  `logged_by_id` bigint NOT NULL,
  `vehicle_id` bigint DEFAULT NULL,
  `generator_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `coupon_id` (`coupon_id`),
  KEY `fuel_logs_fuel_station_id_c6745812_fk_vendors_id` (`fuel_station_id`),
  KEY `fuel_logs_logged_by_id_c3cb9d2c_fk_users_id` (`logged_by_id`),
  KEY `fuel_logs_vehicle_id_b21b98e7_fk_vehicles_id` (`vehicle_id`),
  KEY `fuel_logs_driver_id_80c27cd5_fk_drivers_id` (`driver_id`),
  KEY `fuel_logs_generator_id_2c15b894_fk_generators_id` (`generator_id`),
  CONSTRAINT `fuel_logs_coupon_id_26670c17_fk_fuel_coupons_id` FOREIGN KEY (`coupon_id`) REFERENCES `fuel_coupons` (`id`),
  CONSTRAINT `fuel_logs_driver_id_80c27cd5_fk_drivers_id` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`id`),
  CONSTRAINT `fuel_logs_fuel_station_id_c6745812_fk_vendors_id` FOREIGN KEY (`fuel_station_id`) REFERENCES `vendors` (`id`),
  CONSTRAINT `fuel_logs_generator_id_2c15b894_fk_generators_id` FOREIGN KEY (`generator_id`) REFERENCES `generators` (`id`),
  CONSTRAINT `fuel_logs_logged_by_id_c3cb9d2c_fk_users_id` FOREIGN KEY (`logged_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fuel_logs_vehicle_id_b21b98e7_fk_vehicles_id` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`),
  CONSTRAINT `fuellog_one_asset_only` CHECK ((((`generator_id` is null) and (`vehicle_id` is not null)) or ((`generator_id` is not null) and (`vehicle_id` is null))))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_logs`
--

LOCK TABLES `fuel_logs` WRITE;
/*!40000 ALTER TABLE `fuel_logs` DISABLE KEYS */;
INSERT INTO `fuel_logs` VALUES (1,50.00,50000.00,'2026-05-22','','2026-05-21 22:40:00.894113',43,2,1,1,1,NULL),(2,10.00,13800.00,'2026-05-22','','2026-05-22 02:56:13.119234',45,2,1,1,1,NULL),(3,10.00,10000.00,'2026-05-22','','2026-05-22 02:56:25.037318',44,NULL,1,1,NULL,1),(4,50.00,69000.00,'2026-05-22','','2026-05-22 02:56:57.188459',46,2,1,1,1,NULL);
/*!40000 ALTER TABLE `fuel_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `generators`
--

DROP TABLE IF EXISTS `generators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `generators` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tag` varchar(30) NOT NULL,
  `name` varchar(150) NOT NULL,
  `make` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  `serial_number` varchar(100) NOT NULL,
  `kva_rating` decimal(8,2) NOT NULL,
  `fuel_type` varchar(10) NOT NULL,
  `tank_capacity_litres` decimal(8,2) DEFAULT NULL,
  `location_note` varchar(200) NOT NULL,
  `status` varchar(20) NOT NULL,
  `installed_date` date DEFAULT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `needs_monthly_fuel` tinyint(1) NOT NULL,
  `building` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tag` (`tag`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `generators`
--

LOCK TABLES `generators` WRITE;
/*!40000 ALTER TABLE `generators` DISABLE KEYS */;
INSERT INTO `generators` VALUES (1,'GEN-FOL','Faculty of Law Generator','Mikano','TF001','',250.00,'petrol',NULL,'','active',NULL,'','2026-05-13 23:24:33.643082','2026-05-15 00:53:38.119388',0,'Hajja Mowa'),(2,'GEN-FSC','Faculty of Science and Computing GEN','Mikano','TF002','',250.00,'petrol',250.00,'','active',NULL,'','2026-05-14 20:13:52.672982','2026-05-15 00:53:58.754431',0,'Jauro Gombe Complex');
/*!40000 ALTER TABLE `generators` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maintenance_items`
--

DROP TABLE IF EXISTS `maintenance_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `maintenance_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `service_type` varchar(20) NOT NULL,
  `description` varchar(255) NOT NULL,
  `cost` decimal(12,2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `record_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `maintenance_items_record_id_3c5428bc_fk_maintenance_records_id` (`record_id`),
  CONSTRAINT `maintenance_items_record_id_3c5428bc_fk_maintenance_records_id` FOREIGN KEY (`record_id`) REFERENCES `maintenance_records` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maintenance_items`
--

LOCK TABLES `maintenance_items` WRITE;
/*!40000 ALTER TABLE `maintenance_items` DISABLE KEYS */;
INSERT INTO `maintenance_items` VALUES (1,'routine','Brake Part',50000.00,'2026-05-13 10:40:54.838689',3),(2,'other','- Replacemnet of Oil Filter\r\n- Brake Pad',20000.00,'2026-05-13 10:40:54.841319',4),(3,'other','Front Brake Pad',50000.00,'2026-05-13 10:40:54.843584',2),(4,'routine','Brake Pads',30000.00,'2026-05-13 10:40:54.846750',1),(5,'routine','Brake Part (2 x 500)',1000.00,'2026-05-13 11:13:52.435048',5),(6,'oil','Total Engine Oil',6400.00,'2026-05-13 11:13:52.446954',5),(7,'general_service','Host',2000.00,'2026-05-15 01:10:21.984187',6),(8,'routine','Host',2000.00,'2026-05-15 01:34:32.693324',7),(9,'oil','Changed engine oil',5600.00,'2026-05-15 01:34:32.699413',7),(10,'brakes','1 Brake Calipers',30000.00,'2026-05-22 03:56:10.438317',8),(11,'general_service','Total Engine Oil',50000.00,'2026-05-22 03:56:10.447287',8),(12,'engine','Radiator',1000.00,'2026-05-22 03:56:10.455917',8);
/*!40000 ALTER TABLE `maintenance_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maintenance_records`
--

DROP TABLE IF EXISTS `maintenance_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `maintenance_records` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `service_date` date NOT NULL,
  `service_type` varchar(20) NOT NULL,
  `description` longtext NOT NULL,
  `vendor_other` varchar(150) NOT NULL,
  `total_cost` decimal(12,2) NOT NULL,
  `next_service_date` date DEFAULT NULL,
  `approved_by` varchar(150) NOT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` bigint NOT NULL,
  `vehicle_id` bigint DEFAULT NULL,
  `vendor_id` bigint DEFAULT NULL,
  `generator_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `maintenance_records_created_by_id_700f450c_fk_users_id` (`created_by_id`),
  KEY `maintenance_records_vendor_id_375a6187_fk_vendors_id` (`vendor_id`),
  KEY `maintenance_records_vehicle_id_d45cef91_fk_vehicles_id` (`vehicle_id`),
  KEY `maintenance_records_generator_id_0319289c_fk_generators_id` (`generator_id`),
  CONSTRAINT `maintenance_records_created_by_id_700f450c_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `maintenance_records_generator_id_0319289c_fk_generators_id` FOREIGN KEY (`generator_id`) REFERENCES `generators` (`id`),
  CONSTRAINT `maintenance_records_vehicle_id_d45cef91_fk_vehicles_id` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`),
  CONSTRAINT `maintenance_records_vendor_id_375a6187_fk_vendors_id` FOREIGN KEY (`vendor_id`) REFERENCES `vendors` (`id`),
  CONSTRAINT `maintenance_one_asset_only` CHECK ((((`generator_id` is null) and (`vehicle_id` is not null)) or ((`generator_id` is not null) and (`vehicle_id` is null))))
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maintenance_records`
--

LOCK TABLES `maintenance_records` WRITE;
/*!40000 ALTER TABLE `maintenance_records` DISABLE KEYS */;
INSERT INTO `maintenance_records` VALUES (1,'2026-04-22','routine','Brake Pads','AB Repairs',30000.00,'2026-04-22','Vice Chancellor','','2026-04-22 21:15:28.858924','2026-04-22 21:15:28.858994',1,1,NULL,NULL),(2,'2026-04-28','other','Front Brake Pad','Trswiler Park',50000.00,NULL,'DVC','','2026-04-27 15:47:17.482536','2026-04-27 15:47:17.482586',1,1,NULL,NULL),(3,'2026-05-03','routine','Brake Part','',50000.00,'2026-08-07','DVC','','2026-05-02 00:24:26.883369','2026-05-02 00:24:26.883452',1,1,4,NULL),(4,'2026-05-02','other','- Replacemnet of Oil Filter\r\n- Brake Pad','',20000.00,NULL,'Vice Chancellor','','2026-05-02 21:31:33.972324','2026-05-02 21:31:33.972358',1,1,4,NULL),(5,'2026-05-13','routine','','',7400.00,NULL,'DVC','','2026-05-13 11:13:52.429647','2026-05-13 11:13:52.454548',1,1,4,NULL),(6,'2026-05-15','general_service','','',2000.00,NULL,'DVC','','2026-05-15 01:10:21.982084','2026-05-15 01:10:21.992000',1,NULL,4,1),(7,'2026-05-15','routine','','',7600.00,NULL,'Vice Chancellor','','2026-05-15 01:34:32.692310','2026-05-15 01:34:32.702144',1,NULL,4,1),(8,'2026-05-22','brakes','','',81000.00,NULL,'DVC','','2026-05-22 03:56:10.425003','2026-05-22 03:56:10.462679',1,1,4,NULL);
/*!40000 ALTER TABLE `maintenance_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `monthly_fuel_dismissals`
--

DROP TABLE IF EXISTS `monthly_fuel_dismissals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `monthly_fuel_dismissals` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `month` smallint unsigned NOT NULL,
  `year` smallint unsigned NOT NULL,
  `dismissed_by` varchar(150) NOT NULL,
  `dismissed_at` datetime(6) NOT NULL,
  `vehicle_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `monthly_fuel_dismissals_vehicle_id_month_year_e675a986_uniq` (`vehicle_id`,`month`,`year`),
  CONSTRAINT `monthly_fuel_dismissals_vehicle_id_814d0dab_fk_vehicles_id` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`),
  CONSTRAINT `monthly_fuel_dismissals_chk_1` CHECK ((`month` >= 0)),
  CONSTRAINT `monthly_fuel_dismissals_chk_2` CHECK ((`year` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `monthly_fuel_dismissals`
--

LOCK TABLES `monthly_fuel_dismissals` WRITE;
/*!40000 ALTER TABLE `monthly_fuel_dismissals` DISABLE KEYS */;
INSERT INTO `monthly_fuel_dismissals` VALUES (1,5,2026,'Vaisah Peter Zirra','2026-05-03 03:33:02.373004',2),(2,5,2026,'Vaisah Peter Zirra','2026-05-04 00:44:42.175244',1),(3,5,2026,'Vaisah Peter Zirra','2026-05-13 12:03:07.674493',3);
/*!40000 ALTER TABLE `monthly_fuel_dismissals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `password_reset_otps`
--

DROP TABLE IF EXISTS `password_reset_otps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `password_reset_otps` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `otp` varchar(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `used` tinyint(1) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `password_reset_otps_user_id_a73ed8e7_fk_users_id` (`user_id`),
  CONSTRAINT `password_reset_otps_user_id_a73ed8e7_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `password_reset_otps`
--

LOCK TABLES `password_reset_otps` WRITE;
/*!40000 ALTER TABLE `password_reset_otps` DISABLE KEYS */;
INSERT INTO `password_reset_otps` VALUES (1,'827194','2026-05-02 20:51:55.338911',0,1),(2,'205239','2026-05-02 23:09:46.978991',0,1),(3,'666409','2026-05-02 23:12:53.258204',1,1),(4,'165786','2026-05-02 23:14:57.531919',0,1),(5,'730222','2026-05-04 09:52:23.729979',0,1),(6,'903949','2026-05-04 10:01:07.428790',0,1),(7,'894220','2026-05-04 10:08:06.518529',0,1),(8,'437703','2026-05-05 11:51:39.775771',1,3),(9,'537455','2026-05-05 13:49:39.188015',0,4),(10,'622448','2026-05-19 18:10:31.576497',0,5);
/*!40000 ALTER TABLE `password_reset_otps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `report_schedules`
--

DROP TABLE IF EXISTS `report_schedules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `report_schedules` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `report_type` varchar(40) NOT NULL,
  `format` varchar(10) NOT NULL,
  `recipients` longtext NOT NULL,
  `send_day` smallint unsigned NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_by` varchar(150) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `last_sent` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `report_schedules_chk_1` CHECK ((`send_day` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_schedules`
--

LOCK TABLES `report_schedules` WRITE;
/*!40000 ALTER TABLE `report_schedules` DISABLE KEYS */;
INSERT INTO `report_schedules` VALUES (1,'Monthly Fleet Summary','monthly_expense','pdf','vaisahzirra7@gmail.com, vaisah.zirra@student.neu.edu.ng',1,1,'Vaisah Peter Zirra','2026-05-05 05:05:11.090642','2026-05-20 01:09:21.412181'),(2,'Per-vehivle spending','vehicle_spending','pdf','vaisahzirra7@gmail.com, vaisah.zirra@student.neu.edu.ng',1,1,'Vaisah Peter Zirra','2026-05-09 16:22:37.290769','2026-05-12 00:12:02.898246'),(3,'Maintanance History','maintenance','pdf','vaisahzirra7@gmail.com, vaisah.zirra@student.neu.edu.ng',1,1,'Vaisah Peter Zirra','2026-05-09 16:23:28.133511','2026-05-22 03:54:07.998314'),(4,'Per-GENERATORspending','generator_spending','pdf','vaisahzirra7@gmail.ccm',1,1,'Vaisah Peter Zirra','2026-05-18 04:15:38.606030','2026-05-20 01:09:05.436053');
/*!40000 ALTER TABLE `report_schedules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_module_permissions`
--

DROP TABLE IF EXISTS `role_module_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_module_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `module` varchar(50) NOT NULL,
  `can_read` tinyint(1) NOT NULL,
  `can_write` tinyint(1) NOT NULL,
  `can_edit` tinyint(1) NOT NULL,
  `can_delete` tinyint(1) NOT NULL,
  `role_id` bigint NOT NULL,
  `can_approve` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_module_permissions_role_id_module_4b93cd33_uniq` (`role_id`,`module`),
  CONSTRAINT `role_module_permissions_role_id_e21c5f97_fk_roles_id` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_module_permissions`
--

LOCK TABLES `role_module_permissions` WRITE;
/*!40000 ALTER TABLE `role_module_permissions` DISABLE KEYS */;
INSERT INTO `role_module_permissions` VALUES (32,'vehicles',1,1,1,1,2,0),(33,'coupons',1,1,1,1,2,0),(34,'maintenance',1,1,0,0,2,0),(35,'reports',1,0,0,0,2,0),(36,'dashboard',1,0,0,0,2,0),(37,'coupons',1,1,1,1,1,0),(38,'fuel_logs',1,1,0,0,1,0),(39,'dashboard',1,0,0,0,1,0);
/*!40000 ALTER TABLE `role_module_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `is_system_role` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Quality Assurance','A Quality Assurance (QA) ensures vehicles, maintenance, and operations meet safety and performance standards, reducing risks and costs. They proactively audit maintenance, verify vehicle compliance, monitor driver behavior, and ensure third-party contractors adhere to specifications.',0,'2026-05-01 23:45:15.401304'),(2,'Transport Officer','',0,'2026-05-02 21:40:28.193547');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `station_deposits`
--

DROP TABLE IF EXISTS `station_deposits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `station_deposits` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `amount` decimal(14,2) NOT NULL,
  `deposit_date` date NOT NULL,
  `reference_number` varchar(80) NOT NULL,
  `note` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` bigint NOT NULL,
  `vendor_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `station_deposits_created_by_id_95dd815b_fk_users_id` (`created_by_id`),
  KEY `station_dep_vendor__94be3a_idx` (`vendor_id`,`deposit_date` DESC),
  CONSTRAINT `station_deposits_created_by_id_95dd815b_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `station_deposits_vendor_id_e547737d_fk_vendors_id` FOREIGN KEY (`vendor_id`) REFERENCES `vendors` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `station_deposits`
--

LOCK TABLES `station_deposits` WRITE;
/*!40000 ALTER TABLE `station_deposits` DISABLE KEYS */;
INSERT INTO `station_deposits` VALUES (1,100000.00,'2026-05-21','test001refbank','','2026-05-21 22:30:22.741155',1,1),(4,250000.00,'2026-05-01','test002refbank','','2026-05-22 02:58:02.831799',1,1);
/*!40000 ALTER TABLE `station_deposits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_settings`
--

DROP TABLE IF EXISTS `system_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_settings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `system_name` varchar(120) NOT NULL,
  `institution_name` varchar(160) NOT NULL,
  `institution_subtitle` varchar(200) NOT NULL,
  `logo` varchar(100) DEFAULT NULL,
  `favicon` varchar(100) DEFAULT NULL,
  `email_from` varchar(200) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `updated_by_id` bigint DEFAULT NULL,
  `smtp_host` varchar(200) NOT NULL,
  `smtp_port` int unsigned DEFAULT NULL,
  `smtp_user` varchar(200) NOT NULL,
  `smtp_password_encrypted` longtext NOT NULL DEFAULT (_utf8mb4''),
  `smtp_use_tls` tinyint(1) NOT NULL,
  `smtp_use_ssl` tinyint(1) NOT NULL,
  `low_balance_threshold` decimal(14,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `system_settings_updated_by_id_cf1dfbba_fk_users_id` (`updated_by_id`),
  CONSTRAINT `system_settings_updated_by_id_cf1dfbba_fk_users_id` FOREIGN KEY (`updated_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `system_settings_chk_1` CHECK ((`smtp_port` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_settings`
--

LOCK TABLES `system_settings` WRITE;
/*!40000 ALTER TABLE `system_settings` DISABLE KEYS */;
INSERT INTO `system_settings` VALUES (1,'VanaraFleetsOps','VanaraFleetsOps','North-Eastern University, Gombe  ·  FMS','','branding/favicon.png','vaisah.zirra@whoisvaisah.name.ng','2026-05-21 12:20:01.566736',1,'smtp.zoho.com',587,'vaisah.zirra@whoisvaisah.name.ng','gAAAAABqDvhxYDd2NjCiOf0noRFaplouHoeNMA7fdIKaXd7EpfWMnoJ4ZtKUyEAPrAXkx5eHcLmRLVWCmg6ZRRFb-KU2Ax5nrw==',1,0,0.00);
/*!40000 ALTER TABLE `system_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trips`
--

DROP TABLE IF EXISTS `trips`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trips` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `from_other` varchar(150) NOT NULL,
  `to_other` varchar(150) NOT NULL,
  `trip_date` date NOT NULL,
  `amount_paid` decimal(12,2) NOT NULL,
  `purpose` varchar(255) NOT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `driver_id` bigint NOT NULL,
  `from_destination_id` bigint DEFAULT NULL,
  `logged_by_id` bigint NOT NULL,
  `to_destination_id` bigint DEFAULT NULL,
  `vehicle_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `trips_driver_id_31c8eeda_fk_drivers_id` (`driver_id`),
  KEY `trips_from_destination_id_ff895ffa_fk_destinations_id` (`from_destination_id`),
  KEY `trips_logged_by_id_1946eac8_fk_users_id` (`logged_by_id`),
  KEY `trips_to_destination_id_fd251ea3_fk_destinations_id` (`to_destination_id`),
  KEY `trips_vehicle_id_00865df5_fk_vehicles_id` (`vehicle_id`),
  CONSTRAINT `trips_driver_id_31c8eeda_fk_drivers_id` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`id`),
  CONSTRAINT `trips_from_destination_id_ff895ffa_fk_destinations_id` FOREIGN KEY (`from_destination_id`) REFERENCES `destinations` (`id`),
  CONSTRAINT `trips_logged_by_id_1946eac8_fk_users_id` FOREIGN KEY (`logged_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `trips_to_destination_id_fd251ea3_fk_destinations_id` FOREIGN KEY (`to_destination_id`) REFERENCES `destinations` (`id`),
  CONSTRAINT `trips_vehicle_id_00865df5_fk_vehicles_id` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trips`
--

LOCK TABLES `trips` WRITE;
/*!40000 ALTER TABLE `trips` DISABLE KEYS */;
INSERT INTO `trips` VALUES (1,'','','2026-05-13',49999.99,'','','2026-05-13 17:09:14.670419','2026-05-13 17:09:14.670432',1,1,1,2,3);
/*!40000 ALTER TABLE `trips` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trips_fuel_coupons`
--

DROP TABLE IF EXISTS `trips_fuel_coupons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trips_fuel_coupons` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `trip_id` bigint NOT NULL,
  `fuelcoupon_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `trips_fuel_coupons_trip_id_fuelcoupon_id_711aceb0_uniq` (`trip_id`,`fuelcoupon_id`),
  KEY `trips_fuel_coupons_fuelcoupon_id_67714628_fk_fuel_coupons_id` (`fuelcoupon_id`),
  CONSTRAINT `trips_fuel_coupons_fuelcoupon_id_67714628_fk_fuel_coupons_id` FOREIGN KEY (`fuelcoupon_id`) REFERENCES `fuel_coupons` (`id`),
  CONSTRAINT `trips_fuel_coupons_trip_id_8723369a_fk_trips_id` FOREIGN KEY (`trip_id`) REFERENCES `trips` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trips_fuel_coupons`
--

LOCK TABLES `trips_fuel_coupons` WRITE;
/*!40000 ALTER TABLE `trips_fuel_coupons` DISABLE KEYS */;
/*!40000 ALTER TABLE `trips_fuel_coupons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_invites`
--

DROP TABLE IF EXISTS `user_invites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_invites` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `token` varchar(64) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `used` tinyint(1) NOT NULL,
  `used_at` datetime(6) DEFAULT NULL,
  `created_by_id` bigint DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `user_invites_created_by_id_9b55c1be_fk_users_id` (`created_by_id`),
  KEY `user_invites_user_id_b920b75c_fk_users_id` (`user_id`),
  CONSTRAINT `user_invites_created_by_id_9b55c1be_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `user_invites_user_id_b920b75c_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_invites`
--

LOCK TABLES `user_invites` WRITE;
/*!40000 ALTER TABLE `user_invites` DISABLE KEYS */;
INSERT INTO `user_invites` VALUES (1,'w2zY71Cui0D-4wUHY_ZpNIwJa8DjwPtO_-xotiHfiHQ9Nir0M0pYf50nqkDu47Iw','2026-05-19 18:03:32.254224',0,NULL,1,4),(2,'5mXKoeCFUqRNIcCQhcga_m8QovC0qroAAdbzpm5EwwLw2n8KhDnhyPELH9E1gP0w','2026-05-19 18:04:08.652229',1,NULL,1,5),(3,'u36Hr-Zn01iIfoXtS0QWfloOaqDSvGeI20BWYwSSPMLwNMM_zs23S8wZSDfA6pm9','2026-05-19 18:06:40.789320',1,NULL,1,5),(4,'8vKaNtl5CPdqDFFX4xjbvRGBErLeunPrFGUuCb-xiE6SzvcKPsKqtamrOaLwydhw','2026-05-19 18:09:31.147339',1,NULL,1,5),(5,'pBaNfgu5GmpSk8XIuBZQ6oHxVGah19-KYqOdRou5k_ftSCwYCOeTVPM9A-2sx6PB','2026-05-19 18:10:01.542725',1,NULL,1,5),(6,'dWBBdaDkJ3DoRUOgyi9UtyRLUzuBrv8jVgi0kpK2OY9Q7epv8ehB_YQC53gEi7eK','2026-05-20 00:20:18.131998',1,NULL,1,5),(7,'_MANv6QQr2nKL0dwSCFm-UHG6_0RVZQx4tsH1lI1MBBrnaz3db04UWmNA5EaohDn','2026-05-20 01:04:51.711666',1,NULL,1,5),(8,'JqAi-HbU8Ks-5MVtFpMleKqy4RvsqmIwUJjRAow2Y_lq0wGTEAxHhs8Ti_FGTsFc','2026-05-20 01:20:34.220314',1,NULL,1,5),(9,'L5calwceA_7tRkHgjCEhozaO7rocvyTmlI5IoYFjl05aR8puUJ42jALabmpbquZk','2026-05-20 01:25:18.683781',1,NULL,1,5),(10,'xYrfNIQjJcphw7T3MYAgjozNs-ZBQgNPo7Z3-FwjdeFUaMq5dyATstIz3S8ya7KN','2026-05-20 01:25:36.614951',1,NULL,1,5),(11,'J4esoWExLjohsXWzrUIFWDWSnbv6bB4PftPkFMpKVM_JoeJEeAtkD0R_mG3fZsJp','2026-05-20 01:31:06.395306',0,NULL,1,5);
/*!40000 ALTER TABLE `user_invites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `email` varchar(254) NOT NULL,
  `full_name` varchar(150) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_system_admin` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  `department_id` bigint DEFAULT NULL,
  `role_id` bigint DEFAULT NULL,
  `must_change_password` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `users_created_by_id_19a92469_fk_users_id` (`created_by_id`),
  KEY `users_department_id_f0b302db_fk_departments_id` (`department_id`),
  KEY `users_role_id_1900a745_fk_roles_id` (`role_id`),
  CONSTRAINT `users_created_by_id_19a92469_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `users_department_id_f0b302db_fk_departments_id` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`),
  CONSTRAINT `users_role_id_1900a745_fk_roles_id` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'pbkdf2_sha256$600000$KR4zu1WI5X9yYOGIL9phGV$fj0nNZJlkse7cdWJjCbHbi51ynFf0PgnIcI6gdtfz4w=','2026-05-24 01:26:11.379942',1,'vaisahzirra7@gmail.com','Vaisah Peter Zirra',1,1,1,'2026-04-19 01:43:28.290617',NULL,NULL,NULL,0),(2,'pbkdf2_sha256$600000$piIPiK7qYz88pRRkukJnVQ$Y+F6lS22zGObXjIl48p4G7Inj40stGAOTbPBqW+FzMI=','2026-05-02 21:41:18.539925',0,'test@neu.edu.ng','Test User 1',1,0,0,'2026-05-01 23:46:44.907905',1,NULL,2,0),(3,'pbkdf2_sha256$600000$awEsBsN0Fd8uuks0cleJMN$kiBKFInUZmkbMRGCYz+nS+me6RTWxID80qd3VF9ctNM=','2026-05-07 19:25:43.659647',0,'muhammad.abdullahi@student.neu.edu.ng','Muhammad Bala Abdullahi',1,0,0,'2026-05-05 11:47:35.965024',1,1,1,0),(4,'!96cNzuBlLoeAs1FEztQa5T76wJIiX3XJrQBCq7fK','2026-05-05 13:49:14.513754',0,'abubakarsadiqibrahim4321@gmail.com','Abubakar Sadiq Ibrahim',1,0,0,'2026-05-05 13:48:53.236064',1,2,1,0),(5,'!8ABEaZEwElQsNgfpgMU1O15K3CTUoOeIxwZuqLNg','2026-05-11 23:54:38.421885',0,'vaisah.zirra@student.neu.edu.ng','Zirra Vaisah Peter',1,0,0,'2026-05-11 23:50:37.508264',1,1,2,0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_groups`
--

DROP TABLE IF EXISTS `users_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_groups_user_id_group_id_fc7788e8_uniq` (`user_id`,`group_id`),
  KEY `users_groups_group_id_2f3517aa_fk_auth_group_id` (`group_id`),
  CONSTRAINT `users_groups_group_id_2f3517aa_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `users_groups_user_id_f500bee5_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_groups`
--

LOCK TABLES `users_groups` WRITE;
/*!40000 ALTER TABLE `users_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_user_permissions`
--

DROP TABLE IF EXISTS `users_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_permissions_user_id_permission_id_3b86cbdf_uniq` (`user_id`,`permission_id`),
  KEY `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` (`permission_id`),
  CONSTRAINT `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `users_user_permissions_user_id_92473840_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_user_permissions`
--

LOCK TABLES `users_user_permissions` WRITE;
/*!40000 ALTER TABLE `users_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vehicles`
--

DROP TABLE IF EXISTS `vehicles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vehicles` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `plate_number` varchar(20) NOT NULL,
  `vehicle_type` varchar(20) NOT NULL,
  `make` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  `year` smallint unsigned NOT NULL,
  `colour` varchar(50) NOT NULL,
  `engine_no` varchar(100) NOT NULL,
  `chassis_no` varchar(100) NOT NULL,
  `fuel_type` varchar(10) NOT NULL,
  `status` varchar(20) NOT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `default_driver_id` bigint DEFAULT NULL,
  `department_id` bigint NOT NULL,
  `needs_monthly_fuel` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `plate_number` (`plate_number`),
  KEY `vehicles_default_driver_id_966daa6a_fk_drivers_id` (`default_driver_id`),
  KEY `vehicles_department_id_42cfd838_fk_departments_id` (`department_id`),
  CONSTRAINT `vehicles_default_driver_id_966daa6a_fk_drivers_id` FOREIGN KEY (`default_driver_id`) REFERENCES `drivers` (`id`),
  CONSTRAINT `vehicles_department_id_42cfd838_fk_departments_id` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`),
  CONSTRAINT `vehicles_chk_1` CHECK ((`year` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vehicles`
--

LOCK TABLES `vehicles` WRITE;
/*!40000 ALTER TABLE `vehicles` DISABLE KEYS */;
INSERT INTO `vehicles` VALUES (1,'GMB-217-AA','car','Toyota','Hilux',2013,'Custom','','00000000000001','petrol','active','','2026-04-21 00:06:38.538685','2026-05-22 03:56:22.737822',2,3,1),(2,'GMB-310-AA','car','Peugeot','406',2010,'Silver','','00000000000002','petrol','active','','2026-04-21 00:12:59.286121','2026-05-05 13:46:44.908969',2,2,1),(3,'GMB-358-AA','car','Peugeot','307',2008,'Black','00000000000003','00000000000003','petrol','active','','2026-05-04 00:49:25.218121','2026-05-04 00:51:30.660997',1,1,1);
/*!40000 ALTER TABLE `vehicles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vendors`
--

DROP TABLE IF EXISTS `vendors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vendors` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `type` varchar(20) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `address` longtext NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vendors`
--

LOCK TABLES `vendors` WRITE;
/*!40000 ALTER TABLE `vendors` DISABLE KEYS */;
INSERT INTO `vendors` VALUES (1,'NNPC Mega Station','fuel_station','','Gombe State',1,'2026-04-21 00:16:42.748688','2026-04-21 12:54:07.907855'),(4,'Total Energies Repair','mechanic','','',1,'2026-05-02 00:21:53.603213','2026-05-02 00:21:53.603250');
/*!40000 ALTER TABLE `vendors` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-24  3:49:29
