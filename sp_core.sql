-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: sp_core
-- ------------------------------------------------------
-- Server version	8.0.46

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
-- Table structure for table `fcm_tokens`
--

DROP TABLE IF EXISTS `fcm_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fcm_tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `token` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `ix_fcm_tokens_id` (`id`),
  KEY `fcm_tokens_ibfk_1` (`user_id`),
  CONSTRAINT `fcm_tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fcm_tokens`
--

LOCK TABLES `fcm_tokens` WRITE;
/*!40000 ALTER TABLE `fcm_tokens` DISABLE KEYS */;
INSERT INTO `fcm_tokens` VALUES (4,1,'cIT7s0LtDgI9x6S4EVpdEp:APA91bEHBT7-1InIdCxPJqkQwiL-99GQ9Y_b6mrder3AyWdcib360HnmMd4BSsbJ6REWFIkBbvB-qKSzwg3MdBM7BwUvZa06ZoUTTcMYi_qlY0J1wXx3XDA','2026-05-03 20:47:56'),(6,3,'cJEwPHyvkDsPuUSn_TPX75:APA91bF3DOWcKAsKZtbp3H4Q4oQYCRBrTvt1dvnSE8pT5PYyt0cRcd-SxgpaM2lUoovi1cmGKLsNHULa36Q9jAe07SJc6FmBcAQb9vDeHwTxVe5eUKNTgNE','2026-05-03 21:06:47'),(7,3,'cJEwPHyvkDsPuUSn_TPX75:APA91bHiv_2SKv2GoLPYd1CthBwCQEEep7txWNmaNa8ZNFug6cL8TPhgbzKs44YgmAZ0f8ixWpZBYxMueaWnPrscMqFzwAXujZBeB7GaWkeR6RfQIAbtDhM','2026-05-03 21:06:47'),(9,3,'cJEwPHyvkDsPuUSn_TPX75:APA91bHvEIu9heNG_POnTlrMM8KgWHatjAJ2_vYiBk_5cuOKfYUcWfY7iOxfOPn-uMDvEY0iVbMUFJJ5MOGYxbzWEUj5menBwiCP8knHem0xnID3gGtGm8M','2026-05-03 21:06:47'),(10,6,'da4vyEWsAgsI1EtWcufsJN:APA91bHDJKEow62sjkDENbUnVpdHWEh--xKPoADka-gsG1t21GjhgA8PhN6TYHMMy8ShzM6blVLxp_QcpA0a8usa3QawryUQRTkH98lWLyaURHtCoByr7kc','2026-05-03 23:02:17'),(11,6,'da4vyEWsAgsI1EtWcufsJN:APA91bG7uRkoPTHPJIEUpnXGOkfoElPxtlwExwKpmyq-TTsTdLpFdFTN8PlavDIuK02qbdHeh0oaI01OjDPKNfD8sAFeN9CDoo2xzjRcNUmZbecl9OxJdjg','2026-05-03 23:02:17'),(12,6,'da4vyEWsAgsI1EtWcufsJN:APA91bGX1IV9KIWlsC5LznIYHe1gu5BAMeKS0rD061liGv74cVUCwtPIxcw48_JukWDLIPTrzZgnaP-UHlGclfUm66_URPGRIsSaLO0MwFE2mArGTAVk6CY','2026-05-03 23:02:18'),(13,6,'da4vyEWsAgsI1EtWcufsJN:APA91bELy0DbFZfpxfk3SL9CsIHw7jiiWsCUdjsomUE0nwRra42iIBptqk0x_8AILnpLNrk-wZgdT8ddrJjtP8PM1PgFu6pH5MM7MzU3oQ70LJ5zB87d7kQ','2026-05-03 23:04:33'),(15,6,'da4vyEWsAgsI1EtWcufsJN:APA91bE-0GKnOugITLOMqrwSDyOeV54bkPjkQDl_5AUXMY7AAan5IauwzIR_H69FlHmy_6pTrh8RgIFWeRtXgzvmYaglJlOIttSl-ypLUiXZcpLXRS0NFf8','2026-05-03 23:09:41');
/*!40000 ALTER TABLE `fcm_tokens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `incidents`
--

DROP TABLE IF EXISTS `incidents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `incidents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `lat` float NOT NULL,
  `lng` float NOT NULL,
  `location_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `image_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_id` int NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'reported',
  PRIMARY KEY (`id`),
  KEY `ix_incidents_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `incidents`
--

LOCK TABLES `incidents` WRITE;
/*!40000 ALTER TABLE `incidents` DISABLE KEYS */;
INSERT INTO `incidents` VALUES (1,'accident','dadad',14.0688,121.324,'Sha-Sam Electronics and General Merchandise, A. Bonifacio Street, VII-B, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,1,'2026-05-03 18:06:53','reported'),(2,'crime',' baril',14.0714,121.302,'SM City San Pablo, Maharlika Highway, San Rafael, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,1,'2026-05-03 18:10:35','reported'),(3,'hazard','aha',14.0737,121.317,'Sambat, Lieutenant Cosico Avenue, Platoon Subdivision, VI-E, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,1,'2026-05-03 18:11:38','reported'),(4,'accident','blah',14.1099,121.299,'San Mateo Chapel, Calauan - San Pablo Road, San Mateo, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,1,'2026-05-03 18:28:43','completed'),(5,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:15','reported'),(6,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:20','reported'),(7,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:21','reported'),(8,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:22','reported'),(9,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:27','reported'),(10,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:28','reported'),(11,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:28','reported'),(12,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:28','reported'),(13,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:28','reported'),(14,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:28','reported'),(15,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:28','reported'),(16,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:29','reported'),(17,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:29','reported'),(18,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:29','reported'),(19,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:30','reported'),(20,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:30','reported'),(21,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:30','reported'),(22,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:30','reported'),(23,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:30','reported'),(24,'crime','dadsad',14.0688,121.321,'San Pablo, P. Alcantara Street, VII-A, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:11:31','reported'),(25,'accident','ddsadad',14.0661,121.322,'Franklin Baker Company of the Philippines, II-C, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:12:49','reported'),(26,'accident','ddsadad',14.0661,121.322,'Franklin Baker Company of the Philippines, II-C, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:12:51','reported'),(27,'accident','ddsadad',14.0661,121.322,'Franklin Baker Company of the Philippines, II-C, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:21:45','reported'),(28,'accident','ddsadad',14.0661,121.322,'Franklin Baker Company of the Philippines, II-C, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:21:46','reported'),(29,'accident','ddsadad',14.0661,121.322,'Franklin Baker Company of the Philippines, II-C, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:21:47','reported'),(30,'accident','ddsadad',14.0661,121.322,'Franklin Baker Company of the Philippines, II-C, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:21:47','reported'),(31,'accident','dsdad',14.0829,121.313,'Laguna State Polytechnic University-San Pablo City Campus, Lieutenant Cosico Avenue, Doña Eusebia Subdivision, Del Remedio, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:25:12','completed'),(32,'accident','dsddad',14.0782,121.33,'Sampaloc Lake, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,4,'2026-05-03 22:38:35','completed'),(33,'crime','sdada',14.1099,121.299,'San Mateo Chapel, Calauan - San Pablo Road, San Mateo, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,5,'2026-05-03 22:42:40','completed'),(34,'crime','sdad',14.0661,121.322,'Franklin Baker Company of the Philippines, II-C, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,6,'2026-05-03 23:04:00','completed'),(35,'accident','dsad',14.0829,121.313,'Laguna State Polytechnic University-San Pablo City Campus, Lieutenant Cosico Avenue, Doña Eusebia Subdivision, Del Remedio, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,6,'2026-05-03 23:10:29','completed'),(36,'crime','dsadadad',14.0937,121.304,'Calauan - San Pablo Road, Santa Maria Magdalena, San Pablo, Laguna, Calabarzon, 4000, Philippines',NULL,6,'2026-05-03 23:13:14','completed');
/*!40000 ALTER TABLE `incidents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `push_subscriptions`
--

DROP TABLE IF EXISTS `push_subscriptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `push_subscriptions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `endpoint` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `p256dh` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `auth` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `ix_push_subscriptions_id` (`id`),
  CONSTRAINT `push_subscriptions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `push_subscriptions`
--

LOCK TABLES `push_subscriptions` WRITE;
/*!40000 ALTER TABLE `push_subscriptions` DISABLE KEYS */;
/*!40000 ALTER TABLE `push_subscriptions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sos_alerts`
--

DROP TABLE IF EXISTS `sos_alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sos_alerts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `lat` float NOT NULL,
  `lng` float NOT NULL,
  `user_id` int NOT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `ix_sos_alerts_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sos_alerts`
--

LOCK TABLES `sos_alerts` WRITE;
/*!40000 ALTER TABLE `sos_alerts` DISABLE KEYS */;
/*!40000 ALTER TABLE `sos_alerts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `hashed_password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_admin` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'sjanna382@gmail.com','$pbkdf2-sha256$29000$YCzl/D9nTAnBWMsZA.Cc8w$GIA3NtQ3G0toGI4bMQ3uwqrOjriyKIENTrFjbdFfO50','Janna Santos',0,'2026-05-03 17:53:39'),(3,'admin@saferoute.sp','$pbkdf2-sha256$29000$IaTUWsv5n/P./39PiRGCEA$AcXSIl0LBDYLfXg4nkX0Ge07scGorJdcvHXVSXta27E','System Administrator',1,'2026-05-03 20:46:41'),(4,'jannasantos@gmail.com','$pbkdf2-sha256$29000$zVmL0bo3hvBeq7XWGqMUQg$gNdu2Ooxx8pXRb98fbouwuPJw9Epa.YDRZRjyFDrKKs','Jabbey',0,'2026-05-03 21:55:14'),(5,'ella@gmail.com','$pbkdf2-sha256$29000$UyrlfI/RmvM.B2AM4TxH6A$H0IatgCjhjVcqKrycXt7LIzRUSQeNsDsBj0MB0tasVo','Ella Mae',0,'2026-05-03 22:31:30'),(6,'jaka@gmail.com','$pbkdf2-sha256$29000$KWXMeW9t7f3f21trLWUs5Q$mL99foU2FZ4p4v7/x0lV/WInB02Lb0TLnhllkdgKt2s','Jaka Santos',0,'2026-05-03 22:51:51');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-08 17:21:52
