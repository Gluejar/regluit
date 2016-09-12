-- MySQL dump 10.13  Distrib 5.7.11, for osx10.9 (x86_64)
--
-- Host: 127.0.0.1    Database: unglueit
-- ------------------------------------------------------
-- Server version	5.7.11

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
-- Table structure for table `api_allowedrepo`
--

DROP TABLE IF EXISTS `api_allowedrepo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `api_allowedrepo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `org` varchar(39) NOT NULL,
  `repo_name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `api_allowedrepo`
--

LOCK TABLES `api_allowedrepo` WRITE;
/*!40000 ALTER TABLE `api_allowedrepo` DISABLE KEYS */;
/*!40000 ALTER TABLE `api_allowedrepo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (1,'rylibrary');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_425ae3c4` (`group_id`),
  KEY `auth_group_permissions_1e014c8f` (`permission_id`),
  CONSTRAINT `group_id_refs_id_3cea63fe` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `permission_id_refs_id_5886d21f` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_message`
--

DROP TABLE IF EXISTS `auth_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `auth_message_403f60f` (`user_id`),
  CONSTRAINT `user_id_refs_id_650f49a6` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_message`
--

LOCK TABLES `auth_message` WRITE;
/*!40000 ALTER TABLE `auth_message` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_1bb8f392` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_728de91f` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=308 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can add group',2,'add_group'),(5,'Can change group',2,'change_group'),(6,'Can delete group',2,'delete_group'),(7,'Can add user',3,'add_user'),(8,'Can change user',3,'change_user'),(9,'Can delete user',3,'delete_user'),(10,'Can add message',4,'add_message'),(11,'Can change message',4,'change_message'),(12,'Can delete message',4,'delete_message'),(13,'Can add content type',5,'add_contenttype'),(14,'Can change content type',5,'change_contenttype'),(15,'Can delete content type',5,'delete_contenttype'),(16,'Can add session',6,'add_session'),(17,'Can change session',6,'change_session'),(18,'Can delete session',6,'delete_session'),(19,'Can add site',7,'add_site'),(20,'Can change site',7,'change_site'),(21,'Can delete site',7,'delete_site'),(22,'Can add comment',8,'add_comment'),(23,'Can change comment',8,'change_comment'),(24,'Can delete comment',8,'delete_comment'),(25,'Can moderate comments',8,'can_moderate'),(26,'Can add comment flag',9,'add_commentflag'),(27,'Can change comment flag',9,'change_commentflag'),(28,'Can delete comment flag',9,'delete_commentflag'),(29,'Can add migration history',10,'add_migrationhistory'),(30,'Can change migration history',10,'change_migrationhistory'),(31,'Can delete migration history',10,'delete_migrationhistory'),(32,'Can add registration profile',11,'add_registrationprofile'),(33,'Can change registration profile',11,'change_registrationprofile'),(34,'Can delete registration profile',11,'delete_registrationprofile'),(35,'Can add user social auth',12,'add_usersocialauth'),(36,'Can change user social auth',12,'change_usersocialauth'),(37,'Can delete user social auth',12,'delete_usersocialauth'),(38,'Can add nonce',13,'add_nonce'),(39,'Can change nonce',13,'change_nonce'),(40,'Can delete nonce',13,'delete_nonce'),(41,'Can add association',14,'add_association'),(42,'Can change association',14,'change_association'),(43,'Can delete association',14,'delete_association'),(44,'Can add log entry',15,'add_logentry'),(45,'Can change log entry',15,'change_logentry'),(46,'Can delete log entry',15,'delete_logentry'),(47,'Can add queue',16,'add_queue'),(48,'Can change queue',16,'change_queue'),(49,'Can delete queue',16,'delete_queue'),(50,'Can add message',17,'add_message'),(51,'Can change message',17,'change_message'),(52,'Can delete message',17,'delete_message'),(53,'Can add celery task',18,'add_celerytask'),(54,'Can change celery task',18,'change_celerytask'),(55,'Can delete celery task',18,'delete_celerytask'),(56,'Can add claim',19,'add_claim'),(57,'Can change claim',19,'change_claim'),(58,'Can delete claim',19,'delete_claim'),(59,'Can add rights holder',20,'add_rightsholder'),(60,'Can change rights holder',20,'change_rightsholder'),(61,'Can delete rights holder',20,'delete_rightsholder'),(62,'Can add premium',21,'add_premium'),(63,'Can change premium',21,'change_premium'),(64,'Can delete premium',21,'delete_premium'),(65,'Can add campaign action',22,'add_campaignaction'),(66,'Can change campaign action',22,'change_campaignaction'),(67,'Can delete campaign action',22,'delete_campaignaction'),(68,'Can add campaign',23,'add_campaign'),(69,'Can change campaign',23,'change_campaign'),(70,'Can delete campaign',23,'delete_campaign'),(71,'Can add identifier',24,'add_identifier'),(72,'Can change identifier',24,'change_identifier'),(73,'Can delete identifier',24,'delete_identifier'),(74,'Can add work',25,'add_work'),(75,'Can change work',25,'change_work'),(76,'Can delete work',25,'delete_work'),(77,'Can add author',26,'add_author'),(78,'Can change author',26,'change_author'),(79,'Can delete author',26,'delete_author'),(80,'Can add subject',27,'add_subject'),(81,'Can change subject',27,'change_subject'),(82,'Can delete subject',27,'delete_subject'),(83,'Can add edition',28,'add_edition'),(84,'Can change edition',28,'change_edition'),(85,'Can delete edition',28,'delete_edition'),(86,'Can add was work',29,'add_waswork'),(87,'Can change was work',29,'change_waswork'),(88,'Can delete was work',29,'delete_waswork'),(89,'Can add ebook',30,'add_ebook'),(90,'Can change ebook',30,'change_ebook'),(91,'Can delete ebook',30,'delete_ebook'),(92,'Can add wishlist',31,'add_wishlist'),(93,'Can change wishlist',31,'change_wishlist'),(94,'Can delete wishlist',31,'delete_wishlist'),(95,'Can add wishes',32,'add_wishes'),(96,'Can change wishes',32,'change_wishes'),(97,'Can delete wishes',32,'delete_wishes'),(98,'Can add user profile',33,'add_userprofile'),(99,'Can change user profile',33,'change_userprofile'),(100,'Can delete user profile',33,'delete_userprofile'),(101,'Can add transaction',34,'add_transaction'),(102,'Can change transaction',34,'change_transaction'),(103,'Can delete transaction',34,'delete_transaction'),(104,'Can add payment response',35,'add_paymentresponse'),(105,'Can change payment response',35,'change_paymentresponse'),(106,'Can delete payment response',35,'delete_paymentresponse'),(107,'Can add receiver',36,'add_receiver'),(108,'Can change receiver',36,'change_receiver'),(109,'Can delete receiver',36,'delete_receiver'),(110,'Can add api access',37,'add_apiaccess'),(111,'Can change api access',37,'change_apiaccess'),(112,'Can delete api access',37,'delete_apiaccess'),(113,'Can add api key',38,'add_apikey'),(114,'Can change api key',38,'change_apikey'),(115,'Can delete api key',38,'delete_apikey'),(116,'Can add task meta',39,'add_taskmeta'),(117,'Can change task meta',39,'change_taskmeta'),(118,'Can delete task meta',39,'delete_taskmeta'),(119,'Can add taskset meta',40,'add_tasksetmeta'),(120,'Can change taskset meta',40,'change_tasksetmeta'),(121,'Can delete taskset meta',40,'delete_tasksetmeta'),(122,'Can add interval',41,'add_intervalschedule'),(123,'Can change interval',41,'change_intervalschedule'),(124,'Can delete interval',41,'delete_intervalschedule'),(125,'Can add crontab',42,'add_crontabschedule'),(126,'Can change crontab',42,'change_crontabschedule'),(127,'Can delete crontab',42,'delete_crontabschedule'),(128,'Can add periodic tasks',43,'add_periodictasks'),(129,'Can change periodic tasks',43,'change_periodictasks'),(130,'Can delete periodic tasks',43,'delete_periodictasks'),(131,'Can add periodic task',44,'add_periodictask'),(132,'Can change periodic task',44,'change_periodictask'),(133,'Can delete periodic task',44,'delete_periodictask'),(134,'Can add worker',45,'add_workerstate'),(135,'Can change worker',45,'change_workerstate'),(136,'Can delete worker',45,'delete_workerstate'),(137,'Can add task',46,'add_taskstate'),(138,'Can change task',46,'change_taskstate'),(139,'Can delete task',46,'delete_taskstate'),(140,'Can add notice type',47,'add_noticetype'),(141,'Can change notice type',47,'change_noticetype'),(142,'Can delete notice type',47,'delete_noticetype'),(143,'Can add notice setting',48,'add_noticesetting'),(144,'Can change notice setting',48,'change_noticesetting'),(145,'Can delete notice setting',48,'delete_noticesetting'),(146,'Can add notice',49,'add_notice'),(147,'Can change notice',49,'change_notice'),(148,'Can delete notice',49,'delete_notice'),(149,'Can add notice queue batch',50,'add_noticequeuebatch'),(150,'Can change notice queue batch',50,'change_noticequeuebatch'),(151,'Can delete notice queue batch',50,'delete_noticequeuebatch'),(152,'Can add observed item',51,'add_observeditem'),(153,'Can change observed item',51,'change_observeditem'),(154,'Can delete observed item',51,'delete_observeditem'),(155,'Can add key',52,'add_key'),(156,'Can change key',52,'change_key'),(157,'Can delete key',52,'delete_key'),(158,'Can add email change request',53,'add_emailchangerequest'),(159,'Can change email change request',53,'change_emailchangerequest'),(160,'Can delete email change request',53,'delete_emailchangerequest'),(161,'Can add kv store',54,'add_kvstore'),(162,'Can change kv store',54,'change_kvstore'),(163,'Can delete kv store',54,'delete_kvstore'),(164,'Can add allowed repo',55,'add_allowedrepo'),(165,'Can change allowed repo',55,'change_allowedrepo'),(166,'Can delete allowed repo',55,'delete_allowedrepo'),(167,'Can add bisac heading',56,'add_bisacheading'),(168,'Can change bisac heading',56,'change_bisacheading'),(169,'Can delete bisac heading',56,'delete_bisacheading'),(170,'Can add offer',57,'add_offer'),(171,'Can change offer',57,'change_offer'),(172,'Can delete offer',57,'delete_offer'),(173,'Can add acq',58,'add_acq'),(174,'Can change acq',58,'change_acq'),(175,'Can delete acq',58,'delete_acq'),(176,'Can add hold',59,'add_hold'),(177,'Can change hold',59,'change_hold'),(178,'Can delete hold',59,'delete_hold'),(179,'Can add relation',60,'add_relation'),(180,'Can change relation',60,'change_relation'),(181,'Can delete relation',60,'delete_relation'),(182,'Can add relator',61,'add_relator'),(183,'Can change relator',61,'change_relator'),(184,'Can delete relator',61,'delete_relator'),(185,'Can add publisher',62,'add_publisher'),(186,'Can change publisher',62,'change_publisher'),(187,'Can delete publisher',62,'delete_publisher'),(188,'Can add publisher name',63,'add_publishername'),(189,'Can change publisher name',63,'change_publishername'),(190,'Can delete publisher name',63,'delete_publishername'),(191,'Can add ebook file',64,'add_ebookfile'),(192,'Can change ebook file',64,'change_ebookfile'),(193,'Can delete ebook file',64,'delete_ebookfile'),(194,'Can add badge',65,'add_badge'),(195,'Can change badge',65,'change_badge'),(196,'Can delete badge',65,'delete_badge'),(197,'Can add libpref',66,'add_libpref'),(198,'Can change libpref',66,'change_libpref'),(199,'Can delete libpref',66,'delete_libpref'),(200,'Can add press',67,'add_press'),(201,'Can change press',67,'change_press'),(202,'Can delete press',67,'delete_press'),(203,'Can add gift',68,'add_gift'),(204,'Can change gift',68,'change_gift'),(205,'Can delete gift',68,'delete_gift'),(206,'Can add marc record',69,'add_marcrecord'),(207,'Can change marc record',69,'change_marcrecord'),(208,'Can delete marc record',69,'delete_marcrecord'),(209,'Can add credit log',70,'add_creditlog'),(210,'Can change credit log',70,'change_creditlog'),(211,'Can delete credit log',70,'delete_creditlog'),(212,'Can add credit',71,'add_credit'),(213,'Can change credit',71,'change_credit'),(214,'Can delete credit',71,'delete_credit'),(215,'Can add sent',72,'add_sent'),(216,'Can change sent',72,'change_sent'),(217,'Can delete sent',72,'delete_sent'),(218,'Can add account',73,'add_account'),(219,'Can change account',73,'change_account'),(220,'Can delete account',73,'delete_account'),(221,'Can add landing',74,'add_landing'),(222,'Can change landing',74,'change_landing'),(223,'Can delete landing',74,'delete_landing'),(224,'Can add boox',75,'add_boox'),(225,'Can change boox',75,'change_boox'),(226,'Can delete boox',75,'delete_boox'),(227,'Can add library',76,'add_library'),(228,'Can change library',76,'change_library'),(229,'Can delete library',76,'delete_library'),(230,'Can add block',77,'add_block'),(231,'Can change block',77,'change_block'),(232,'Can delete block',77,'delete_block'),(233,'Can add card pattern',78,'add_cardpattern'),(234,'Can change card pattern',78,'change_cardpattern'),(235,'Can delete card pattern',78,'delete_cardpattern'),(236,'Can add library user',79,'add_libraryuser'),(237,'Can change library user',79,'change_libraryuser'),(238,'Can delete library user',79,'delete_libraryuser'),(239,'Can add email pattern',80,'add_emailpattern'),(240,'Can change email pattern',80,'change_emailpattern'),(241,'Can delete email pattern',80,'delete_emailpattern'),(242,'Can add page',81,'add_page'),(243,'Can change page',81,'change_page'),(244,'Can delete page',81,'delete_page'),(245,'Can add target',82,'add_target'),(246,'Can change target',82,'change_target'),(247,'Can delete target',82,'delete_target'),(248,'Can add deposit',83,'add_deposit'),(249,'Can change deposit',83,'change_deposit'),(250,'Can delete deposit',83,'delete_deposit'),(251,'Can add format',84,'add_format'),(252,'Can change format',84,'change_format'),(253,'Can delete format',84,'delete_format'),(254,'Can add subject',85,'add_subject'),(255,'Can change subject',85,'change_subject'),(256,'Can delete subject',85,'delete_subject'),(257,'Can add global styles',86,'add_globalstyles'),(258,'Can change global styles',86,'change_globalstyles'),(259,'Can delete global styles',86,'delete_globalstyles'),(260,'Can add questionnaire',87,'add_questionnaire'),(261,'Can change questionnaire',87,'change_questionnaire'),(262,'Can delete questionnaire',87,'delete_questionnaire'),(263,'Can export questionnaire answers',87,'export'),(264,'Management Tools',87,'management'),(265,'Can add landing',88,'add_landing'),(266,'Can change landing',88,'change_landing'),(267,'Can delete landing',88,'delete_landing'),(268,'Can add db stylesheet',89,'add_dbstylesheet'),(269,'Can change db stylesheet',89,'change_dbstylesheet'),(270,'Can delete db stylesheet',89,'delete_dbstylesheet'),(271,'Can add question set',90,'add_questionset'),(272,'Can change question set',90,'change_questionset'),(273,'Can delete question set',90,'delete_questionset'),(274,'Can add run info',91,'add_runinfo'),(275,'Can change run info',91,'change_runinfo'),(276,'Can delete run info',91,'delete_runinfo'),(277,'Can add run info history',92,'add_runinfohistory'),(278,'Can change run info history',92,'change_runinfohistory'),(279,'Can delete run info history',92,'delete_runinfohistory'),(280,'Can add question',93,'add_question'),(281,'Can change question',93,'change_question'),(282,'Can delete question',93,'delete_question'),(283,'Can add choice',94,'add_choice'),(284,'Can change choice',94,'change_choice'),(285,'Can delete choice',94,'delete_choice'),(286,'Can add answer',95,'add_answer'),(287,'Can change answer',95,'change_answer'),(288,'Can delete answer',95,'delete_answer'),(289,'Can add comment',96,'add_comment'),(290,'Can change comment',96,'change_comment'),(291,'Can delete comment',96,'delete_comment'),(292,'Can moderate comments',96,'can_moderate'),(293,'Can add comment flag',97,'add_commentflag'),(294,'Can change comment flag',97,'change_commentflag'),(295,'Can delete comment flag',97,'delete_commentflag'),(296,'Can add user social auth',98,'add_usersocialauth'),(297,'Can change user social auth',98,'change_usersocialauth'),(298,'Can delete user social auth',98,'delete_usersocialauth'),(299,'Can add nonce',99,'add_nonce'),(300,'Can change nonce',99,'change_nonce'),(301,'Can delete nonce',99,'delete_nonce'),(302,'Can add association',100,'add_association'),(303,'Can change association',100,'change_association'),(304,'Can delete association',100,'delete_association'),(305,'Can add code',101,'add_code'),(306,'Can change code',101,'change_code'),(307,'Can delete code',101,'delete_code');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(254) NOT NULL,
  `password` varchar(128) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'RaymondYee','Raymond','Yee','rdhyee@gluejar.com','!',0,1,0,'2012-03-02 13:17:24.000000','2012-03-02 13:17:24'),(2,'rdhyee','Raymond','Yee','raymond.yee@gmail.com','sha1$e2d7b$55e51c0fad5f39292e7f99ad180c8ab31bb5bbc1',1,1,1,'2012-03-02 13:22:05.000000','2012-03-02 13:21:21'),(3,'rdhyeetest','','','raymond.yee@dataunbound.com','pbkdf2_sha256$12000$phVMOxBL7JfW$3GxX4F9iHa2o3HIVhHR2P1ufPUcTZpNkBzxOD0a3H00=',0,1,0,'2016-04-21 12:53:40.000000','2012-03-13 19:11:32'),(4,'paypaltest','','','raymondyee@mashupguide.net','sha1$2e5f9$7d642321bf209341164f3dca13c656d329e6af60',1,1,0,'2012-05-09 14:34:52.000000','2012-05-09 14:34:52'),(5,'yee-example','','','yee@example.org','pbkdf2_sha256$12000$6elL0ltxJPOY$PEBaVdNEaikqxPXXZX+GAJBa0Oi0HiEFv0GkXNpB4Qc=',0,1,0,'2016-04-21 12:54:54.000000','2016-04-21 12:52:00'),(6,'RightsatUnglueit','','','rights@gluejar.com','',0,1,0,'2016-04-21 12:52:01.000000','2016-04-21 12:52:01'),(7,'rylibrary','','','rylibrary@example.org','',0,1,0,'2016-04-21 12:54:56.000000','2016-04-21 12:54:55');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_403f60f` (`user_id`),
  KEY `auth_user_groups_425ae3c4` (`group_id`),
  CONSTRAINT `group_id_refs_id_f116770` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `user_id_refs_id_7ceef80f` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
INSERT INTO `auth_user_groups` VALUES (2,5,1),(1,7,1);
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_403f60f` (`user_id`),
  KEY `auth_user_user_permissions_1e014c8f` (`permission_id`),
  CONSTRAINT `permission_id_refs_id_67e79cb` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `user_id_refs_id_dfbab7d` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bisac_bisacheading`
--

DROP TABLE IF EXISTS `bisac_bisacheading`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bisac_bisacheading` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `full_label` varchar(100) NOT NULL,
  `label` varchar(60) NOT NULL,
  `notation` varchar(9) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `lft` int(10) unsigned NOT NULL,
  `rght` int(10) unsigned NOT NULL,
  `tree_id` int(10) unsigned NOT NULL,
  `level` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `full_label` (`full_label`),
  KEY `bisac_bisacheading_410d0aac` (`parent_id`),
  KEY `bisac_bisacheading_329f6fb3` (`lft`),
  KEY `bisac_bisacheading_e763210f` (`rght`),
  KEY `bisac_bisacheading_ba470c4a` (`tree_id`),
  KEY `bisac_bisacheading_20e079f4` (`level`),
  CONSTRAINT `parent_id_refs_id_6000acca` FOREIGN KEY (`parent_id`) REFERENCES `bisac_bisacheading` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bisac_bisacheading`
--

LOCK TABLES `bisac_bisacheading` WRITE;
/*!40000 ALTER TABLE `bisac_bisacheading` DISABLE KEYS */;
/*!40000 ALTER TABLE `bisac_bisacheading` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booxtream_boox`
--

DROP TABLE IF EXISTS `booxtream_boox`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `booxtream_boox` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `download_link_epub` varchar(200) DEFAULT NULL,
  `download_link_mobi` varchar(200) DEFAULT NULL,
  `referenceid` varchar(32) NOT NULL,
  `downloads_remaining` smallint(5) unsigned NOT NULL,
  `expirydays` smallint(5) unsigned NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booxtream_boox`
--

LOCK TABLES `booxtream_boox` WRITE;
/*!40000 ALTER TABLE `booxtream_boox` DISABLE KEYS */;
INSERT INTO `booxtream_boox` VALUES (1,'http://download.booxtream.com/get/3351679482.571905d8d1ec77.93302499.epub','http://download.booxtream.com/get/3351679482.571905d8d1ec77.93302499.mobi','52:3:1',7,1,'2016-04-21 12:54:52');
/*!40000 ALTER TABLE `booxtream_boox` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `celery_taskmeta`
--

DROP TABLE IF EXISTS `celery_taskmeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `celery_taskmeta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_id` varchar(255) NOT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'PENDING',
  `result` longtext,
  `date_done` datetime NOT NULL,
  `traceback` longtext,
  `hidden` tinyint(1) NOT NULL,
  `meta` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_id` (`task_id`),
  KEY `celery_taskmeta_2ff6b945` (`hidden`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `celery_taskmeta`
--

LOCK TABLES `celery_taskmeta` WRITE;
/*!40000 ALTER TABLE `celery_taskmeta` DISABLE KEYS */;
/*!40000 ALTER TABLE `celery_taskmeta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `celery_tasksetmeta`
--

DROP TABLE IF EXISTS `celery_tasksetmeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `celery_tasksetmeta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `taskset_id` varchar(255) NOT NULL,
  `result` longtext NOT NULL,
  `date_done` datetime NOT NULL,
  `hidden` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `taskset_id` (`taskset_id`),
  KEY `celery_tasksetmeta_2ff6b945` (`hidden`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `celery_tasksetmeta`
--

LOCK TABLES `celery_tasksetmeta` WRITE;
/*!40000 ALTER TABLE `celery_tasksetmeta` DISABLE KEYS */;
/*!40000 ALTER TABLE `celery_tasksetmeta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_acq`
--

DROP TABLE IF EXISTS `core_acq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_acq` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `expires` datetime DEFAULT NULL,
  `work_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `license` smallint(5) unsigned NOT NULL,
  `watermarked_id` int(11) DEFAULT NULL,
  `nonce` varchar(32) DEFAULT NULL,
  `refreshes` datetime NOT NULL,
  `lib_acq_id` int(11) DEFAULT NULL,
  `refreshed` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_acq_dfb5c784` (`work_id`),
  KEY `core_acq_6340c63c` (`user_id`),
  KEY `core_acq_e985424f` (`watermarked_id`),
  KEY `core_acq_900c31e6` (`lib_acq_id`),
  KEY `core_acq_63b5ea41` (`created`),
  CONSTRAINT `lib_acq_id_refs_id_69ee4cfe` FOREIGN KEY (`lib_acq_id`) REFERENCES `core_acq` (`id`),
  CONSTRAINT `user_id_refs_id_111f77be` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `watermarked_id_refs_id_5b94149c` FOREIGN KEY (`watermarked_id`) REFERENCES `booxtream_boox` (`id`),
  CONSTRAINT `work_id_refs_id_61481778` FOREIGN KEY (`work_id`) REFERENCES `core_work` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_acq`
--

LOCK TABLES `core_acq` WRITE;
/*!40000 ALTER TABLE `core_acq` DISABLE KEYS */;
INSERT INTO `core_acq` VALUES (1,'2016-04-21 12:54:21',NULL,52,3,0,1,'c8d558d1f9cd7bac678043d78dbe5ac3','2016-04-21 12:54:21',NULL,1),(2,'2016-04-21 12:54:59',NULL,52,7,2,NULL,'200a4ff92cf2b9dcea8779c1f86239a1','2016-04-21 12:54:59',NULL,1);
/*!40000 ALTER TABLE `core_acq` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_author`
--

DROP TABLE IF EXISTS `core_author`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_author` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_author_name_723fcfc05e1849ee_uniq` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_author`
--

LOCK TABLES `core_author` WRITE;
/*!40000 ALTER TABLE `core_author` DISABLE KEYS */;
INSERT INTO `core_author` VALUES (1,'2012-03-02 13:02:58','Jorge Luis Borges'),(2,'2012-03-02 13:02:59','Djuna Barnes'),(3,'2012-03-02 13:02:59','Thomas Stearns Eliot'),(4,'2012-03-02 13:02:59','Jeanette Winterson'),(5,'2012-03-02 13:03:00','Gertrude Stein'),(6,'2012-03-02 13:03:00','Janet Flanner'),(7,'2012-03-02 13:03:00','Irving Drutman'),(8,'2012-03-02 13:03:01','Sylvia Beach'),(9,'2012-03-02 13:03:01','Keri Walsh'),(10,'2012-03-02 13:03:02','John B. Thompson'),(11,'2012-03-02 13:03:03','Noel Riley Fitch'),(12,'2012-03-02 13:03:04','Jessica Mitford'),(13,'2012-03-02 13:03:04','Christopher Hitchens'),(14,'2012-03-02 13:03:05','Jessamyn West'),(15,'2012-03-02 13:03:07','Julian P. Muller'),(16,'2012-03-02 13:03:07','Thomas J. Watson'),(17,'2012-03-02 13:03:07','Peter Petre'),(18,'2012-03-02 13:03:08','Samuel R. Delany'),(19,'2012-03-02 13:03:09','Daniel Goleman'),(20,'2012-03-02 13:03:10','Heidi Murkoff'),(21,'2012-03-02 13:03:10','Sharon Mazel'),(22,'2012-03-02 13:03:11','Manning Rubin'),(23,'2012-03-02 13:03:11','Paul Frahm'),(24,'2012-03-02 13:03:12','Lawrence Weschler'),(25,'2012-03-02 13:03:12','Getty Foundation'),(26,'2012-03-02 13:03:13','Roland Huntford'),(27,'2012-03-02 13:03:13','Wael Ghonim'),(28,'2012-03-02 13:03:14','Meredith Hooper'),(29,'2012-03-02 13:03:15','Dashiell Hammett'),(30,'2012-03-02 13:03:15','Richard Layman'),(31,'2012-03-02 13:03:15','Mary McCarthy'),(32,'2012-03-02 13:03:16','Sandra M. Gilbert'),(33,'2012-03-02 13:03:16','Susan Gubar'),(34,'2012-03-02 13:03:17','Elaine Showalter'),(35,'2012-03-02 13:03:17','Nancy Rawles'),(36,'2012-03-02 13:03:18','Ted Morgan'),(37,'2012-03-02 13:03:19','Michael Herr'),(38,'2012-03-02 13:03:19','Robert Stone'),(39,'2012-03-02 13:03:20','Archimedes L. A. Patti'),(40,'2012-03-02 13:03:20','Amnon Yariv'),(41,'2012-03-02 13:03:21','Neil W. Ashcroft'),(42,'2012-03-02 13:03:21','N. David Mermin'),(43,'2012-03-02 13:03:22','James L. Gould'),(44,'2012-03-02 13:03:22','Carol Grant Gould'),(45,'2012-03-02 13:03:26','Konrad Lorenz'),(46,'2012-03-02 13:03:26','Michael Martys'),(47,'2012-03-02 13:03:26','Angelika Tipler'),(48,'2012-03-02 13:03:26','Vernor Vinge'),(49,'2012-03-02 13:03:27','William Gibson'),(50,'2012-03-02 13:03:28','Nicholas Meyer'),(51,'2012-03-02 13:03:29','Oliver W. Sacks'),(52,'2012-03-02 13:03:29','Ursula K. Le Guin'),(53,'2012-03-02 13:03:31','John Le Carré'),(54,'2016-04-21 12:52:01','Raymond Yee'),(55,'2016-08-25 18:30:45','梅尔维尔 (美)');
/*!40000 ALTER TABLE `core_author` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_author_editions`
--

DROP TABLE IF EXISTS `core_author_editions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_author_editions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `author_id` int(11) NOT NULL,
  `edition_id` int(11) NOT NULL,
  `relation_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_author_editions_author_id_7e744d9d_uniq` (`author_id`,`edition_id`),
  KEY `core_author_editions_337b96ff` (`author_id`),
  KEY `core_author_editions_16ab133f` (`edition_id`),
  KEY `core_author_editions_d525a588` (`relation_id`),
  CONSTRAINT `author_id_refs_id_17a0e6c8` FOREIGN KEY (`author_id`) REFERENCES `core_author` (`id`),
  CONSTRAINT `edition_id_refs_id_6d94098` FOREIGN KEY (`edition_id`) REFERENCES `core_edition` (`id`),
  CONSTRAINT `relation_id_refs_id_4fa4862a` FOREIGN KEY (`relation_id`) REFERENCES `core_relation` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_author_editions`
--

LOCK TABLES `core_author_editions` WRITE;
/*!40000 ALTER TABLE `core_author_editions` DISABLE KEYS */;
INSERT INTO `core_author_editions` VALUES (1,1,1,1),(2,2,2,1),(3,3,2,1),(4,4,2,1),(5,5,3,1),(6,6,4,1),(7,7,4,1),(8,8,5,1),(9,8,6,1),(10,9,6,1),(11,10,7,1),(12,11,8,1),(13,12,9,1),(14,13,9,1),(15,14,10,1),(16,14,11,1),(17,14,12,1),(18,14,13,1),(19,15,13,1),(20,16,14,1),(21,17,14,1),(22,18,15,1),(23,19,16,1),(24,19,17,1),(25,19,18,1),(26,20,19,1),(27,21,19,1),(28,22,20,1),(29,23,20,1),(30,24,21,1),(31,25,21,1),(32,24,22,1),(33,26,23,1),(34,27,24,1),(35,28,25,1),(36,29,26,1),(37,30,26,1),(38,31,27,1),(39,32,28,1),(40,33,28,1),(41,34,29,1),(42,35,30,1),(43,36,31,1),(44,36,32,1),(45,37,33,1),(46,38,33,1),(47,39,34,1),(48,40,35,1),(49,41,36,1),(50,42,36,1),(51,43,37,1),(52,44,37,1),(53,43,38,1),(54,44,38,1),(55,43,39,1),(56,44,39,1),(57,44,40,1),(58,43,41,1),(59,45,42,1),(60,46,42,1),(61,47,42,1),(62,48,43,1),(63,49,44,1),(64,50,45,1),(65,51,46,1),(66,52,47,1),(67,52,48,1),(68,52,49,1),(69,53,50,1),(70,53,51,1),(71,54,52,1),(72,55,53,1);
/*!40000 ALTER TABLE `core_author_editions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_badge`
--

DROP TABLE IF EXISTS `core_badge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_badge` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(72) NOT NULL,
  `description` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_badge`
--

LOCK TABLES `core_badge` WRITE;
/*!40000 ALTER TABLE `core_badge` DISABLE KEYS */;
INSERT INTO `core_badge` VALUES (1,'pledger','a pledger'),(2,'pledger2','a repeat pledger');
/*!40000 ALTER TABLE `core_badge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_campaign`
--

DROP TABLE IF EXISTS `core_campaign`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_campaign` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `name` varchar(500) DEFAULT NULL,
  `description` longtext,
  `details` longtext,
  `target` decimal(14,2) DEFAULT NULL,
  `deadline` datetime DEFAULT NULL,
  `activated` datetime DEFAULT NULL,
  `paypal_receiver` varchar(100) NOT NULL,
  `amazon_receiver` varchar(100) NOT NULL,
  `work_id` int(11) NOT NULL,
  `status` varchar(15) DEFAULT NULL,
  `left` decimal(14,2) DEFAULT NULL,
  `license` varchar(255) NOT NULL,
  `edition_id` int(11) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `publisher_id` int(11) DEFAULT NULL,
  `dollar_per_day` double DEFAULT NULL,
  `cc_date_initial` datetime DEFAULT NULL,
  `type` smallint(5) unsigned NOT NULL,
  `do_watermark` tinyint(1) NOT NULL,
  `use_add_ask` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_campaign_50cafa73` (`work_id`),
  KEY `core_campaign_16ab133f` (`edition_id`),
  KEY `core_campaign_b50d97d6` (`deadline`),
  KEY `core_campaign_81b79144` (`publisher_id`),
  KEY `core_campaign_48fb58bb` (`status`),
  KEY `core_campaign_f24bf87c` (`activated`),
  KEY `core_campaign_024f9524` (`left`),
  CONSTRAINT `edition_id_refs_id_64d79e7a` FOREIGN KEY (`edition_id`) REFERENCES `core_edition` (`id`),
  CONSTRAINT `publisher_id_refs_id_949a052d` FOREIGN KEY (`publisher_id`) REFERENCES `core_publisher` (`id`),
  CONSTRAINT `work_id_refs_id_fe13496` FOREIGN KEY (`work_id`) REFERENCES `core_work` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_campaign`
--

LOCK TABLES `core_campaign` WRITE;
/*!40000 ALTER TABLE `core_campaign` DISABLE KEYS */;
INSERT INTO `core_campaign` VALUES (1,'2012-03-02 13:04:03','60 ways to relieve stress in 60 seconds','Test Campaign',NULL,8424.00,'2012-05-17 02:36:40',NULL,'rh1_1317336251_biz@gluejar.com','',20,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(2,'2012-03-02 13:04:03','A literature of their own','Test Campaign',NULL,1950.00,'2012-04-25 16:22:09',NULL,'rh1_1317336251_biz@gluejar.com','',29,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(3,'2012-03-02 13:04:03','A Wizard of Earthsea','Test Campaign',NULL,1636.00,'2012-03-07 17:26:54',NULL,'rh1_1317336251_biz@gluejar.com','',48,'ACTIVE',1636.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(4,'2012-03-02 13:04:03','Animal architects','Test Campaign',NULL,1709.00,'2012-07-12 14:12:21',NULL,'rh1_1317336251_biz@gluejar.com','',37,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(5,'2012-03-02 13:04:03','Animal Architects','Test Campaign',NULL,7554.00,'2012-07-22 16:14:02',NULL,'rh1_1317336251_biz@gluejar.com','',38,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(6,'2012-03-02 13:04:03','Call for the Dead','Test Campaign',NULL,7057.00,'2012-05-12 20:22:17',NULL,'rh1_1317336251_biz@gluejar.com','',51,'ACTIVE',7057.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(7,'2012-03-02 13:04:03','Collected Stories of Jessamyn West','Test Campaign',NULL,1252.00,'2012-06-12 06:48:30',NULL,'rh1_1317336251_biz@gluejar.com','',13,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(8,'2012-03-02 13:04:03','Dhalgren','Test Campaign',NULL,4776.00,'2012-04-30 23:12:21',NULL,'rh1_1317336251_biz@gluejar.com','',15,'ACTIVE',4776.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(9,'2012-03-02 13:04:03','Dispatches','Test Campaign',NULL,6557.00,'2012-06-23 15:38:50',NULL,'rh1_1317336251_biz@gluejar.com','',33,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(10,'2012-03-02 13:04:03','Emotional intelligence','Test Campaign',NULL,7972.00,'2012-08-21 19:47:26',NULL,'rh1_1317336251_biz@gluejar.com','',16,'ACTIVE',7972.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(11,'2012-03-02 13:04:03','Ethology','Test Campaign',NULL,2142.00,'2012-06-12 10:59:01',NULL,'rh1_1317336251_biz@gluejar.com','',41,'ACTIVE',2142.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(12,'2012-03-02 13:04:03','Father, Son & Co.','Test Campaign',NULL,2837.00,'2012-08-26 15:59:21',NULL,'rh1_1317336251_biz@gluejar.com','',14,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(13,'2012-03-02 13:04:03','Four Ways to Forgiveness','Test Campaign',NULL,9515.00,'2012-03-09 20:47:59',NULL,'rh1_1317336251_biz@gluejar.com','',49,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(14,'2012-03-02 13:04:03','Here am I--where are you?','Test Campaign',NULL,4545.00,'2012-03-10 05:06:43',NULL,'rh1_1317336251_biz@gluejar.com','',42,'ACTIVE',4545.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(15,'2012-03-02 13:04:03','Hons and Rebels','Test Campaign',NULL,6902.00,'2012-08-28 22:00:05',NULL,'rh1_1317336251_biz@gluejar.com','',9,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(16,'2012-03-02 13:04:03','Labyrinths','Test Campaign',NULL,4434.00,'2012-08-12 17:14:25',NULL,'rh1_1317336251_biz@gluejar.com','',1,'ACTIVE',4434.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(17,'2012-03-02 13:04:03','Love like gumbo','Test Campaign',NULL,5129.00,'2012-06-22 05:11:03',NULL,'rh1_1317336251_biz@gluejar.com','',30,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(18,'2012-03-02 13:04:03','Maugham','Test Campaign',NULL,1833.00,'2012-08-04 06:36:01',NULL,'rh1_1317336251_biz@gluejar.com','',31,'ACTIVE',1833.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(19,'2012-03-02 13:04:04','Merchants of Culture','Test Campaign',NULL,4231.00,'2012-04-22 14:36:16',NULL,'rh1_1317336251_biz@gluejar.com','',7,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(20,'2012-03-02 13:04:04','My battle of Algiers','Test Campaign',NULL,6451.00,'2012-05-01 19:39:11',NULL,'rh1_1317336251_biz@gluejar.com','',32,'ACTIVE',6451.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(21,'2012-03-02 13:04:04','Neuromancer','Test Campaign',NULL,7071.00,'2012-07-29 12:32:08',NULL,'rh1_1317336251_biz@gluejar.com','',44,'ACTIVE',7071.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(22,'2012-03-02 13:04:04','Nightwood','Test Campaign',NULL,5770.00,'2012-08-05 19:27:05',NULL,'rh1_1317336251_biz@gluejar.com','',2,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(23,'2012-03-02 13:04:04','Paris was yesterday','Test Campaign',NULL,4506.00,'2012-08-24 19:28:42',NULL,'rh1_1317336251_biz@gluejar.com','',4,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(24,'2012-03-02 13:04:04','Quantum electronics','Test Campaign',NULL,1503.00,'2012-06-24 05:45:09',NULL,'rh1_1317336251_biz@gluejar.com','',35,'ACTIVE',1503.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(25,'2012-03-02 13:04:04','Rainbows End','Test Campaign',NULL,5194.00,'2012-05-01 05:04:27',NULL,'rh1_1317336251_biz@gluejar.com','',43,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(26,'2012-03-02 13:04:04','Revolution 2:0','Test Campaign',NULL,5154.00,'2012-07-07 10:11:52',NULL,'rh1_1317336251_biz@gluejar.com','',24,'ACTIVE',5154.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(27,'2012-03-02 13:04:04','Seeing is forgetting the name of the thing one sees','Test Campaign',NULL,8275.00,'2012-08-12 11:53:29',NULL,'rh1_1317336251_biz@gluejar.com','',21,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(28,'2012-03-02 13:04:04','Seeing voices','Test Campaign',NULL,7760.00,'2012-04-15 09:55:26',NULL,'rh1_1317336251_biz@gluejar.com','',46,'ACTIVE',7760.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(29,'2012-03-02 13:04:04','Selected Letters of Dashiell Hammett: 1921-1960','Test Campaign',NULL,8350.00,'2012-05-09 07:28:03',NULL,'rh1_1317336251_biz@gluejar.com','',26,'ACTIVE',8350.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(30,'2012-03-02 13:04:04','Shakespeare and Company','Test Campaign',NULL,5220.00,'2012-07-03 21:15:22',NULL,'rh1_1317336251_biz@gluejar.com','',5,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(31,'2012-03-02 13:04:04','Solid state physics','Test Campaign',NULL,4675.00,'2012-04-05 18:15:22',NULL,'rh1_1317336251_biz@gluejar.com','',36,'ACTIVE',4675.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(32,'2012-03-02 13:04:04','Sylvia Beach and the Lost Generation','Test Campaign',NULL,3389.00,'2012-03-16 15:14:33',NULL,'rh1_1317336251_biz@gluejar.com','',8,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(33,'2012-03-02 13:04:04','The animal mind','Test Campaign',NULL,2955.00,'2012-05-26 08:46:29',NULL,'rh1_1317336251_biz@gluejar.com','',39,'ACTIVE',2955.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(34,'2012-03-02 13:04:04','The Friendly Persuasion','Test Campaign',NULL,1933.00,'2012-03-18 12:36:56',NULL,'rh1_1317336251_biz@gluejar.com','',10,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(35,'2012-03-02 13:04:04','The group','Test Campaign',NULL,2325.00,'2012-07-27 22:44:31',NULL,'rh1_1317336251_biz@gluejar.com','',27,'ACTIVE',2325.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(36,'2012-03-02 13:04:04','The Last Place on Earth','Test Campaign',NULL,4197.00,'2012-04-05 10:52:52',NULL,'rh1_1317336251_biz@gluejar.com','',23,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(37,'2012-03-02 13:04:04','The left hand of darkness','Test Campaign',NULL,9996.00,'2012-03-13 20:52:58',NULL,'rh1_1317336251_biz@gluejar.com','',47,'ACTIVE',9996.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(38,'2012-03-02 13:04:04','The letters of Sylvia Beach','Test Campaign',NULL,9578.00,'2012-04-05 20:07:06',NULL,'rh1_1317336251_biz@gluejar.com','',6,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(39,'2012-03-02 13:04:04','The Longest Winter','Test Campaign',NULL,623.00,'2012-06-17 09:53:12',NULL,'rh1_1317336251_biz@gluejar.com','',25,'ACTIVE',623.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(40,'2012-03-02 13:04:04','The madwoman in the attic','Test Campaign',NULL,1738.00,'2012-07-30 01:18:14',NULL,'rh1_1317336251_biz@gluejar.com','',28,'ACTIVE',1738.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(41,'2012-03-02 13:04:04','The making of Americans','Test Campaign',NULL,660.00,'2012-07-01 04:21:11',NULL,'rh1_1317336251_biz@gluejar.com','',3,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(42,'2012-03-02 13:04:04','The Massacre at Fall Creek','Test Campaign',NULL,631.00,'2012-03-18 02:57:42',NULL,'rh1_1317336251_biz@gluejar.com','',11,'ACTIVE',631.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(43,'2012-03-02 13:04:04','The remarkable life of William Beebe','Test Campaign',NULL,6519.00,'2012-05-12 06:19:39',NULL,'rh1_1317336251_biz@gluejar.com','',40,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(44,'2012-03-02 13:04:04','The seven-per-cent solution','Test Campaign',NULL,8684.00,'2012-03-08 17:25:05',NULL,'rh1_1317336251_biz@gluejar.com','',45,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(45,'2012-03-02 13:04:04','The Spy Who Came in from the Cold','Test Campaign',NULL,6151.00,'2012-05-06 13:43:59',NULL,'rh1_1317336251_biz@gluejar.com','',50,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(46,'2012-03-02 13:04:04','Vermeer in Bosnia: selected writings','Test Campaign',NULL,8466.00,'2012-05-28 12:14:10',NULL,'rh1_1317336251_biz@gluejar.com','',22,'ACTIVE',8466.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(47,'2012-03-02 13:04:04','Vital lies, simple truths','Test Campaign',NULL,1224.00,'2012-04-05 13:50:30',NULL,'rh1_1317336251_biz@gluejar.com','',18,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(48,'2012-03-02 13:04:04','What to Expect When You\'re Expecting','Test Campaign',NULL,2814.00,'2012-07-03 05:14:26',NULL,'rh1_1317336251_biz@gluejar.com','',19,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(49,'2012-03-02 13:04:04','Why Viet Nam?','Test Campaign',NULL,7074.00,'2012-04-24 01:35:55',NULL,'rh1_1317336251_biz@gluejar.com','',34,'ACTIVE',7074.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(50,'2012-03-02 13:04:04','Woman Said Yes','Test Campaign',NULL,5191.00,'2012-06-18 12:09:57',NULL,'rh1_1317336251_biz@gluejar.com','',12,'INITIALIZED',NULL,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(51,'2012-03-02 13:04:04','Working with emotional intelligence','Test Campaign',NULL,8852.00,'2012-04-14 23:35:50',NULL,'rh1_1317336251_biz@gluejar.com','',17,'ACTIVE',8852.00,'CC BY-NC-ND',NULL,'',NULL,NULL,NULL,1,1,1),(52,'2016-04-21 12:52:01','Pro Web 2.0 Mashups','<p>&quot;Buy this book for the sake of humanity!</p>\r\n','',1000.00,NULL,'2016-04-21 12:54:53','raymond.yee@dataunbound.com','',52,'ACTIVE',990.00,'CC BY-NC-ND',52,'',NULL,0.199920031987205,'2030-01-01 00:00:00',2,1,0);
/*!40000 ALTER TABLE `core_campaign` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_campaign_managers`
--

DROP TABLE IF EXISTS `core_campaign_managers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_campaign_managers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `campaign_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_campaign_managers_campaign_id_6201021a_uniq` (`campaign_id`,`user_id`),
  KEY `core_campaign_managers_702b94e6` (`campaign_id`),
  KEY `core_campaign_managers_403f60f` (`user_id`),
  CONSTRAINT `campaign_id_refs_id_14a43a05` FOREIGN KEY (`campaign_id`) REFERENCES `core_campaign` (`id`),
  CONSTRAINT `user_id_refs_id_4ec5c04d` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_campaign_managers`
--

LOCK TABLES `core_campaign_managers` WRITE;
/*!40000 ALTER TABLE `core_campaign_managers` DISABLE KEYS */;
INSERT INTO `core_campaign_managers` VALUES (1,52,3);
/*!40000 ALTER TABLE `core_campaign_managers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_campaignaction`
--

DROP TABLE IF EXISTS `core_campaignaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_campaignaction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime NOT NULL,
  `type` varchar(15) NOT NULL,
  `comment` longtext,
  `campaign_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_campaignaction_702b94e6` (`campaign_id`),
  CONSTRAINT `campaign_id_refs_id_6277a473` FOREIGN KEY (`campaign_id`) REFERENCES `core_campaign` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_campaignaction`
--

LOCK TABLES `core_campaignaction` WRITE;
/*!40000 ALTER TABLE `core_campaignaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_campaignaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_celerytask`
--

DROP TABLE IF EXISTS `core_celerytask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_celerytask` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL DEFAULT '2011-11-21 11:28:24',
  `task_id` varchar(255) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `description` varchar(2048) DEFAULT NULL,
  `function_name` varchar(1024) NOT NULL,
  `function_args` int(11) DEFAULT NULL,
  `active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `core_celerytask_403f60f` (`user_id`),
  CONSTRAINT `user_id_refs_id_5724e0a2` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_celerytask`
--

LOCK TABLES `core_celerytask` WRITE;
/*!40000 ALTER TABLE `core_celerytask` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_celerytask` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_claim`
--

DROP TABLE IF EXISTS `core_claim`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_claim` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `rights_holder_id` int(11) NOT NULL,
  `work_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `status` varchar(7) NOT NULL DEFAULT 'pending',
  PRIMARY KEY (`id`),
  KEY `core_claim_3369ff6d` (`rights_holder_id`),
  KEY `core_claim_50cafa73` (`work_id`),
  KEY `core_claim_403f60f` (`user_id`),
  CONSTRAINT `rights_holder_id_refs_id_3813725f` FOREIGN KEY (`rights_holder_id`) REFERENCES `core_rightsholder` (`id`),
  CONSTRAINT `user_id_refs_id_4daf1126` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `work_id_refs_id_6b9b1671` FOREIGN KEY (`work_id`) REFERENCES `core_work` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_claim`
--

LOCK TABLES `core_claim` WRITE;
/*!40000 ALTER TABLE `core_claim` DISABLE KEYS */;
INSERT INTO `core_claim` VALUES (1,'2016-04-21 12:52:01',1,52,3,'active');
/*!40000 ALTER TABLE `core_claim` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_ebook`
--

DROP TABLE IF EXISTS `core_ebook`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_ebook` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `format` varchar(25) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `provider` varchar(255) NOT NULL,
  `rights` varchar(255) DEFAULT NULL,
  `edition_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `download_count` int(11) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `filesize` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `core_ebook_16ab133f` (`edition_id`),
  KEY `core_ebook_403f60f` (`user_id`),
  KEY `core_ebook_61b47ff4` (`rights`),
  KEY `core_ebook_63b5ea41` (`created`),
  CONSTRAINT `edition_id_refs_id_3bf4f8d1` FOREIGN KEY (`edition_id`) REFERENCES `core_edition` (`id`),
  CONSTRAINT `user_id_refs_id_38a40e3c` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_ebook`
--

LOCK TABLES `core_ebook` WRITE;
/*!40000 ALTER TABLE `core_ebook` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_ebook` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_ebookfile`
--

DROP TABLE IF EXISTS `core_ebookfile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_ebookfile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `file` varchar(100) NOT NULL,
  `format` varchar(25) NOT NULL,
  `edition_id` int(11) NOT NULL,
  `created` datetime NOT NULL,
  `asking` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_ebookfile_ae2379d4` (`edition_id`),
  CONSTRAINT `edition_id_refs_id_713d0b56` FOREIGN KEY (`edition_id`) REFERENCES `core_edition` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_ebookfile`
--

LOCK TABLES `core_ebookfile` WRITE;
/*!40000 ALTER TABLE `core_ebookfile` DISABLE KEYS */;
INSERT INTO `core_ebookfile` VALUES (1,'ebf/04058a8899b146388dbb7043d58bc727.epub','epub',52,'2016-04-21 12:54:21',0);
/*!40000 ALTER TABLE `core_ebookfile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_edition`
--

DROP TABLE IF EXISTS `core_edition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_edition` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `title` varchar(1000) NOT NULL,
  `publication_date` varchar(50) DEFAULT NULL,
  `work_id` int(11) DEFAULT NULL,
  `cover_image` varchar(200) DEFAULT NULL,
  `unglued` tinyint(1) NOT NULL,
  `publisher_name_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `core_edition_50cafa73` (`work_id`),
  KEY `core_edition_20a64221` (`publisher_name_id`),
  KEY `core_edition_ecf7107f` (`publication_date`),
  CONSTRAINT `publisher_name_id_refs_id_bf28ca9b` FOREIGN KEY (`publisher_name_id`) REFERENCES `core_publishername` (`id`),
  CONSTRAINT `work_id_refs_id_441b48fb` FOREIGN KEY (`work_id`) REFERENCES `core_work` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_edition`
--

LOCK TABLES `core_edition` WRITE;
/*!40000 ALTER TABLE `core_edition` DISABLE KEYS */;
INSERT INTO `core_edition` VALUES (1,'2012-03-02 13:02:58','Labyrinths','1964',1,NULL,0,1),(2,'2012-03-02 13:02:59','Nightwood','2006-09-01',2,NULL,0,2),(3,'2012-03-02 13:03:00','The making of Americans','1995',3,NULL,0,3),(4,'2012-03-02 13:03:00','Paris was yesterday','1988',4,NULL,0,4),(5,'2012-03-02 13:03:01','Shakespeare and Company','1991-10-01',5,NULL,0,5),(6,'2012-03-02 13:03:01','The letters of Sylvia Beach','2010-06-30',6,NULL,0,6),(7,'2012-03-02 13:03:02','Merchants of Culture','2010-09-22',7,NULL,0,7),(8,'2012-03-02 13:03:03','Sylvia Beach and the Lost Generation','1985',8,NULL,0,8),(9,'2012-03-02 13:03:04','Hons and Rebels','2004-09-30',9,NULL,0,9),(10,'2012-03-02 13:03:05','The Friendly Persuasion','2003-09-15',10,NULL,0,4),(11,'2012-03-02 13:03:06','The Massacre at Fall Creek','1986-09-02',11,NULL,0,4),(12,'2012-03-02 13:03:06','Woman Said Yes','1986-09-02',12,NULL,0,4),(13,'2012-03-02 13:03:07','Collected Stories of Jessamyn West','1987-11-23',13,NULL,0,4),(14,'2012-03-02 13:03:07','Father, Son & Co.','2000-02-29',14,NULL,0,10),(15,'2012-03-02 13:03:08','Dhalgren','2001-05-15',15,NULL,0,11),(16,'2012-03-02 13:03:09','Emotional intelligence','2006-09-26',16,NULL,0,10),(17,'2012-03-02 13:03:09','Working with emotional intelligence','1998',17,NULL,0,10),(18,'2012-03-02 13:03:10','Vital lies, simple truths','1996-05-01',18,NULL,0,12),(19,'2012-03-02 13:03:10','What to Expect When You\'re Expecting','2008-04-10',19,NULL,0,13),(20,'2012-03-02 13:03:11','60 ways to relieve stress in 60 seconds','1993',20,NULL,0,14),(21,'2012-03-02 13:03:12','Seeing is forgetting the name of the thing one sees','2008',21,NULL,0,15),(22,'2012-03-02 13:03:12','Vermeer in Bosnia: selected writings','2004',22,NULL,0,NULL),(23,'2012-03-02 13:03:13','The Last Place on Earth','1999',23,NULL,0,16),(24,'2012-03-02 13:03:13','Revolution 2:0','2012-01-17',24,NULL,0,17),(25,'2012-03-02 13:03:14','The Longest Winter','2010-05-01',25,NULL,0,18),(26,'2012-03-02 13:03:15','Selected Letters of Dashiell Hammett: 1921-1960','2002-04-25',26,NULL,0,19),(27,'2012-03-02 13:03:15','The group','1991-09-01',27,NULL,0,4),(28,'2012-03-02 13:03:16','The madwoman in the attic','1979',28,NULL,0,NULL),(29,'2012-03-02 13:03:17','A literature of their own','1977',29,NULL,0,20),(30,'2012-03-02 13:03:17','Love like gumbo','1997-11',30,NULL,0,21),(31,'2012-03-02 13:03:18','Maugham','1980',31,NULL,0,22),(32,'2012-03-02 13:03:19','My battle of Algiers','2005',32,NULL,0,23),(33,'2012-03-02 13:03:19','Dispatches','2009-02-17',33,NULL,0,24),(34,'2012-03-02 13:03:20','Why Viet Nam?','1982-09-30',34,NULL,0,15),(35,'2012-03-02 13:03:20','Quantum electronics','1989-01-17',35,NULL,0,25),(36,'2012-03-02 13:03:21','Solid state physics','1976',36,NULL,0,NULL),(37,'2012-03-02 13:03:22','Animal architects','2007-03-12',37,NULL,0,26),(38,'2012-03-02 13:03:22','Animal Architects','2012-03-06',38,NULL,0,NULL),(39,'2012-03-02 13:03:23','The animal mind','1999',39,NULL,0,27),(40,'2012-03-02 13:03:24','The remarkable life of William Beebe','2006-09-25',40,NULL,0,28),(41,'2012-03-02 13:03:25','Ethology','1982',41,NULL,0,8),(42,'2012-03-02 13:03:26','Here am I--where are you?','1991-10-01',42,NULL,0,29),(43,'2012-03-02 13:03:26','Rainbows End','2007-04-03',43,NULL,0,30),(44,'2012-03-02 13:03:27','Neuromancer','2000-07-01',44,NULL,0,31),(45,'2012-03-02 13:03:28','The seven-per-cent solution','1993-09-23',45,NULL,0,8),(46,'2012-03-02 13:03:29','Seeing voices','2000-11-28',46,NULL,0,11),(47,'2012-03-02 13:03:29','The left hand of darkness','1969',47,NULL,0,NULL),(48,'2012-03-02 13:03:30','A Wizard of Earthsea','2004-09-28',48,NULL,0,32),(49,'2012-03-02 13:03:31','Four Ways to Forgiveness','2004-12-14',49,NULL,0,33),(50,'2012-03-02 13:03:31','The Spy Who Came in from the Cold','2005-09-01',50,NULL,0,34),(51,'2012-03-02 13:03:32','Call for the Dead','2002-02-01',51,NULL,0,35),(52,'2016-04-21 12:52:01','Pro Web 2.0 Mashups','2008-04-25',52,NULL,0,36),(53,'2016-08-25 18:30:45','Moby-dick','2011',53,NULL,0,NULL);
/*!40000 ALTER TABLE `core_edition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_gift`
--

DROP TABLE IF EXISTS `core_gift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_gift` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `acq_id` int(11) NOT NULL,
  `to` varchar(75) NOT NULL,
  `giver_id` int(11) NOT NULL,
  `message` longtext NOT NULL,
  `used` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `core_gift_a5043c7f` (`acq_id`),
  KEY `core_gift_26b81902` (`giver_id`),
  CONSTRAINT `acq_id_refs_id_d14024bc` FOREIGN KEY (`acq_id`) REFERENCES `core_acq` (`id`),
  CONSTRAINT `giver_id_refs_id_3923974c` FOREIGN KEY (`giver_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_gift`
--

LOCK TABLES `core_gift` WRITE;
/*!40000 ALTER TABLE `core_gift` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_gift` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_hold`
--

DROP TABLE IF EXISTS `core_hold`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_hold` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `work_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `library_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_hold_dfb5c784` (`work_id`),
  KEY `core_hold_6340c63c` (`user_id`),
  KEY `core_hold_98518bb8` (`library_id`),
  CONSTRAINT `library_id_refs_id_1a8bfc55` FOREIGN KEY (`library_id`) REFERENCES `libraryauth_library` (`id`),
  CONSTRAINT `user_id_refs_id_a35378a3` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `work_id_refs_id_45ad2d6d` FOREIGN KEY (`work_id`) REFERENCES `core_work` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_hold`
--

LOCK TABLES `core_hold` WRITE;
/*!40000 ALTER TABLE `core_hold` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_hold` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_identifier`
--

DROP TABLE IF EXISTS `core_identifier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_identifier` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(4) CHARACTER SET utf8 NOT NULL,
  `value` varchar(250) COLLATE utf8_bin NOT NULL,
  `work_id` int(11) NOT NULL,
  `edition_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_identifier_type_73c65d72_uniq` (`type`,`value`),
  KEY `core_identifier_50cafa73` (`work_id`),
  KEY `core_identifier_16ab133f` (`edition_id`),
  CONSTRAINT `edition_id_refs_id_3ef1dd63` FOREIGN KEY (`edition_id`) REFERENCES `core_edition` (`id`),
  CONSTRAINT `work_id_refs_id_173a5601` FOREIGN KEY (`work_id`) REFERENCES `core_work` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_identifier`
--

LOCK TABLES `core_identifier` WRITE;
/*!40000 ALTER TABLE `core_identifier` DISABLE KEYS */;
INSERT INTO `core_identifier` VALUES (1,'goog','wtPxGztYx-UC',1,1),(2,'isbn','9780811216999',1,1),(3,'goog','v6iZL5n5cLwC',2,2),(4,'isbn','9780811216715',2,2),(5,'goog','cRMjLSUJB-8C',3,3),(6,'isbn','9781564780881',3,3),(7,'goog','ceZXAAAAYAAJ',4,4),(8,'isbn','9780156709903',4,4),(9,'goog','fEmg2ZGajiYC',5,5),(10,'isbn','9780803260979',5,5),(11,'goog','m8bro-kUA0IC',6,6),(12,'isbn','9780231145367',6,6),(13,'goog','8-G_hkBRHxgC',7,7),(14,'isbn','9780745647869',7,7),(15,'goog','Zpu5_c2o-2IC',8,8),(16,'isbn','9780393302318',8,8),(17,'goog','pzeGAQAACAAJ',9,9),(18,'isbn','9781590171103',9,9),(19,'goog','bw8OALeRZwwC',10,10),(20,'isbn','9780156029094',10,10),(21,'goog','_jlyGQAACAAJ',11,11),(22,'isbn','9780156576819',11,11),(23,'goog','P_JLcAcNXoUC',12,12),(24,'isbn','9780156982900',12,12),(25,'goog','Jj8e9sCds-kC',13,13),(26,'isbn','9780156189798',13,13),(27,'goog','S2ViPwAACAAJ',14,14),(28,'isbn','9780553380835',14,14),(29,'goog','NaZoQgAACAAJ',15,15),(30,'isbn','9780375706684',15,15),(31,'goog','c3PDO7jKTJMC',16,16),(32,'isbn','9780553804911',16,16),(33,'goog','0Zzcd8k6TNEC',17,17),(34,'isbn','9780553378580',17,17),(35,'goog','R_jF5yUjYSEC',18,18),(36,'isbn','9780684831077',18,18),(37,'goog','ASPVDMmiLZkC',19,19),(38,'isbn','9780761148579',19,19),(39,'goog','DKo0GcKyxXQC',20,20),(40,'isbn','9781563053382',20,20),(41,'goog','kWjtMAAACAAJ',21,21),(42,'isbn','9780520256095',21,21),(43,'goog','meDISAAACAAJ',22,22),(44,'isbn','9780679442707',22,22),(45,'goog','NpXhF9snsA4C',23,23),(46,'isbn','9780375754746',23,23),(47,'goog','JSdstTJWNq4C',24,24),(48,'isbn','9780547773988',24,24),(49,'goog','b1IQPQAACAAJ',25,25),(50,'isbn','9780719595806',25,25),(51,'goog','hr9AnjP9i3MC',26,26),(52,'isbn','9781582432106',26,26),(53,'goog','rXNMFENTY2wC',27,27),(54,'isbn','9780156372084',27,27),(55,'goog','O2GyQgAACAAJ',28,28),(56,'isbn','9780300022865',28,28),(57,'goog','baRxQgAACAAJ',29,29),(58,'isbn','9780691063188',29,29),(59,'goog','bmOxAAAAIAAJ',30,30),(60,'isbn','9780940242753',30,30),(61,'goog','fKrVrGbsQt8C',31,31),(62,'isbn','9780671240776',31,31),(63,'goog','JHV_QgAACAAJ',32,32),(64,'isbn','9780060852245',32,32),(65,'goog','QOI_jmwFxGkC',33,33),(66,'isbn','9780307270801',33,33),(67,'goog','e8EpyU3-2zwC',34,34),(68,'isbn','9780520047839',34,34),(69,'goog','UTWg1VIkNuMC',35,35),(70,'isbn','9780471609971',35,35),(71,'goog','oXIfAQAAMAAJ',36,36),(72,'isbn','9780030839931',36,36),(73,'goog','J02DI6uG8jgC',37,37),(74,'isbn','9780465027828',37,37),(75,'goog','Qc5kXwAACAAJ',38,38),(76,'isbn','9780465028382',38,38),(77,'goog','xTBUOgAACAAJ',39,39),(78,'isbn','9780716760351',39,39),(79,'goog','XCNOPgAACAAJ',40,40),(80,'isbn','9781597261074',40,40),(81,'goog','Wh2IAAAAIAAJ',41,41),(82,'isbn','9780393014884',41,41),(83,'goog','KAuKQgAACAAJ',42,42),(84,'isbn','9780151400560',42,42),(85,'goog','rF9zs9TRakYC',43,43),(86,'isbn','9780812536362',43,43),(87,'goog','IDFfMPW32hQC',44,44),(88,'isbn','9780441007462',44,44),(89,'goog','a_FQYUt63WEC',45,45),(90,'isbn','9780393311198',45,45),(91,'goog','0S4rLyDj8AgC',46,46),(92,'isbn','9780375704079',46,46),(93,'goog','tIuFygAACAAJ',47,47),(94,'isbn','9780760759141',47,47),(95,'goog','hwlCPgAACAAJ',48,48),(96,'isbn','9780553383041',48,48),(97,'goog','yj1NPgAACAAJ',49,49),(98,'isbn','9780060760298',49,49),(99,'goog','o6o7PgAACAAJ',50,50),(100,'isbn','9780802714541',50,50),(101,'goog','oY0NdYZbG2kC',51,51),(102,'isbn','9780743431675',51,51),(103,'goog','eGdLbRZ5AX0C',52,52),(104,'isbn','9781430202868',52,52),(105,'goog','2qzZoAEACAAJ',53,53),(106,'isbn','9787500129875',53,53);
/*!40000 ALTER TABLE `core_identifier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_libpref`
--

DROP TABLE IF EXISTS `core_libpref`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_libpref` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `marc_link_target` varchar(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_id_refs_id_7519465d` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_libpref`
--

LOCK TABLES `core_libpref` WRITE;
/*!40000 ALTER TABLE `core_libpref` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_libpref` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_offer`
--

DROP TABLE IF EXISTS `core_offer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_offer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `work_id` int(11) NOT NULL,
  `price` decimal(6,2) DEFAULT NULL,
  `license` smallint(5) unsigned NOT NULL,
  `active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_offer_dfb5c784` (`work_id`),
  CONSTRAINT `work_id_refs_id_f0db7ea9` FOREIGN KEY (`work_id`) REFERENCES `core_work` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_offer`
--

LOCK TABLES `core_offer` WRITE;
/*!40000 ALTER TABLE `core_offer` DISABLE KEYS */;
INSERT INTO `core_offer` VALUES (1,52,10.00,1,1),(2,52,10.00,2,1);
/*!40000 ALTER TABLE `core_offer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_premium`
--

DROP TABLE IF EXISTS `core_premium`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_premium` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `type` varchar(2) NOT NULL,
  `campaign_id` int(11) DEFAULT NULL,
  `amount` decimal(10,0) NOT NULL,
  `description` longtext,
  `limit` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_premium_702b94e6` (`campaign_id`),
  CONSTRAINT `campaign_id_refs_id_512fbe69` FOREIGN KEY (`campaign_id`) REFERENCES `core_campaign` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=151 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_premium`
--

LOCK TABLES `core_premium` WRITE;
/*!40000 ALTER TABLE `core_premium` DISABLE KEYS */;
INSERT INTO `core_premium` VALUES (1,'2011-11-17 22:03:37','00',NULL,1,'The unglued ebook delivered to your inbox.',0),(2,'2011-11-17 22:03:37','00',NULL,25,'Your username under \"supporters\" in the acknowledgements section.',0),(3,'2011-11-17 22:03:37','00',NULL,50,'Your username and profile URL of your choice under \"benefactors\"',0),(4,'2011-11-17 22:03:37','00',NULL,100,'Your username, profile URL, and profile tagline under \"bibliophiles\"',0),(150,'2011-11-17 22:03:37','00',NULL,0,'No premium, thanks!  I just want to help unglue.',0);
/*!40000 ALTER TABLE `core_premium` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_press`
--

DROP TABLE IF EXISTS `core_press`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_press` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(200) NOT NULL,
  `title` varchar(140) NOT NULL,
  `source` varchar(140) NOT NULL,
  `date` date NOT NULL,
  `language` varchar(20) NOT NULL,
  `highlight` tinyint(1) NOT NULL,
  `note` varchar(140) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_press_eeede814` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_press`
--

LOCK TABLES `core_press` WRITE;
/*!40000 ALTER TABLE `core_press` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_press` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_publisher`
--

DROP TABLE IF EXISTS `core_publisher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_publisher` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `name_id` int(11) NOT NULL,
  `url` varchar(1024) DEFAULT NULL,
  `logo_url` varchar(1024) DEFAULT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  KEY `core_publisher_4da47e07` (`name_id`),
  CONSTRAINT `name_id_refs_id_5d27f2fb` FOREIGN KEY (`name_id`) REFERENCES `core_publishername` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_publisher`
--

LOCK TABLES `core_publisher` WRITE;
/*!40000 ALTER TABLE `core_publisher` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_publisher` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_publishername`
--

DROP TABLE IF EXISTS `core_publishername`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_publishername` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `publisher_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_publishername_name_6705ace0ea367f07_uniq` (`name`),
  KEY `core_publishername_81b79144` (`publisher_id`),
  CONSTRAINT `publisher_id_refs_id_e6ee33d3` FOREIGN KEY (`publisher_id`) REFERENCES `core_publisher` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_publishername`
--

LOCK TABLES `core_publishername` WRITE;
/*!40000 ALTER TABLE `core_publishername` DISABLE KEYS */;
INSERT INTO `core_publishername` VALUES (1,'New Directions Publishing Corporation',NULL),(2,'New Directions',NULL),(3,'Dalkey Archive Pr',NULL),(4,'Mariner Books',NULL),(5,'Bison Books',NULL),(6,'Columbia Univ Pr',NULL),(7,'Polity Pr',NULL),(8,'W. W. Norton & Company',NULL),(9,'NYRB Classics',NULL),(10,'Bantam',NULL),(11,'Vintage',NULL),(12,'Simon and Schuster',NULL),(13,'Workman Pub Co',NULL),(14,'Workman Publishing',NULL),(15,'Univ of California Pr',NULL),(16,'Random House of Canada',NULL),(17,'Houghton Mifflin Harcourt (HMH)',NULL),(18,'John Murray Pubs Ltd',NULL),(19,'Counterpoint Press',NULL),(20,'Princeton Univ Pr',NULL),(21,'Fjord Pr',NULL),(22,'Simon & Schuster',NULL),(23,'Smithsonian',NULL),(24,'Everyman\'s Library',NULL),(25,'John Wiley & Sons Inc',NULL),(26,'Basic Books (AZ)',NULL),(27,'W H Freeman & Co',NULL),(28,'Island Pr',NULL),(29,'Harcourt',NULL),(30,'Tor Science Fiction',NULL),(31,'Ace Trade',NULL),(32,'Spectra',NULL),(33,'Harper Perennial',NULL),(34,'Walker & Co',NULL),(35,'Scribner',NULL),(36,'Apress',NULL);
/*!40000 ALTER TABLE `core_publishername` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_relation`
--

DROP TABLE IF EXISTS `core_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_relation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(3) NOT NULL,
  `name` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_relation`
--

LOCK TABLES `core_relation` WRITE;
/*!40000 ALTER TABLE `core_relation` DISABLE KEYS */;
INSERT INTO `core_relation` VALUES (1,'aut','Author'),(2,'arr','arranger'),(3,'prf','performer'),(4,'art','artist'),(5,'lbt','librettist'),(6,'ann','annotator'),(7,'prt','printer'),(8,'edt','editor'),(9,'adp','adapter'),(10,'aui','author_of_introduction'),(11,'res','researcher'),(12,'dub','dubious_author'),(13,'clb','collaborator'),(14,'cnd','conductor'),(15,'aft','author_of_afterword'),(16,'oth','other_contributor'),(17,'pht','photographer'),(18,'cmm','commentator'),(19,'trl','translator'),(20,'egr','engineer'),(21,'ill','illustrator'),(22,'ctb','contributor'),(23,'pbl','publisher_contributor'),(24,'unk','unknown_contributor'),(25,'com','compiler'),(26,'trc','transcriber'),(27,'cmp','composer');
/*!40000 ALTER TABLE `core_relation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_rightsholder`
--

DROP TABLE IF EXISTS `core_rightsholder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_rightsholder` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `email` varchar(100) NOT NULL,
  `rights_holder_name` varchar(100) NOT NULL,
  `owner_id` int(11) NOT NULL,
  `can_sell` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_rightsholder_5d52dd10` (`owner_id`),
  CONSTRAINT `owner_id_refs_id_4785c9f2` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_rightsholder`
--

LOCK TABLES `core_rightsholder` WRITE;
/*!40000 ALTER TABLE `core_rightsholder` DISABLE KEYS */;
INSERT INTO `core_rightsholder` VALUES (1,'2016-04-21 12:52:00','raymond.yee@dataunbound.com','RY Inc',3,1);
/*!40000 ALTER TABLE `core_rightsholder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_subject`
--

DROP TABLE IF EXISTS `core_subject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_subject` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `name` varchar(200) NOT NULL,
  `is_visible` tinyint(1) NOT NULL,
  `authority` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_subject_name_uniq` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_subject`
--

LOCK TABLES `core_subject` WRITE;
/*!40000 ALTER TABLE `core_subject` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_subject` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_subject_works`
--

DROP TABLE IF EXISTS `core_subject_works`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_subject_works` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `work_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_subject_works_subject_id_7fafdf11_uniq` (`subject_id`,`work_id`),
  KEY `core_subject_works_638462f1` (`subject_id`),
  KEY `core_subject_works_50cafa73` (`work_id`),
  CONSTRAINT `subject_id_refs_id_1f2e6ee2` FOREIGN KEY (`subject_id`) REFERENCES `core_subject` (`id`),
  CONSTRAINT `work_id_refs_id_23534694` FOREIGN KEY (`work_id`) REFERENCES `core_work` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_subject_works`
--

LOCK TABLES `core_subject_works` WRITE;
/*!40000 ALTER TABLE `core_subject_works` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_subject_works` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_userprofile`
--

DROP TABLE IF EXISTS `core_userprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_userprofile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `tagline` varchar(140) NOT NULL,
  `pic_url` varchar(200) NOT NULL,
  `home_url` varchar(200) NOT NULL,
  `twitter_id` varchar(15) NOT NULL,
  `facebook_id` bigint(20) DEFAULT NULL,
  `librarything_id` varchar(31) NOT NULL,
  `goodreads_user_id` varchar(32) DEFAULT NULL,
  `goodreads_user_name` varchar(200) DEFAULT NULL,
  `goodreads_auth_token` longtext,
  `goodreads_auth_secret` longtext,
  `goodreads_user_link` varchar(200) DEFAULT NULL,
  `avatar_source` smallint(5) unsigned DEFAULT NULL,
  `kindle_email` varchar(254) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_id_refs_id_55007184` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_userprofile`
--

LOCK TABLES `core_userprofile` WRITE;
/*!40000 ALTER TABLE `core_userprofile` DISABLE KEYS */;
INSERT INTO `core_userprofile` VALUES (1,'2012-03-02 13:17:24',1,'','','','',NULL,'',NULL,NULL,NULL,NULL,NULL,NULL,''),(2,'2012-03-02 13:21:21',2,'','','','',NULL,'',NULL,NULL,NULL,NULL,NULL,NULL,''),(3,'2012-03-13 19:11:32',3,'','','','',NULL,'',NULL,NULL,NULL,NULL,NULL,NULL,''),(4,'2012-05-09 14:34:52',4,'','','','',NULL,'',NULL,NULL,NULL,NULL,NULL,NULL,''),(5,'2016-04-21 12:52:00',5,'','','','',NULL,'',NULL,NULL,NULL,NULL,NULL,4,''),(6,'2016-04-21 12:52:01',6,'','','','',NULL,'',NULL,NULL,NULL,NULL,NULL,4,''),(7,'2016-04-21 12:54:55',7,'','','','',NULL,'',NULL,NULL,NULL,NULL,NULL,4,'');
/*!40000 ALTER TABLE `core_userprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_userprofile_badges`
--

DROP TABLE IF EXISTS `core_userprofile_badges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_userprofile_badges` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userprofile_id` int(11) NOT NULL,
  `badge_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_userprofile_badges_userprofile_id_bf97d4699fcdd09_uniq` (`userprofile_id`,`badge_id`),
  KEY `core_userprofile_badges_1be1924f` (`userprofile_id`),
  KEY `core_userprofile_badges_540bf7e8` (`badge_id`),
  CONSTRAINT `badge_id_refs_id_2a419c3a` FOREIGN KEY (`badge_id`) REFERENCES `core_badge` (`id`),
  CONSTRAINT `userprofile_id_refs_id_f21bd339` FOREIGN KEY (`userprofile_id`) REFERENCES `core_userprofile` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_userprofile_badges`
--

LOCK TABLES `core_userprofile_badges` WRITE;
/*!40000 ALTER TABLE `core_userprofile_badges` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_userprofile_badges` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_waswork`
--

DROP TABLE IF EXISTS `core_waswork`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_waswork` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `work_id` int(11) NOT NULL,
  `was` int(11) NOT NULL,
  `moved` datetime NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `was` (`was`),
  KEY `core_waswork_50cafa73` (`work_id`),
  KEY `core_waswork_403f60f` (`user_id`),
  CONSTRAINT `user_id_refs_id_6b2efc3c` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `work_id_refs_id_1a094c05` FOREIGN KEY (`work_id`) REFERENCES `core_work` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_waswork`
--

LOCK TABLES `core_waswork` WRITE;
/*!40000 ALTER TABLE `core_waswork` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_waswork` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_wishlist`
--

DROP TABLE IF EXISTS `core_wishlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_wishlist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_id_refs_id_109b8800` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_wishlist`
--

LOCK TABLES `core_wishlist` WRITE;
/*!40000 ALTER TABLE `core_wishlist` DISABLE KEYS */;
INSERT INTO `core_wishlist` VALUES (1,'2012-03-02 13:17:24',1),(2,'2012-03-02 13:21:21',2),(3,'2012-03-13 19:11:32',3),(4,'2012-05-09 14:34:52',4),(5,'2016-04-21 12:52:00',5),(6,'2016-04-21 12:52:01',6),(7,'2016-04-21 12:54:55',7);
/*!40000 ALTER TABLE `core_wishlist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_wishlist_works`
--

DROP TABLE IF EXISTS `core_wishlist_works`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_wishlist_works` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `wishlist_id` int(11) NOT NULL,
  `work_id` int(11) NOT NULL,
  `created` datetime NOT NULL,
  `source` varchar(15) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_wishlist_works_wishlist_id_7ac55979_uniq` (`wishlist_id`,`work_id`),
  KEY `core_wishlist_works_515c0ae1` (`wishlist_id`),
  KEY `core_wishlist_works_50cafa73` (`work_id`),
  KEY `core_wishlist_works_a34b03a6` (`source`),
  KEY `core_wishlist_works_63b5ea41` (`created`),
  CONSTRAINT `wishlist_id_refs_id_29586d26` FOREIGN KEY (`wishlist_id`) REFERENCES `core_wishlist` (`id`),
  CONSTRAINT `work_id_refs_id_117c3b10` FOREIGN KEY (`work_id`) REFERENCES `core_work` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_wishlist_works`
--

LOCK TABLES `core_wishlist_works` WRITE;
/*!40000 ALTER TABLE `core_wishlist_works` DISABLE KEYS */;
INSERT INTO `core_wishlist_works` VALUES (1,3,48,'2016-04-21 12:53:54','pledging'),(2,7,52,'2016-04-21 12:54:59','pledging');
/*!40000 ALTER TABLE `core_wishlist_works` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_work`
--

DROP TABLE IF EXISTS `core_work`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_work` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime NOT NULL,
  `title` varchar(1000) NOT NULL,
  `language` varchar(5) NOT NULL,
  `openlibrary_lookup` datetime DEFAULT NULL,
  `num_wishes` int(11) NOT NULL,
  `description` longtext,
  `selected_edition_id` int(11) DEFAULT NULL,
  `featured` datetime DEFAULT NULL,
  `is_free` tinyint(1) NOT NULL,
  `publication_range` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `core_work_988f77ad` (`num_wishes`),
  KEY `core_work_65e6e3c2` (`selected_edition_id`),
  KEY `core_work_784efa61` (`language`),
  KEY `core_work_63b5ea41` (`created`),
  KEY `core_work_9ce45497` (`featured`),
  CONSTRAINT `selected_edition_id_refs_id_1b248dcc` FOREIGN KEY (`selected_edition_id`) REFERENCES `core_edition` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_work`
--

LOCK TABLES `core_work` WRITE;
/*!40000 ALTER TABLE `core_work` DISABLE KEYS */;
INSERT INTO `core_work` VALUES (1,'2012-03-02 13:02:58','Labyrinths','en',NULL,0,'A new edition of a classic work by a late forefront Argentinean writer features the 1964 augmented original text and is complemented by a biographical essay, a tribute to the writer\'s body of work, and a chronology of his life. Reprint.',NULL,NULL,0,NULL),(2,'2012-03-02 13:02:59','Nightwood','en',NULL,0,'The fiery and enigmatic masterpiece-one of the greatest novels of the Modernist era.',NULL,NULL,0,NULL),(3,'2012-03-02 13:02:59','The making of Americans','en',NULL,0,'\"Essential for all literature collections . . . Several of Stein\'s titles returned to print in 1995, but none more important than The Making of Americans.\"-Library Journal',NULL,NULL,0,NULL),(4,'2012-03-02 13:03:00','Paris was yesterday','en',NULL,0,'A portrait of French life and culture in the late twenties and thirties is presented in excerpts from the author\'s column in the New Yorker',NULL,NULL,0,NULL),(5,'2012-03-02 13:03:01','Shakespeare and Company','en',NULL,0,'Sylvia Beach was intimately acquainted with the expatriate and visiting writers of the Lost Generation, a label that she never accepted. Like moths of great promise, they were drawn to her well-lighted bookstore and warm hearth on the Left Bank. Shakespeare and Company evokes the zeitgeist of an era through its revealing glimpses of James Joyce, Ernest Hemingway, Scott Fitzgerald, Sherwood Anderson, Andre Gide, Ezra Pound, Gertrude Stein, Alice B. Toklas, D. H. Lawrence, and others already famous or soon to be. In his introduction to this new edition, James Laughlin recalls his friendship with Sylvia Beach. Like her bookstore, his publishing house, New Directions, is considered a cultural touchstone.',NULL,NULL,0,NULL),(6,'2012-03-02 13:03:01','The letters of Sylvia Beach','en',NULL,0,'The first collection of selected correspondence of the noted bookseller and publisher includes letters to Ernest Hemingway, James Joyce, William Carlos Williams, Marianne Moore, and Gertrude Stein.',NULL,NULL,0,NULL),(7,'2012-03-02 13:03:02','Merchants of Culture','en',NULL,0,'The world of book publishing is going through turbulent times. For nearly five centuries the methods and practices of book publishing remained largely unchanged, but at the dawn of the 21st century the industry finds itself faced with perhaps the greatest challenges since Gutenberg. A combination of economic pressures and technological change is forcing publishers to alter their practices and think hard about the future of the book in the digital age. In this book - the first major study of trade publishing for more than 30 years - Thompson situates the current challenges facing the industry in an historical context, analyzing the transformation of trade publishing in the United States and Britain since the 1960s. He gives a detailed account of how the world of trade publishing really works, dissecting the roles of publishers, agents and booksellers and showing how their practices are shaped by a field that has a distinctive structure and dynamic. Against this backdrop Thompson analyzes the impact of the digital revolution on book publishing and examines the pressures that are reshaping the field of trade publishing today.',NULL,NULL,0,NULL),(8,'2012-03-02 13:03:03','Sylvia Beach and the Lost Generation','en',NULL,0,'Making use of the author\'s access to the Beach family papers, this account chronicles the literary circle that gathered at Beach\'s Paris book shop',NULL,NULL,0,NULL),(9,'2012-03-02 13:03:04','Hons and Rebels','en',NULL,0,'In this \"wonderfully funny and very poignant\" (Philip Toynbee) autobiography, Mitford offers a fascinating study of the unusual upbringing of her famous family.',NULL,NULL,0,NULL),(10,'2012-03-02 13:03:05','The Friendly Persuasion','en',NULL,0,'Jess Birdwell, a Quaker with a fondness for fast horses, his wife Eliza, and their children struggle to deal with the turmoil, violence, and challenges of the Civil War in their own way. Reprint. 12,500 first printing.',NULL,NULL,0,NULL),(11,'2012-03-02 13:03:06','The Massacre at Fall Creek','en',NULL,0,'Narrates the reactions of a small 1824 Indian settlement to the capture, trial, conviction and execution of five white men for the premeditated murder of nine peaceful men, women and children of the Seneca tribe',11,NULL,0,NULL),(12,'2012-03-02 13:03:06','Woman Said Yes','en',NULL,0,'The noted American writer celebrates her mother\'s life-affirming values and behavior and records their influence on her own fight with tuberculosis and her sister\'s courageous response to the onslaught of incurable spinal cancer',NULL,NULL,0,NULL),(13,'2012-03-02 13:03:07','Collected Stories of Jessamyn West','en',NULL,0,'Thirty-eight stories depict suspense, romance, obsession, the supernatural, adolescence, and sexual relationships',NULL,NULL,0,NULL),(14,'2012-03-02 13:03:07','Father, Son & Co.','en',NULL,0,'The former CEO for IBM details his father\'s initial creation of the company, IBM\'s first foray into computers, and his own career with the company.',NULL,NULL,0,NULL),(15,'2012-03-02 13:03:08','Dhalgren','en',NULL,0,'Journeying to the central United States city of Bellona, where all have fled save madmen and criminals, a poet and adventurer known only as the Kid wonders at the strange portents that appear in the city\'s cloud-covered sky.',15,NULL,0,NULL),(16,'2012-03-02 13:03:09','Emotional intelligence','en',NULL,0,'Everyone knows that high IQ is no guarantee of success, happiness, or virtue, but until Emotional Intelligence, we could only guess why. Daniel Goleman\'s brilliant report from the frontiers of psychology and neuroscience offers startling new insight into our \"two minds\"—the rational and the emotional—and how they together shape our destiny. Through vivid examples, Goleman delineates the five crucial skills of emotional intelligence, and shows how they determine our success in relationships, work, and even our physical well-being. What emerges is an entirely new way to talk about being smart. The best news is that \"emotional literacy\" is not fixed early in life. Every parent, every teacher, every business leader, and everyone interested in a more civil society, has a stake in this compelling vision of human possibility. From the Trade Paperback edition.',NULL,NULL,0,NULL),(17,'2012-03-02 13:03:09','Working with emotional intelligence','en',NULL,0,'The author of the breakthrough bestseller Emotional Intelligence demonstrates that emotional and social skills are more important than IQ in determining an individual\'s success in today\'s business world. Reprint.',17,NULL,0,NULL),(18,'2012-03-02 13:03:10','Vital lies, simple truths','en',NULL,0,'A penetrating analysis of the dark corners of human deception, enlivened by intriguing case histories and experiments.',NULL,NULL,0,NULL),(19,'2012-03-02 13:03:10','What to Expect When You\'re Expecting','en',NULL,0,'Cuts through the confusion surrounding pregnancy and birth by debunking dozens of myths that mislead parents, offering explanations of medical terms, and covering a variety of issues including prenatal care, birth defects, and amniocentesis.',NULL,NULL,0,NULL),(20,'2012-03-02 13:03:11','60 ways to relieve stress in 60 seconds','en',NULL,0,'Suggests ways to alleviate stress through brief activities designed to relieve tension and distract one from the daily routine',20,NULL,0,'1993'),(21,'2012-03-02 13:03:11','Seeing is forgetting the name of the thing one sees','en',NULL,0,'When this book first appeared in 1982, it introduced readers to Robert Irwin, the Los Angeles artist \"who one day got hooked on his own curiosity and decided to live it.\" Now expanded to include six additional chapters and twenty-four pages of color plates,Seeing Is Forgetting the Name of the Thing One Seeschronicles three decades of conversation between Lawrence Weschler and light and space master Irwin. It surveys many of Irwin\'s site-conditioned projects--in particular the Central Gardens at the Getty Museum (the subject of an epic battle with the site\'s principal architect, Richard Meier) and the design that transformed an abandoned Hudson Valley factory into Dia\'s new Beacon campus--enhancing what many had already considered the best book ever on an artist.',NULL,NULL,0,NULL),(22,'2012-03-02 13:03:12','Vermeer in Bosnia: selected writings','en',NULL,0,'',22,NULL,0,NULL),(23,'2012-03-02 13:03:13','The Last Place on Earth','en',NULL,0,'Recounts the efforts of Scott, a British explorer, and Amundsen, a Norwegian, to be the first to reach the South Pole',NULL,NULL,0,NULL),(24,'2012-03-02 13:03:13','Revolution 2:0','en',NULL,0,'A key figure behind the Egyptian uprising in January 2011, which resulted in the ousting of President Mubarak tells the riveting inside story of what happened and presents lessons on how to unleash the power of crowds to create political change. 200,000 first printing.',24,NULL,0,NULL),(25,'2012-03-02 13:03:14','The Longest Winter','en',NULL,0,'Their tents were torn, their food was nearly finished, and the ship had failed to pick them up as planned. Gale-force winds blew, bitter with the cold of approaching winter. Stranded and desperate, the six men of the Northern Party faced disaster. Searching out a snow drift, they burrowed inside. Lieutenant Victor Campbell drew a line across the floor in the gloom to establish naval order: three officers on one side, the three seamen on the other. A birthday was celebrated with a carefully hoarded biscuit and they sang hymns every Sunday, so what kept these men going? Circumstances forced them closer together, their roles blurred and a shared sense of reality emerged. This mutual suffering made them indivisible and somehow they made it through the longest winter. To the south, the men waiting at headquarters knew that the Polar Party must be dead and hoped that another six men would not be added to the death toll. Working from expedition diaries, journals, and letters written by expedition members, Meredith Hooper tells the intensely human story of Scott’s other expedition.',25,NULL,0,NULL),(26,'2012-03-02 13:03:15','Selected Letters of Dashiell Hammett: 1921-1960','en',NULL,0,'A collection of letters--to friends, lovers, family, and colleagues--by the legendary crime writer reveals the man behind the author as he discusses the craft of writing, his personal life, and his literary creations, Sam Spade and Nick and Nora Charles. Reprint. 25,000 first printing.',26,NULL,0,NULL),(27,'2012-03-02 13:03:15','The group','en',NULL,0,'Depicts the experiences of eight Vassar graduates during the thirty years following their graduation',27,NULL,0,NULL),(28,'2012-03-02 13:03:16','The madwoman in the attic','en',NULL,0,'',NULL,NULL,0,NULL),(29,'2012-03-02 13:03:17','A literature of their own','en',NULL,0,'Describes the female literary tradition in the English novel and the social backgrounds of the women who composed it',NULL,NULL,0,NULL),(30,'2012-03-02 13:03:17','Love like gumbo','en',NULL,0,'In South Central Los Angeles in 1978, Grace Broussard, the youngest member of a Creole family transplanted from Louisiana, seeks to distance herself from her family through a ten point plan designed to shock them, but the ghost of her father interferes wi',NULL,NULL,0,NULL),(31,'2012-03-02 13:03:18','Maugham','en',NULL,0,'',NULL,NULL,0,NULL),(32,'2012-03-02 13:03:19','My battle of Algiers','en',NULL,0,'A personal account of his experiences as a young officer during the horrors of the Algerian War in the 1950s by a Pulitzer Prize-winning historian details the horrific events of the conflict, which included bombings, assassinations, torture, and other unimaginable barbarities. 25,000 first printing.',32,NULL,0,NULL),(33,'2012-03-02 13:03:19','Dispatches','en',NULL,0,'(Book Jacket Status: Jacketed) Written on the front lines in Vietnam, Dispatches became an immediate classic of war reportage when it was published in 1977. From its terrifying opening pages to its final eloquent words, Dispatches makes us see, in unforgettable and unflinching detail, the chaos and fervor of the war and the surreal insanity of life in that singular combat zone. Michael Herr’s unsparing, unorthodox retellings of the day-to-day events in Vietnam take on the force of poetry, rendering clarity from one of the most incomprehensible and nightmarish events of our time. Dispatches is among the most blistering and compassionate accounts of war in our literature.',NULL,NULL,0,NULL),(34,'2012-03-02 13:03:20','Why Viet Nam?','en',NULL,0,'Identifies the origins and causes of U.S. involvement in Viet Nam, beginning with the surrender of Japanese forces in Indochina in 1945',34,NULL,0,NULL),(35,'2012-03-02 13:03:20','Quantum electronics','en',NULL,0,'This Third Edition of the popular text, while retaining nearly all the material of the previous edition, incorporates material on important new developments in lasers and quantum electronics. Covers phase-conjugate optics and its myriad applications, the long wavelength quaternary semiconductor laser, and our deepened understanding of the physics of semiconductor lasers--especially that applying to their current modulations and limiting bandwidth, laser arrays and the related concept of supermodes, quantum well semiconductor lasers, the role of phase amplitude coupling in laser noise, and free-electron lasers. In addition, the chapters on laser noise and third-order nonlinear effects have been extensively revised.',35,NULL,0,NULL),(36,'2012-03-02 13:03:21','Solid state physics','en',NULL,0,'',36,NULL,0,NULL),(37,'2012-03-02 13:03:22','Animal architects','en',NULL,0,'Looks at why animals build, explores the building processes of a variety of species, and discusses how a study of animal building behavior can provides an understanding of the human mind.',NULL,NULL,0,NULL),(38,'2012-03-02 13:03:22','Animal Architects','en',NULL,0,'From two of the world’s most distinguished experts in animal behavior, a radical, creative, and accessible new approach to understanding animal minds through the structures they build',NULL,NULL,0,NULL),(39,'2012-03-02 13:03:23','The animal mind','en',NULL,0,'In this book, the author\'s examine the evidence of the innate & learned mental capacities of animals, including perceptual processing, & the most advanced forms of thought & language. Includes a final chapter on that animal we look at in the mirror each morning. Throughout their book, the authors challenge our basic assumptions about animal cognition & ask \"are animals capable of thought & awareness?\"',39,NULL,0,NULL),(40,'2012-03-02 13:03:24','The remarkable life of William Beebe','en',NULL,0,'When William Beebe needed to know what was going on in the depths of the ocean, he had himself lowered a half-mile down in a four-foot steel sphere to see-five times deeper than anyone had ever gone in the 1930s. When he wanted to trace the evolution of pheasants in 1910, he trekked on foot through the mountains and jungles of the Far East to locate every species. To decipher the complex ecology of the tropics, he studied the interactions of every creature and plant in a small area from the top down, setting the emerging field of tropical ecology into dynamic motion. William Beebe\'s curiosity about the natural world was insatiable, and he did nothing by halves. As the first biographer to see the letters and private journals Beebe kept from 1887 until his death in 1962, science writer Carol Grant Gould brings the life and times of this groundbreaking scientist and explorer compellingly to light. From the Galapagos Islands to the jungles of British Guiana, from the Bronx Zoo to the deep seas, Beebe\'s biography is a riveting adventure. A best-selling author in his own time, Beebe was a fearless explorer and thoughtful scientist who put his life on the line in pursuit of knowledge. The unique glimpses he provided into the complex web of interactions that keeps the earth alive and breathing have inspired generations of conservationists and ecologists. This exciting biography of a great naturalist brings William Beebe at last to the recognition he deserves.',NULL,NULL,0,NULL),(41,'2012-03-02 13:03:25','Ethology','en',NULL,0,'A history of ethology explains the neural and evolutionary mechanisms of behavior, the relationship of behavior to genetics, and the social and complex behavior of animals and humans',41,NULL,0,NULL),(42,'2012-03-02 13:03:26','Here am I--where are you?','en',NULL,0,'Documents the social conduct of wild geese with anecdotes about specific geese who take on strikingly human characteristics',42,NULL,0,NULL),(43,'2012-03-02 13:03:26','Rainbows End','en',NULL,0,'In a near-future western civilization that is threatened by corruptive practices within its technologically advanced information networks, a recovered Alzheimer\'s victim, his military son and daughter-in-law, and his middle school-age granddaughter are caught up in a dangerous maelstrom beyond their worst imaginings. By the Hugo Award-winning author of A Deepness in the Sky. Reprint.',NULL,NULL,0,NULL),(44,'2012-03-02 13:03:27','Neuromancer','en',NULL,0,'Case, a burned-out computer whiz, is asked to steal a security code that is locked in the most heavily guarded databank in the solar system, in a new edition of the influential Hugo, Nebula, and Philip K. Dick Award winner. Reprint.',44,NULL,0,NULL),(45,'2012-03-02 13:03:28','The seven-per-cent solution','en',NULL,0,'Back in print to tie-in with The Canary Trainer, this \"rediscovered\" Sherlock Holmes adventure recounts the unique collaboration of Holmes and Sigmund Freud in the solution of a mystery on which the lives of millions may depend.',NULL,NULL,0,NULL),(46,'2012-03-02 13:03:29','Seeing voices','en',NULL,0,'A renowned neurologist investigates the world of the deaf, examining their past and present treatment at the hands of society, and assesses the value and significance of sign language. Reprint. 12,500 first printing.',46,NULL,0,NULL),(47,'2012-03-02 13:03:29','The left hand of darkness','en',NULL,0,'The Terrans have sent a landing party to Gethan and what they find are a people outside their understanding, who do not see one another as men or women, strong or weak.',47,NULL,0,NULL),(48,'2012-03-02 13:03:30','A Wizard of Earthsea','en',NULL,1,'Ursula K. Le Guin\'s first book of Earthsea--a treasured classic novel of wisdom and wizardry--introduces a boy who grows to manhood while attempting to subdue the evil he unleashed on the world as an apprentice to the Master Wizard. Young Adult.',48,NULL,0,'2004'),(49,'2012-03-02 13:03:31','Four Ways to Forgiveness','en',NULL,0,'Four interconnected novellas follow the stories of disgraced revolutionary Abberkam, callow \"space brat\" Solly, haughty soldier Teyeo, and historian and exile Havzhiva as each battles for duty and freedom, in a collection set in the author\'s Hainish universe. Reprint.',NULL,NULL,0,NULL),(50,'2012-03-02 13:03:31','The Spy Who Came in from the Cold','en',NULL,0,'Secret agent Alec Leamas is on a dangerous mission in East Berlin, but he has doubts about the organization he serves.',NULL,NULL,0,NULL),(51,'2012-03-02 13:03:32','Call for the Dead','en',NULL,0,'Featuring an introduction by the author, this is a paperback reissue of the debut novel that introduces one of the most popular characters in espionage fiction: George Smiley.',51,NULL,0,NULL),(52,'2016-04-21 12:52:01','Pro Web 2.0 Mashups','en',NULL,1,'',52,NULL,0,'2008'),(53,'2016-08-25 18:30:45','Moby-dick','zh-CN',NULL,0,'',NULL,NULL,0,NULL);
/*!40000 ALTER TABLE `core_work` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `distro_deposit`
--

DROP TABLE IF EXISTS `distro_deposit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `distro_deposit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_id` int(11) NOT NULL,
  `isbn` varchar(13) NOT NULL,
  `format` varchar(30) NOT NULL,
  `updated` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `distro_deposit_70bfdfd1` (`target_id`),
  CONSTRAINT `target_id_refs_id_814d0105` FOREIGN KEY (`target_id`) REFERENCES `distro_target` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `distro_deposit`
--

LOCK TABLES `distro_deposit` WRITE;
/*!40000 ALTER TABLE `distro_deposit` DISABLE KEYS */;
/*!40000 ALTER TABLE `distro_deposit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `distro_format`
--

DROP TABLE IF EXISTS `distro_format`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `distro_format` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `distro_format`
--

LOCK TABLES `distro_format` WRITE;
/*!40000 ALTER TABLE `distro_format` DISABLE KEYS */;
/*!40000 ALTER TABLE `distro_format` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `distro_target`
--

DROP TABLE IF EXISTS `distro_target`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `distro_target` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `host` varchar(60) NOT NULL,
  `pw` varchar(30) NOT NULL,
  `user` varchar(30) NOT NULL,
  `protocol` varchar(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `distro_target`
--

LOCK TABLES `distro_target` WRITE;
/*!40000 ALTER TABLE `distro_target` DISABLE KEYS */;
/*!40000 ALTER TABLE `distro_target` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `distro_target_formats`
--

DROP TABLE IF EXISTS `distro_target_formats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `distro_target_formats` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_id` int(11) NOT NULL,
  `format_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `distro_target_formats_target_id_6635b7be763e51f3_uniq` (`target_id`,`format_id`),
  KEY `distro_target_formats_70bfdfd1` (`target_id`),
  KEY `distro_target_formats_cdb01fd0` (`format_id`),
  CONSTRAINT `format_id_refs_id_31712f41` FOREIGN KEY (`format_id`) REFERENCES `distro_format` (`id`),
  CONSTRAINT `target_id_refs_id_e11c34a1` FOREIGN KEY (`target_id`) REFERENCES `distro_target` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `distro_target_formats`
--

LOCK TABLES `distro_target_formats` WRITE;
/*!40000 ALTER TABLE `distro_target_formats` DISABLE KEYS */;
/*!40000 ALTER TABLE `distro_target_formats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_403f60f` (`user_id`),
  KEY `django_admin_log_1bb8f392` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_288599e6` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `user_id_refs_id_c8665aa` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_comment_flags`
--

DROP TABLE IF EXISTS `django_comment_flags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_comment_flags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `comment_id` int(11) NOT NULL,
  `flag` varchar(30) NOT NULL,
  `flag_date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`comment_id`,`flag`),
  KEY `django_comment_flags_403f60f` (`user_id`),
  KEY `django_comment_flags_64c238ac` (`comment_id`),
  KEY `django_comment_flags_111c90f9` (`flag`),
  CONSTRAINT `comment_id_refs_id_373a05f7` FOREIGN KEY (`comment_id`) REFERENCES `django_comments` (`id`),
  CONSTRAINT `user_id_refs_id_603c4dcb` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_comment_flags`
--

LOCK TABLES `django_comment_flags` WRITE;
/*!40000 ALTER TABLE `django_comment_flags` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_comment_flags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_comments`
--

DROP TABLE IF EXISTS `django_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content_type_id` int(11) NOT NULL,
  `object_pk` longtext NOT NULL,
  `site_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `user_name` varchar(50) NOT NULL,
  `user_email` varchar(254) NOT NULL,
  `user_url` varchar(200) NOT NULL,
  `comment` longtext NOT NULL,
  `submit_date` datetime NOT NULL,
  `ip_address` char(15) DEFAULT NULL,
  `is_public` tinyint(1) NOT NULL,
  `is_removed` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_comments_1bb8f392` (`content_type_id`),
  KEY `django_comments_6223029` (`site_id`),
  KEY `django_comments_403f60f` (`user_id`),
  KEY `django_comments_submit_date_12b4e916a37b5c82_uniq` (`submit_date`),
  CONSTRAINT `content_type_id_refs_id_d5868a5` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `site_id_refs_id_7248df08` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`),
  CONSTRAINT `user_id_refs_id_7e9ddfef` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_comments`
--

LOCK TABLES `django_comments` WRITE;
/*!40000 ALTER TABLE `django_comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (15,'admin','logentry'),(55,'api','allowedrepo'),(2,'auth','group'),(4,'auth','message'),(1,'auth','permission'),(3,'auth','user'),(56,'bisac','bisacheading'),(75,'booxtream','boox'),(8,'comments','comment'),(9,'comments','commentflag'),(5,'contenttypes','contenttype'),(58,'core','acq'),(26,'core','author'),(65,'core','badge'),(23,'core','campaign'),(22,'core','campaignaction'),(18,'core','celerytask'),(19,'core','claim'),(30,'core','ebook'),(64,'core','ebookfile'),(28,'core','edition'),(68,'core','gift'),(59,'core','hold'),(24,'core','identifier'),(52,'core','key'),(66,'core','libpref'),(57,'core','offer'),(21,'core','premium'),(67,'core','press'),(62,'core','publisher'),(63,'core','publishername'),(60,'core','relation'),(61,'core','relator'),(20,'core','rightsholder'),(27,'core','subject'),(33,'core','userprofile'),(29,'core','waswork'),(32,'core','wishes'),(31,'core','wishlist'),(25,'core','work'),(100,'default','association'),(101,'default','code'),(99,'default','nonce'),(98,'default','usersocialauth'),(83,'distro','deposit'),(84,'distro','format'),(82,'distro','target'),(96,'django_comments','comment'),(97,'django_comments','commentflag'),(42,'djcelery','crontabschedule'),(41,'djcelery','intervalschedule'),(44,'djcelery','periodictask'),(43,'djcelery','periodictasks'),(39,'djcelery','taskmeta'),(40,'djcelery','tasksetmeta'),(46,'djcelery','taskstate'),(45,'djcelery','workerstate'),(17,'djkombu','message'),(16,'djkombu','queue'),(53,'email_change','emailchangerequest'),(77,'libraryauth','block'),(78,'libraryauth','cardpattern'),(80,'libraryauth','emailpattern'),(76,'libraryauth','library'),(79,'libraryauth','libraryuser'),(69,'marc','marcrecord'),(49,'notification','notice'),(50,'notification','noticequeuebatch'),(48,'notification','noticesetting'),(47,'notification','noticetype'),(51,'notification','observeditem'),(81,'page','page'),(73,'payment','account'),(71,'payment','credit'),(70,'payment','creditlog'),(35,'payment','paymentresponse'),(36,'payment','receiver'),(72,'payment','sent'),(34,'payment','transaction'),(95,'questionnaire','answer'),(94,'questionnaire','choice'),(89,'questionnaire','dbstylesheet'),(86,'questionnaire','globalstyles'),(88,'questionnaire','landing'),(93,'questionnaire','question'),(87,'questionnaire','questionnaire'),(90,'questionnaire','questionset'),(91,'questionnaire','runinfo'),(92,'questionnaire','runinfohistory'),(85,'questionnaire','subject'),(11,'registration','registrationprofile'),(6,'sessions','session'),(7,'sites','site'),(14,'social_auth','association'),(13,'social_auth','nonce'),(12,'social_auth','usersocialauth'),(10,'south','migrationhistory'),(74,'survey','landing'),(37,'tastypie','apiaccess'),(38,'tastypie','apikey'),(54,'thumbnail','kvstore');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2016-08-25 18:36:34.677196'),(2,'contenttypes','0002_remove_content_type_name','2016-08-25 18:36:34.807504'),(3,'auth','0001_initial','2016-08-25 18:36:34.837576'),(4,'auth','0002_alter_permission_name_max_length','2016-08-25 18:36:34.873400'),(5,'auth','0003_alter_user_email_max_length','2016-08-25 18:36:34.907162'),(6,'auth','0004_alter_user_username_opts','2016-08-25 18:36:34.929398'),(7,'auth','0005_alter_user_last_login_null','2016-08-25 18:36:34.964408'),(8,'auth','0006_require_contenttypes_0002','2016-08-25 18:36:34.970225'),(9,'default','0001_initial','2016-08-25 18:36:36.950265'),(10,'default','0002_add_related_name','2016-08-25 18:36:38.812421'),(11,'libraryauth','0001_initial','2016-08-25 18:36:43.172322'),(12,'core','0001_initial','2016-08-25 18:36:43.176659'),(13,'booxtream','0001_initial','2016-08-25 18:36:43.180107'),(14,'core','0002_auto_20160722_1716','2016-08-25 18:36:43.183419'),(15,'libraryauth','0002_auto_20160727_2214','2016-08-25 18:36:45.098603'),(16,'admin','0001_initial','2016-08-25 18:36:57.171290'),(17,'api','0001_initial','2016-08-25 18:36:57.182368'),(18,'bisac','0001_initial','2016-08-25 18:36:57.194697'),(19,'default','0003_alter_email_max_length','2016-08-25 18:36:57.222018'),(20,'default','0004_auto_20160423_0400','2016-08-25 18:36:57.450414'),(21,'distro','0001_initial','2016-08-25 18:36:57.491408'),(22,'sites','0001_initial','2016-08-25 18:36:57.510773'),(23,'django_comments','0001_initial','2016-08-25 18:36:57.873996'),(24,'django_comments','0002_update_user_email_field_length','2016-08-25 18:36:58.015672'),(25,'django_comments','0003_add_submit_date_index','2016-08-25 18:36:58.160824'),(26,'djcelery','0001_initial','2016-08-25 18:36:58.228225'),(27,'email_change','0001_initial','2016-08-25 18:36:58.365658'),(28,'marc','0001_initial','2016-08-25 18:36:58.498155'),(29,'notification','0001_initial','2016-08-25 18:36:59.596413'),(30,'payment','0001_initial','2016-08-25 18:37:00.578111'),(31,'questionnaire','0001_initial','2016-08-25 18:37:04.011806'),(32,'registration','0001_initial','2016-08-25 18:37:04.225662'),(33,'sessions','0001_initial','2016-08-25 18:37:04.252763'),(34,'tastypie','0001_initial','2016-08-25 18:37:04.496005');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_3da3d3d8` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('175e0d57a0f0f04156a8eb4316e47a2e','YzgwYWRiYTBhZTAzYjA3OWMzMzE2ZjEyYzY2ZTVhYjI3Zjg2ZjgxNzqAAn1xAVUKdGVzdGNvb2tp\nZXECVQZ3b3JrZWRxA3Mu\n','2012-05-23 14:35:23'),('18fbcae31f97186e23df72668c871697','OTU5N2MyYWZlMGEyZjQwMDlhNzhlZjQ2NzQ4ODY0YzM1MTFhN2VjNzqAAn1xAShVBm9wZW5pZH1V\nDV9hdXRoX3VzZXJfaWRxAooBAlUec29jaWFsX2F1dGhfbGFzdF9sb2dpbl9iYWNrZW5kcQNVBmdv\nb2dsZXEEVQp0ZXN0Y29va2llVQZ3b3JrZWRVEl9hdXRoX3VzZXJfYmFja2VuZHEFVSlzb2NpYWxf\nYXV0aC5iYWNrZW5kcy5nb29nbGUuR29vZ2xlQmFja2VuZHEGdS4=\n','2012-03-16 13:22:05'),('2a5014c0ae1d8df35a7ba7894737898c','OTIyOTliMjkxYjQ2NDE3ZGZiNmFhNThhZDUxN2U0NmZiNWY1YjJjMzqAAn1xAShVBm9wZW5pZH1V\nDV9hdXRoX3VzZXJfaWRxAooBAVUec29jaWFsX2F1dGhfbGFzdF9sb2dpbl9iYWNrZW5kcQNVBmdv\nb2dsZXEEVQp0ZXN0Y29va2llVQZ3b3JrZWRVEl9hdXRoX3VzZXJfYmFja2VuZHEFVSlzb2NpYWxf\nYXV0aC5iYWNrZW5kcy5nb29nbGUuR29vZ2xlQmFja2VuZHEGdS4=\n','2012-03-16 13:17:24'),('6b425a32ff36427157428901ed0fafef','ZjNmNDhkYjNjMGM3M2UxNDRiNmM4MjY5ZTJhNGIxMTg2NjQxNmU3MzqAAn1xAS4=\n','2012-05-23 14:32:04'),('7612afkcttd12na2oik9aia4n89i0nps','NzlkZGFlNmM5MTBiYjU3YWE1M2NkNTdmODU4ZDE0NTIyMTc2MzllZjp7ImFtb3VudCI6MTAwMCwiX2F1dGhfdXNlcl9pZCI6NywiX2F1dGhfdXNlcl9iYWNrZW5kIjoic29jaWFsLmJhY2tlbmRzLmdvb2dsZS5Hb29nbGVPQXV0aDIifQ==','2016-06-02 12:54:59'),('7cflps1w2jxbsb7ni1lqudhv22zffwp2','M2I4NmEwYmM3ZTg0NmUyZDQwN2FjOWI1MmExNGI4ZDdlMTg0NTU0YTp7fQ==','2016-06-02 12:52:25'),('98a8c3b6c6bab3895a9d13fcb377c8f0','ZjNmNDhkYjNjMGM3M2UxNDRiNmM4MjY5ZTJhNGIxMTg2NjQxNmU3MzqAAn1xAS4=\n','2012-05-23 14:02:27'),('b5529b6ff89dd2e5662a34eb3b134085','MTEyNjAwNGQxNjY0YTY3ODI5N2UxODk0M2M2NmY4Y2Q2ODJiNDJkNDqAAn1xAS4=\n','2012-05-17 14:12:51'),('ceafe30bfba3d5669ac52b8958471207','MTEyNjAwNGQxNjY0YTY3ODI5N2UxODk0M2M2NmY4Y2Q2ODJiNDJkNDqAAn1xAS4=\n','2012-05-21 19:50:58'),('d588298920bbe41b16ba73a0dd2d6f2a','OGIzMmE3NTU0NTViODBhYWEwZGNhZTlkMDkyZWE2MDAwN2FhYTgwNTqAAn1xAShVEl9hdXRoX3Vz\nZXJfYmFja2VuZHECVSlkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHED\nVQ1fYXV0aF91c2VyX2lkcQSKAQN1Lg==\n','2012-03-27 19:14:27');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES (1,'unglue.it','unglue.it'),(2,'please.unglueit.com','unglue.it development'),(3,'localhost:8000','unglue.it local development'),(4,'ry-dev.unglueit.com','ry-dev development'),(5,'just.unglue.it','unglue.it staging');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `djcelery_crontabschedule`
--

DROP TABLE IF EXISTS `djcelery_crontabschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `djcelery_crontabschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `minute` varchar(64) NOT NULL DEFAULT '*',
  `hour` varchar(64) NOT NULL DEFAULT '*',
  `day_of_week` varchar(64) NOT NULL DEFAULT '*',
  `day_of_month` varchar(64) NOT NULL,
  `month_of_year` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `djcelery_crontabschedule`
--

LOCK TABLES `djcelery_crontabschedule` WRITE;
/*!40000 ALTER TABLE `djcelery_crontabschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `djcelery_crontabschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `djcelery_intervalschedule`
--

DROP TABLE IF EXISTS `djcelery_intervalschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `djcelery_intervalschedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `every` int(11) NOT NULL,
  `period` varchar(24) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `djcelery_intervalschedule`
--

LOCK TABLES `djcelery_intervalschedule` WRITE;
/*!40000 ALTER TABLE `djcelery_intervalschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `djcelery_intervalschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `djcelery_periodictask`
--

DROP TABLE IF EXISTS `djcelery_periodictask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `djcelery_periodictask` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `task` varchar(200) NOT NULL,
  `interval_id` int(11) DEFAULT NULL,
  `crontab_id` int(11) DEFAULT NULL,
  `args` longtext NOT NULL,
  `kwargs` longtext NOT NULL,
  `queue` varchar(200) DEFAULT NULL,
  `exchange` varchar(200) DEFAULT NULL,
  `routing_key` varchar(200) DEFAULT NULL,
  `expires` datetime DEFAULT NULL,
  `enabled` tinyint(1) NOT NULL DEFAULT '1',
  `last_run_at` datetime DEFAULT NULL,
  `total_run_count` int(10) unsigned NOT NULL DEFAULT '0',
  `date_changed` datetime NOT NULL,
  `description` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `djcelery_periodictask_17d2d99d` (`interval_id`),
  KEY `djcelery_periodictask_7aa5fda` (`crontab_id`),
  CONSTRAINT `crontab_id_refs_id_1400a18c` FOREIGN KEY (`crontab_id`) REFERENCES `djcelery_crontabschedule` (`id`),
  CONSTRAINT `interval_id_refs_id_dfabcb7` FOREIGN KEY (`interval_id`) REFERENCES `djcelery_intervalschedule` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `djcelery_periodictask`
--

LOCK TABLES `djcelery_periodictask` WRITE;
/*!40000 ALTER TABLE `djcelery_periodictask` DISABLE KEYS */;
/*!40000 ALTER TABLE `djcelery_periodictask` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `djcelery_periodictasks`
--

DROP TABLE IF EXISTS `djcelery_periodictasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `djcelery_periodictasks` (
  `ident` smallint(6) NOT NULL DEFAULT '1',
  `last_update` datetime NOT NULL,
  PRIMARY KEY (`ident`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `djcelery_periodictasks`
--

LOCK TABLES `djcelery_periodictasks` WRITE;
/*!40000 ALTER TABLE `djcelery_periodictasks` DISABLE KEYS */;
/*!40000 ALTER TABLE `djcelery_periodictasks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `djcelery_taskstate`
--

DROP TABLE IF EXISTS `djcelery_taskstate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `djcelery_taskstate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `state` varchar(64) NOT NULL,
  `task_id` varchar(36) NOT NULL,
  `name` varchar(200) DEFAULT NULL,
  `tstamp` datetime NOT NULL,
  `args` longtext,
  `kwargs` longtext,
  `eta` datetime DEFAULT NULL,
  `expires` datetime DEFAULT NULL,
  `result` longtext,
  `traceback` longtext,
  `runtime` double DEFAULT NULL,
  `retries` int(11) NOT NULL DEFAULT '0',
  `worker_id` int(11) DEFAULT NULL,
  `hidden` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_id` (`task_id`),
  KEY `djcelery_taskstate_355bfc27` (`state`),
  KEY `djcelery_taskstate_52094d6e` (`name`),
  KEY `djcelery_taskstate_f459b00` (`tstamp`),
  KEY `djcelery_taskstate_20fc5b84` (`worker_id`),
  KEY `djcelery_taskstate_c91f1bf` (`hidden`),
  CONSTRAINT `worker_id_refs_id_4e3453a` FOREIGN KEY (`worker_id`) REFERENCES `djcelery_workerstate` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `djcelery_taskstate`
--

LOCK TABLES `djcelery_taskstate` WRITE;
/*!40000 ALTER TABLE `djcelery_taskstate` DISABLE KEYS */;
/*!40000 ALTER TABLE `djcelery_taskstate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `djcelery_workerstate`
--

DROP TABLE IF EXISTS `djcelery_workerstate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `djcelery_workerstate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hostname` varchar(255) NOT NULL,
  `last_heartbeat` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hostname` (`hostname`),
  KEY `djcelery_workerstate_1475381c` (`last_heartbeat`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `djcelery_workerstate`
--

LOCK TABLES `djcelery_workerstate` WRITE;
/*!40000 ALTER TABLE `djcelery_workerstate` DISABLE KEYS */;
/*!40000 ALTER TABLE `djcelery_workerstate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `djkombu_message`
--

DROP TABLE IF EXISTS `djkombu_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `djkombu_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `visible` tinyint(1) NOT NULL,
  `sent_at` datetime DEFAULT NULL,
  `payload` longtext NOT NULL,
  `queue_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `djkombu_message_16b2708a` (`visible`),
  KEY `djkombu_message_774871ae` (`sent_at`),
  KEY `djkombu_message_1e72d6b8` (`queue_id`),
  CONSTRAINT `queue_id_refs_id_13f7812d` FOREIGN KEY (`queue_id`) REFERENCES `djkombu_queue` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `djkombu_message`
--

LOCK TABLES `djkombu_message` WRITE;
/*!40000 ALTER TABLE `djkombu_message` DISABLE KEYS */;
INSERT INTO `djkombu_message` VALUES (1,1,'2016-04-21 12:52:01','{\"body\": \"gAJ9cQEoVQdleHBpcmVzcQJOVQN1dGNxA4hVBGFyZ3NxBGNkamFuZ28uZGIubW9kZWxzLmJhc2UKbW9kZWxfdW5waWNrbGUKcQVYBAAAAGNvcmVxBlULVXNlclByb2ZpbGVxB4ZdY2RqYW5nby5kYi5tb2RlbHMuYmFzZQpzaW1wbGVfY2xhc3NfZmFjdG9yeQpxCIdScQl9cQooVRVnb29kcmVhZHNfYXV0aF9zZWNyZXRxC05VB3VzZXJfaWRxDIoBBlUTZ29vZHJlYWRzX3VzZXJfbmFtZXENTlUHY3JlYXRlZHEOY2RhdGV0aW1lCmRhdGV0aW1lCnEPVQoH4AQVDDQBBRsLhVJxEFUNYXZhdGFyX3NvdXJjZXERSwRVB3RhZ2xpbmVxElgAAAAAVQtfdXNlcl9jYWNoZXETaAVYBAAAAGF1dGhxFFUEVXNlcnEVhl1oCIdScRZ9cRcoVQh1c2VybmFtZXEYVRBSaWdodHNhdFVuZ2x1ZWl0cRlVCmZpcnN0X25hbWVxGlgAAAAAVQlsYXN0X25hbWVxG1gAAAAAVQ5fcHJvZmlsZV9jYWNoZXEcaAlVCWlzX2FjdGl2ZXEdiFUGX3N0YXRlcR5jZGphbmdvLmRiLm1vZGVscy5iYXNlCk1vZGVsU3RhdGUKcR8pgXEgfXEhKFUGYWRkaW5ncSKJVQJkYnEjVQdkZWZhdWx0cSR1YlUNX2NyZWRpdF9jYWNoZXElaAVYBwAAAHBheW1lbnRxJlUGQ3JlZGl0cSeGXWgIh1JxKH1xKShoDIoBBlUHcGxlZGdlZHEqY2RlY2ltYWwKRGVjaW1hbApxK1UEMC4wMIVScSxoHmgfKYFxLX1xLihoIoloI2gkdWJVAmlkcS+KAQZVDWxhc3RfYWN0aXZpdHlxMGgPVQoH4AQVDDQBBReDhVJxMVUHYmFsYW5jZXEyaCtVBDAuMDCFUnEzaBNoFnViVQVlbWFpbHE0VRJyaWdodHNAZ2x1ZWphci5jb21xNVUMaXNfc3VwZXJ1c2VycTaJVQhpc19zdGFmZnE3iVUKbGFzdF9sb2dpbnE4aA9VCgfgBBUMNAEFE7+FUnE5VQ9fd2lzaGxpc3RfY2FjaGVxOmgFWAQAAABjb3JlcTtVCFdpc2hsaXN0cTyGXWgIh1JxPX1xPihoDIoBBmgTaBZoHmgfKYFxP31xQChoIoloI2gkdWJoL4oBBmgOaA9VCgfgBBUMNAEFGR2FUnFBdWJVCHBhc3N3b3JkcUJYAAAAAGgvigEGVQtkYXRlX2pvaW5lZHFDaA9VCgfgBBUMNAEFE+GFUnFEdWJoHmgfKYFxRX1xRihoIoloI2gkdWJVCnR3aXR0ZXJfaWRxR1gAAAAAVQdwaWNfdXJscUhYAAAAAFURZ29vZHJlYWRzX3VzZXJfaWRxSU5VDGtpbmRsZV9lbWFpbHFKWAAAAABVE2dvb2RyZWFkc191c2VyX2xpbmtxS05VC2ZhY2Vib29rX2lkcUxOVQ9saWJyYXJ5dGhpbmdfaWRxTVgAAAAAVQhob21lX3VybHFOWAAAAABVFGdvb2RyZWFkc19hdXRoX3Rva2VucU9OaC+KAQZ1YoVxUFUFY2hvcmRxUU5VCWNhbGxiYWNrc3FSTlUIZXJyYmFja3NxU05VB3Rhc2tzZXRxVE5oL1UkYTgzOWVkMmUtYjg1MS00ZDE0LWIzMDUtNWRmMDllZGRkNzdhcVVVB3JldHJpZXNxVksAVQR0YXNrcVdVJHJlZ2x1aXQuY29yZS50YXNrcy5tbF9zdWJzY3JpYmVfdGFza3FYVQl0aW1lbGltaXRxWU5OhlUDZXRhcVpOVQZrd2FyZ3NxW31xXHUu\", \"headers\": {}, \"content-type\": \"application/x-python-serialize\", \"properties\": {\"body_encoding\": \"base64\", \"correlation_id\": \"a839ed2e-b851-4d14-b305-5df09eddd77a\", \"reply_to\": \"ae4b079a-eb04-391a-84f4-74bb685d562e\", \"delivery_info\": {\"priority\": 0, \"routing_key\": \"celery\", \"exchange\": \"celery\"}, \"delivery_mode\": 2, \"delivery_tag\": \"ff70da6e-82b1-40c5-a582-e8812aef8b68\"}, \"content-encoding\": \"binary\"}',1),(2,1,'2016-04-21 12:53:54','{\"body\": \"gAJ9cQEoVQdleHBpcmVzcQJOVQN1dGNxA4hVBGFyZ3NxBF1xBVUFY2hvcmRxBk5VCWNhbGxiYWNrc3EHTlUIZXJyYmFja3NxCE5VB3Rhc2tzZXRxCU5VAmlkcQpVJDdmZmVjNWNmLTNkMWEtNDBjOS05ZDFlLWViZTczOGRmNGM1MnELVQdyZXRyaWVzcQxLAFUEdGFza3ENVSVyZWdsdWl0LmNvcmUudGFza3MuZW1pdF9ub3RpZmljYXRpb25zcQ5VCXRpbWVsaW1pdHEPTk6GVQNldGFxEE5VBmt3YXJnc3ERfXESdS4=\", \"headers\": {}, \"content-type\": \"application/x-python-serialize\", \"properties\": {\"body_encoding\": \"base64\", \"correlation_id\": \"7ffec5cf-3d1a-40c9-9d1e-ebe738df4c52\", \"reply_to\": \"b4c6b5fe-2354-30ec-9a2a-658503c69395\", \"delivery_info\": {\"priority\": 0, \"routing_key\": \"celery\", \"exchange\": \"celery\"}, \"delivery_mode\": 2, \"delivery_tag\": \"7084743a-04ab-4631-93dd-b030a58b4ca0\"}, \"content-encoding\": \"binary\"}',1),(3,1,'2016-04-21 12:53:55','{\"body\": \"gAJ9cQEoVQdleHBpcmVzcQJOVQN1dGNxA4hVBGFyZ3NxBF1xBVUFY2hvcmRxBk5VCWNhbGxiYWNrc3EHTlUIZXJyYmFja3NxCE5VB3Rhc2tzZXRxCU5VAmlkcQpVJDQ5MDRhMWI3LWIzZWYtNDU2Yi1iYzFlLTAwNDFmYTFiNGNhNHELVQdyZXRyaWVzcQxLAFUEdGFza3ENVSVyZWdsdWl0LmNvcmUudGFza3MuZW1pdF9ub3RpZmljYXRpb25zcQ5VCXRpbWVsaW1pdHEPTk6GVQNldGFxEE5VBmt3YXJnc3ERfXESdS4=\", \"headers\": {}, \"content-type\": \"application/x-python-serialize\", \"properties\": {\"body_encoding\": \"base64\", \"correlation_id\": \"4904a1b7-b3ef-456b-bc1e-0041fa1b4ca4\", \"reply_to\": \"b4c6b5fe-2354-30ec-9a2a-658503c69395\", \"delivery_info\": {\"priority\": 0, \"routing_key\": \"celery\", \"exchange\": \"celery\"}, \"delivery_mode\": 2, \"delivery_tag\": \"190d0d61-a656-45f7-bee5-1c5edae68e7f\"}, \"content-encoding\": \"binary\"}',1),(4,1,'2016-04-21 12:53:56','{\"body\": \"gAJ9cQEoVQdleHBpcmVzcQJOVQN1dGNxA4hVBGFyZ3NxBF1xBVUFY2hvcmRxBk5VCWNhbGxiYWNrc3EHTlUIZXJyYmFja3NxCE5VB3Rhc2tzZXRxCU5VAmlkcQpVJGNkOWE3OTQ5LTMxMmMtNDRhMy1iZjNhLTk1OTA3YWI2OTEwNnELVQdyZXRyaWVzcQxLAFUEdGFza3ENVSVyZWdsdWl0LmNvcmUudGFza3MuZW1pdF9ub3RpZmljYXRpb25zcQ5VCXRpbWVsaW1pdHEPTk6GVQNldGFxEE5VBmt3YXJnc3ERfXESdS4=\", \"headers\": {}, \"content-type\": \"application/x-python-serialize\", \"properties\": {\"body_encoding\": \"base64\", \"correlation_id\": \"cd9a7949-312c-44a3-bf3a-95907ab69106\", \"reply_to\": \"b4c6b5fe-2354-30ec-9a2a-658503c69395\", \"delivery_info\": {\"priority\": 0, \"routing_key\": \"celery\", \"exchange\": \"celery\"}, \"delivery_mode\": 2, \"delivery_tag\": \"711c6ed7-257a-4409-adb6-8355b6131d52\"}, \"content-encoding\": \"binary\"}',1),(5,1,'2016-04-21 12:53:57','{\"body\": \"gAJ9cQEoVQdleHBpcmVzcQJOVQN1dGNxA4hVBGFyZ3NxBF1xBVUFY2hvcmRxBk5VCWNhbGxiYWNrc3EHTlUIZXJyYmFja3NxCE5VB3Rhc2tzZXRxCU5VAmlkcQpVJGM3Y2NhNzJlLTMxNDYtNGE2NC05MWRmLTU0MjdjNmJkMzk5N3ELVQdyZXRyaWVzcQxLAFUEdGFza3ENVSVyZWdsdWl0LmNvcmUudGFza3MuZW1pdF9ub3RpZmljYXRpb25zcQ5VCXRpbWVsaW1pdHEPTk6GVQNldGFxEE5VBmt3YXJnc3ERfXESdS4=\", \"headers\": {}, \"content-type\": \"application/x-python-serialize\", \"properties\": {\"body_encoding\": \"base64\", \"correlation_id\": \"c7cca72e-3146-4a64-91df-5427c6bd3997\", \"reply_to\": \"b4c6b5fe-2354-30ec-9a2a-658503c69395\", \"delivery_info\": {\"priority\": 0, \"routing_key\": \"celery\", \"exchange\": \"celery\"}, \"delivery_mode\": 2, \"delivery_tag\": \"c6d19430-42c3-4778-af31-3f76c690b12a\"}, \"content-encoding\": \"binary\"}',1),(6,1,'2016-04-21 12:54:59','{\"body\": \"gAJ9cQEoVQdleHBpcmVzcQJOVQN1dGNxA4hVBGFyZ3NxBGNkamFuZ28uZGIubW9kZWxzLmJhc2UKbW9kZWxfdW5waWNrbGUKcQVYBAAAAGNvcmVxBlUDQWNxcQeGXWNkamFuZ28uZGIubW9kZWxzLmJhc2UKc2ltcGxlX2NsYXNzX2ZhY3RvcnkKcQiHUnEJfXEKKFUJcmVmcmVzaGVzcQtjZGF0ZXRpbWUKZGF0ZXRpbWUKcQxVCgfgBBUMNjsHb2+FUnENVQVub25jZXEOVSAyMDBhNGZmOTJjZjJiOWRjZWE4Nzc5YzFmODYyMzlhMVUHdXNlcl9pZHEPigEHVQ53YXRlcm1hcmtlZF9pZHEQTlUHbGljZW5zZXERSwJVB2NyZWF0ZWRxEmgMVQoH4AQVDDY7B29LhVJxE1ULX3dvcmtfY2FjaGVxFGgFWAQAAABjb3JlcRVVBFdvcmtxFoZdaAiHUnEXfXEYKFUTc2VsZWN0ZWRfZWRpdGlvbl9pZHEZigE0VQ5fbGFzdF9jYW1wYWlnbnEaTlUIbGFuZ3VhZ2VxG1gCAAAAZW5VBXRpdGxlcRxYEwAAAFBybyBXZWIgMi4wIE1hc2h1cHNxHVUSb3BlbmxpYnJhcnlfbG9va3VwcR5OaBJoDFUKB+AEFQw0AQAAAIVScR9VBl9zdGF0ZXEgY2RqYW5nby5kYi5tb2RlbHMuYmFzZQpNb2RlbFN0YXRlCnEhKYFxIn1xIyhVBmFkZGluZ3EkiVUCZGJxJVUHZGVmYXVsdHEmdWJVEXB1YmxpY2F0aW9uX3JhbmdlcSdYBAAAADIwMDhVB2lzX2ZyZWVxKIlVCGZlYXR1cmVkcSlOVQpudW1fd2lzaGVzcSqKAFUCaWRxK4oBNFULZGVzY3JpcHRpb25xLFgAAAAAdWJVC191c2VyX2NhY2hlcS1oBVgEAAAAYXV0aHEuVQRVc2VycS+GXWgIh1JxMH1xMShVCHVzZXJuYW1lcTJYCQAAAHJ5bGlicmFyeVUKZmlyc3RfbmFtZXEzWAAAAABVCWxhc3RfbmFtZXE0WAAAAABVCWlzX2FjdGl2ZXE1iGggaCEpgXE2fXE3KGgkiWglaCZ1YlUFZW1haWxxOFgVAAAAcnlsaWJyYXJ5QGV4YW1wbGUub3JnVQxpc19zdXBlcnVzZXJxOYlVCGlzX3N0YWZmcTqJVQpsYXN0X2xvZ2lucTtoDFUKB+AEFQw2OAAAAIVScTxVDl9saWJyYXJ5X2NhY2hlcT1oBVgLAAAAbGlicmFyeWF1dGhxPlUHTGlicmFyeXE/hl1oCIdScUB9cUEoaA+KAQdVBG5hbWVxQlgKAAAAUlkgTGlicmFyeWgtaDBoIGghKYFxQ31xRChoJIloJWgmdWJVCG93bmVyX2lkcUWKAQVVCGFwcHJvdmVkcUaJVQhncm91cF9pZHFHigEBaCuKAQFVB2JhY2tlbmRxSFgFAAAAZW1haWx1YlUIcGFzc3dvcmRxSVgAAAAAaCuKAQdVC2RhdGVfam9pbmVkcUpoDFUKB+AEFQw2NwAAAIVScUt1YmgCTmggaCEpgXFMfXFNKGgkiWglaCZ1YlUJcmVmcmVzaGVkcU6IVQpsaWJfYWNxX2lkcU9OaCuKAQJVB3dvcmtfaWRxUIoBNHVihXFRVQVjaG9yZHFSTlUJY2FsbGJhY2tzcVNOVQhlcnJiYWNrc3FUTlUHdGFza3NldHFVTmgrVSQyY2JlNWE3My04NTRlLTQ4OGMtYmFiMS1jNTYzYzJiN2E0NmVxVlUHcmV0cmllc3FXSwBVBHRhc2txWFUgcmVnbHVpdC5jb3JlLnRhc2tzLndhdGVybWFya19hY3FxWVUJdGltZWxpbWl0cVpOToZVA2V0YXFbTlUGa3dhcmdzcVx9cV11Lg==\", \"headers\": {}, \"content-type\": \"application/x-python-serialize\", \"properties\": {\"body_encoding\": \"base64\", \"correlation_id\": \"2cbe5a73-854e-488c-bab1-c563c2b7a46e\", \"reply_to\": \"b4c6b5fe-2354-30ec-9a2a-658503c69395\", \"delivery_info\": {\"priority\": 0, \"routing_key\": \"celery\", \"exchange\": \"celery\"}, \"delivery_mode\": 2, \"delivery_tag\": \"e353108d-24f3-415f-a195-2e530f035ea0\"}, \"content-encoding\": \"binary\"}',1),(7,1,'2016-04-21 12:54:59','{\"body\": \"gAJ9cQEoVQdleHBpcmVzcQJOVQN1dGNxA4hVBGFyZ3NxBF1xBVUFY2hvcmRxBk5VCWNhbGxiYWNrc3EHTlUIZXJyYmFja3NxCE5VB3Rhc2tzZXRxCU5VAmlkcQpVJDRmMDY0ZmY5LTdiN2UtNGMyOC05MWE3LTU2MDg5NzA1MTFhNXELVQdyZXRyaWVzcQxLAFUEdGFza3ENVSVyZWdsdWl0LmNvcmUudGFza3MuZW1pdF9ub3RpZmljYXRpb25zcQ5VCXRpbWVsaW1pdHEPTk6GVQNldGFxEE5VBmt3YXJnc3ERfXESdS4=\", \"headers\": {}, \"content-type\": \"application/x-python-serialize\", \"properties\": {\"body_encoding\": \"base64\", \"correlation_id\": \"4f064ff9-7b7e-4c28-91a7-5608970511a5\", \"reply_to\": \"b4c6b5fe-2354-30ec-9a2a-658503c69395\", \"delivery_info\": {\"priority\": 0, \"routing_key\": \"celery\", \"exchange\": \"celery\"}, \"delivery_mode\": 2, \"delivery_tag\": \"db851ad2-48a0-4cb3-b15f-616fe304a3c1\"}, \"content-encoding\": \"binary\"}',1),(8,1,'2016-04-21 12:54:59','{\"body\": \"gAJ9cQEoVQdleHBpcmVzcQJOVQN1dGNxA4hVBGFyZ3NxBF1xBVUFY2hvcmRxBk5VCWNhbGxiYWNrc3EHTlUIZXJyYmFja3NxCE5VB3Rhc2tzZXRxCU5VAmlkcQpVJGY4NWY4Yjk1LTNiNWMtNGY2Zi1hMTJhLTQxMmE5MTljYjNkZnELVQdyZXRyaWVzcQxLAFUEdGFza3ENVSVyZWdsdWl0LmNvcmUudGFza3MuZW1pdF9ub3RpZmljYXRpb25zcQ5VCXRpbWVsaW1pdHEPTk6GVQNldGFxEE5VBmt3YXJnc3ERfXESdS4=\", \"headers\": {}, \"content-type\": \"application/x-python-serialize\", \"properties\": {\"body_encoding\": \"base64\", \"correlation_id\": \"f85f8b95-3b5c-4f6f-a12a-412a919cb3df\", \"reply_to\": \"b4c6b5fe-2354-30ec-9a2a-658503c69395\", \"delivery_info\": {\"priority\": 0, \"routing_key\": \"celery\", \"exchange\": \"celery\"}, \"delivery_mode\": 2, \"delivery_tag\": \"11857cc4-4cfc-4821-9028-5f4d15c6027b\"}, \"content-encoding\": \"binary\"}',1);
/*!40000 ALTER TABLE `djkombu_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `djkombu_queue`
--

DROP TABLE IF EXISTS `djkombu_queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `djkombu_queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `djkombu_queue`
--

LOCK TABLES `djkombu_queue` WRITE;
/*!40000 ALTER TABLE `djkombu_queue` DISABLE KEYS */;
INSERT INTO `djkombu_queue` VALUES (1,'celery');
/*!40000 ALTER TABLE `djkombu_queue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_change_emailchangerequest`
--

DROP TABLE IF EXISTS `email_change_emailchangerequest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `email_change_emailchangerequest` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `verification_key` varchar(40) NOT NULL,
  `email` varchar(75) NOT NULL,
  `date_created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_id_refs_id_6cd2578d` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_change_emailchangerequest`
--

LOCK TABLES `email_change_emailchangerequest` WRITE;
/*!40000 ALTER TABLE `email_change_emailchangerequest` DISABLE KEYS */;
/*!40000 ALTER TABLE `email_change_emailchangerequest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `libraryauth_block`
--

DROP TABLE IF EXISTS `libraryauth_block`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `libraryauth_block` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `library_id` int(11) NOT NULL,
  `lower` int(10) unsigned NOT NULL,
  `upper` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `lower` (`lower`),
  KEY `libraryauth_block_98518bb8` (`library_id`),
  KEY `libraryauth_block_d8292f08` (`upper`),
  CONSTRAINT `library_id_refs_id_903f7a13` FOREIGN KEY (`library_id`) REFERENCES `libraryauth_library` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `libraryauth_block`
--

LOCK TABLES `libraryauth_block` WRITE;
/*!40000 ALTER TABLE `libraryauth_block` DISABLE KEYS */;
/*!40000 ALTER TABLE `libraryauth_block` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `libraryauth_cardpattern`
--

DROP TABLE IF EXISTS `libraryauth_cardpattern`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `libraryauth_cardpattern` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `library_id` int(11) NOT NULL,
  `pattern` varchar(20) NOT NULL,
  `checksum` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `libraryauth_cardpattern_98518bb8` (`library_id`),
  CONSTRAINT `library_id_refs_id_482f9c77` FOREIGN KEY (`library_id`) REFERENCES `libraryauth_library` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `libraryauth_cardpattern`
--

LOCK TABLES `libraryauth_cardpattern` WRITE;
/*!40000 ALTER TABLE `libraryauth_cardpattern` DISABLE KEYS */;
/*!40000 ALTER TABLE `libraryauth_cardpattern` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `libraryauth_emailpattern`
--

DROP TABLE IF EXISTS `libraryauth_emailpattern`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `libraryauth_emailpattern` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `library_id` int(11) NOT NULL,
  `pattern` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `libraryauth_emailpattern_98518bb8` (`library_id`),
  CONSTRAINT `library_id_refs_id_ecbdc778` FOREIGN KEY (`library_id`) REFERENCES `libraryauth_library` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `libraryauth_emailpattern`
--

LOCK TABLES `libraryauth_emailpattern` WRITE;
/*!40000 ALTER TABLE `libraryauth_emailpattern` DISABLE KEYS */;
INSERT INTO `libraryauth_emailpattern` VALUES (1,1,'@example.org');
/*!40000 ALTER TABLE `libraryauth_emailpattern` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `libraryauth_library`
--

DROP TABLE IF EXISTS `libraryauth_library`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `libraryauth_library` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) DEFAULT NULL,
  `backend` varchar(10) NOT NULL,
  `name` varchar(80) NOT NULL,
  `approved` tinyint(1) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `group_id` (`group_id`),
  KEY `libraryauth_library_cb902d83` (`owner_id`),
  CONSTRAINT `group_id_refs_id_780edae5` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `owner_id_refs_id_4e6a8978` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `user_id_refs_id_4e6a8978` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `libraryauth_library`
--

LOCK TABLES `libraryauth_library` WRITE;
/*!40000 ALTER TABLE `libraryauth_library` DISABLE KEYS */;
INSERT INTO `libraryauth_library` VALUES (1,7,1,'email','RY Library',0,5);
/*!40000 ALTER TABLE `libraryauth_library` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `libraryauth_libraryuser`
--

DROP TABLE IF EXISTS `libraryauth_libraryuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `libraryauth_libraryuser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `library_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `credential` varchar(30) DEFAULT NULL,
  `date_modified` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `libraryauth_libraryuser_98518bb8` (`library_id`),
  KEY `libraryauth_libraryuser_6340c63c` (`user_id`),
  CONSTRAINT `library_id_refs_id_a4f6753c` FOREIGN KEY (`library_id`) REFERENCES `libraryauth_library` (`id`),
  CONSTRAINT `user_id_refs_id_807a7931` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `libraryauth_libraryuser`
--

LOCK TABLES `libraryauth_libraryuser` WRITE;
/*!40000 ALTER TABLE `libraryauth_libraryuser` DISABLE KEYS */;
INSERT INTO `libraryauth_libraryuser` VALUES (1,1,7,NULL,'2016-04-21 12:54:55'),(2,1,5,NULL,'2016-04-21 12:54:55');
/*!40000 ALTER TABLE `libraryauth_libraryuser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `marc_marcrecord`
--

DROP TABLE IF EXISTS `marc_marcrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `marc_marcrecord` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guts` longtext NOT NULL,
  `edition_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `marc_marcrecord_ae2379d4` (`edition_id`),
  KEY `marc_marcrecord_6340c63c` (`user_id`),
  CONSTRAINT `edition_id_refs_id_e161d6b6` FOREIGN KEY (`edition_id`) REFERENCES `core_edition` (`id`),
  CONSTRAINT `user_id_refs_id_f4ff367d` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `marc_marcrecord`
--

LOCK TABLES `marc_marcrecord` WRITE;
/*!40000 ALTER TABLE `marc_marcrecord` DISABLE KEYS */;
/*!40000 ALTER TABLE `marc_marcrecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification_notice`
--

DROP TABLE IF EXISTS `notification_notice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notification_notice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recipient_id` int(11) NOT NULL,
  `sender_id` int(11) DEFAULT NULL,
  `message` longtext NOT NULL,
  `notice_type_id` int(11) NOT NULL,
  `added` datetime NOT NULL,
  `unseen` tinyint(1) NOT NULL,
  `archived` tinyint(1) NOT NULL,
  `on_site` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `notification_notice_32f69dc` (`recipient_id`),
  KEY `notification_notice_6fe0a617` (`sender_id`),
  KEY `notification_notice_d734034` (`notice_type_id`),
  CONSTRAINT `notice_type_id_refs_id_212d5727` FOREIGN KEY (`notice_type_id`) REFERENCES `notification_noticetype` (`id`),
  CONSTRAINT `recipient_id_refs_id_690c45d1` FOREIGN KEY (`recipient_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `sender_id_refs_id_690c45d1` FOREIGN KEY (`sender_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification_notice`
--

LOCK TABLES `notification_notice` WRITE;
/*!40000 ALTER TABLE `notification_notice` DISABLE KEYS */;
INSERT INTO `notification_notice` VALUES (1,1,NULL,'    \n              \n        <div class=\"comments row1\">\n          <div class=\"nonavatar\">\n            <div class=\"image\">\n                <a href=\"/work/2003/?tab=2\"><img src=\"http://bks0.books.google.com/books?id=Lx-hrmLCGHkC&amp;printsec=frontcover&amp;img=1&amp;zoom=1\" alt=\"cover image\" /></a>\n            </div>\n              <span><a href=\"/supporter/rdhyee/\">Raymond Yee</a> on <a href=\"/work/2003/?tab=2\">Bach</a></span><br />\n              \n              <span class=\"text\">fine book</span>\n           </div>\n           \n           <div class=\"avatar\">\n              <a href=\"/supporter/rdhyee/\">\n                \n                    <img class=\"user-avatar\" src=\"/static/images/header/avatar.png\" height=\"50\" width=\"50\" alt=\"Generic Ungluer Avatar\" title=\"Ungluer\" />\n                \n              </a>\n           </div>\n    </div>\n              \n    \n',1,'2012-03-27 16:53:46',1,0,1),(2,1,NULL,'    \n              \n        <div class=\"comments row1\">\n          <div class=\"nonavatar\">\n            <div class=\"image\">\n                <a href=\"/work/2003/?tab=2\"><img src=\"http://bks2.books.google.com/books?id=Lx-hrmLCGHkC&amp;printsec=frontcover&amp;img=1&amp;zoom=1\" alt=\"cover image\" /></a>\n            </div>\n              <span><a href=\"/supporter/rdhyee/\">Raymond Yee</a> on <a href=\"/work/2003/?tab=2\">Bach</a></span><br />\n              \n              <span class=\"text\">excellent book</span>\n           </div>\n           \n           <div class=\"avatar\">\n              <a href=\"/supporter/rdhyee/\">\n                \n                    <img class=\"user-avatar\" src=\"/static/images/header/avatar.png\" height=\"50\" width=\"50\" alt=\"Generic Ungluer Avatar\" title=\"Ungluer\" />\n                \n              </a>\n           </div>\n    </div>\n              \n    \n',1,'2012-03-27 16:54:37',1,0,1),(3,14,NULL,'    \n              \n        <div class=\"comments row1\">\n          <div class=\"nonavatar\">\n            <div class=\"image\">\n                <a href=\"/work/2003/?tab=2\"><img src=\"http://bks1.books.google.com/books?id=Lx-hrmLCGHkC&amp;printsec=frontcover&amp;img=1&amp;zoom=1\" alt=\"cover image\" /></a>\n            </div>\n              <span><a href=\"/supporter/rdhyee/\">Raymond Yee</a> on <a href=\"/work/2003/?tab=2\">Bach</a></span><br />\n              \n              <span class=\"text\">excellent book</span>\n           </div>\n           \n           <div class=\"avatar\">\n              <a href=\"/supporter/rdhyee/\">\n                \n                    <img class=\"user-avatar\" src=\"/static/images/header/avatar.png\" height=\"50\" width=\"50\" alt=\"Generic Ungluer Avatar\" title=\"Ungluer\" />\n                \n              </a>\n           </div>\n    </div>\n              \n    \n',1,'2012-03-27 16:54:38',1,0,1),(4,466,NULL,'    \n              \n        <div class=\"comments row1\">\n          <div class=\"nonavatar\">\n            <div class=\"image\">\n                <a href=\"/work/79519/?tab=2\"><img src=\"http://bks5.books.google.com/books?id=QaYbM0Fvch8C&amp;printsec=frontcover&amp;img=1&amp;zoom=1\" alt=\"cover image\" /></a>\n            </div>\n              <span><a href=\"/supporter/rdhyee4/\">rdhyee4</a> on <a href=\"/work/79519/?tab=2\">I Am America (And So Can You!)</a></span><br />\n              \n              <span class=\"text\">go, Stephen</span>\n           </div>\n           \n           <div class=\"avatar\">\n              <a href=\"/supporter/rdhyee4/\">\n                \n                    <img class=\"user-avatar\" src=\"/static/images/header/avatar.png\" height=\"50\" width=\"50\" alt=\"Generic Ungluer Avatar\" title=\"Ungluer\" />\n                \n              </a>\n           </div>\n    </div>\n              \n    \n',1,'2012-03-27 16:59:48',1,0,1),(5,466,NULL,'    \n              \n        <div class=\"comments row1\">\n          <div class=\"nonavatar\">\n            <div class=\"image\">\n                <a href=\"/work/79519/?tab=2\"><img src=\"http://bks6.books.google.com/books?id=QaYbM0Fvch8C&amp;printsec=frontcover&amp;img=1&amp;zoom=1\" alt=\"cover image\" /></a>\n            </div>\n              <span><a href=\"/supporter/rdhyee4/\">rdhyee4</a> on <a href=\"/work/79519/?tab=2\">I Am America (And So Can You!)</a></span><br />\n              \n              <span class=\"text\">Colbert is awesome</span>\n           </div>\n           \n           <div class=\"avatar\">\n              <a href=\"/supporter/rdhyee4/\">\n                \n                    <img class=\"user-avatar\" src=\"/static/images/header/avatar.png\" height=\"50\" width=\"50\" alt=\"Generic Ungluer Avatar\" title=\"Ungluer\" />\n                \n              </a>\n           </div>\n    </div>\n              \n    \n',1,'2012-03-27 17:42:07',1,0,1),(6,466,NULL,'    \n              \n        <div class=\"comments row1\">\n          <div class=\"nonavatar\">\n            <div class=\"image\">\n                <a href=\"/work/79519/?tab=2\"><img src=\"http://bks6.books.google.com/books?id=QaYbM0Fvch8C&amp;printsec=frontcover&amp;img=1&amp;zoom=1\" alt=\"cover image\" /></a>\n            </div>\n              <span><a href=\"/supporter/rdhyee4/\">rdhyee4</a> on <a href=\"/work/79519/?tab=2\">I Am America (And So Can You!)</a></span><br />\n              \n              <span class=\"text\">Colbert is awesomer.</span>\n           </div>\n           \n           <div class=\"avatar\">\n              <a href=\"/supporter/rdhyee4/\">\n                \n                    <img class=\"user-avatar\" src=\"/static/images/header/avatar.png\" height=\"50\" width=\"50\" alt=\"Generic Ungluer Avatar\" title=\"Ungluer\" />\n                \n              </a>\n           </div>\n    </div>\n              \n    \n',1,'2012-03-27 17:43:23',1,0,1),(7,1,NULL,'    \n              \n        <div class=\"comments row1\">\n          <div class=\"nonavatar\">\n            <div class=\"image\">\n                <a href=\"/work/2003/?tab=2\"><img src=\"http://bks3.books.google.com/books?id=Lx-hrmLCGHkC&amp;printsec=frontcover&amp;img=1&amp;zoom=1\" alt=\"cover image\" /></a>\n            </div>\n              <span><a href=\"/supporter/rdhyee/\">Raymond Yee</a> on <a href=\"/work/2003/?tab=2\">Bach</a></span><br />\n              \n              <span class=\"text\">awesome book about an awesome composer</span>\n           </div>\n           \n           <div class=\"avatar\">\n              <a href=\"/supporter/rdhyee/\">\n                \n                    <img class=\"user-avatar\" src=\"/static/images/header/avatar.png\" height=\"50\" width=\"50\" alt=\"Generic Ungluer Avatar\" title=\"Ungluer\" />\n                \n              </a>\n           </div>\n    </div>\n              \n    \n',1,'2012-03-28 11:19:05',1,0,1);
/*!40000 ALTER TABLE `notification_notice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification_noticequeuebatch`
--

DROP TABLE IF EXISTS `notification_noticequeuebatch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notification_noticequeuebatch` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pickled_data` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification_noticequeuebatch`
--

LOCK TABLES `notification_noticequeuebatch` WRITE;
/*!40000 ALTER TABLE `notification_noticequeuebatch` DISABLE KEYS */;
INSERT INTO `notification_noticequeuebatch` VALUES (3,'KGxwMQooTDNMClMncmlnaHRzX2hvbGRlcl9jbGFpbScKcDIKKGRwMwpTJ2NsYWltJwpwNApjZGph\nbmdvLmRiLm1vZGVscy5iYXNlCm1vZGVsX3VucGlja2xlCnA1CigoVmNvcmUKcDYKUydDbGFpbScK\ncDcKdChsY2RqYW5nby5kYi5tb2RlbHMuYmFzZQpzaW1wbGVfY2xhc3NfZmFjdG9yeQpwOAp0UnA5\nCihkcDEwClMnc3RhdHVzJwpwMTEKUydwZW5kaW5nJwpwMTIKc1MndXNlcl9pZCcKcDEzCkwzTApz\nUydjcmVhdGVkJwpwMTQKY2RhdGV0aW1lCmRhdGV0aW1lCnAxNQooUydceDA3XHhlMFx4MDRceDE1\nXHgwYzRceDAxXHgwNVxuXHhkNScKdFJwMTYKc1MnX3VzZXJfY2FjaGUnCnAxNwpnNQooKFZhdXRo\nCnAxOApTJ1VzZXInCnAxOQp0KGxnOAp0UnAyMAooZHAyMQpTJ3VzZXJuYW1lJwpwMjIKVnJkaHll\nZXRlc3QKcDIzCnNTJ2ZpcnN0X25hbWUnCnAyNApWCnNTJ2xhc3RfbmFtZScKcDI1ClYKc1MnaXNf\nYWN0aXZlJwpwMjYKSTAxCnNTJ19zdGF0ZScKcDI3CmNjb3B5X3JlZwpfcmVjb25zdHJ1Y3Rvcgpw\nMjgKKGNkamFuZ28uZGIubW9kZWxzLmJhc2UKTW9kZWxTdGF0ZQpwMjkKY19fYnVpbHRpbl9fCm9i\namVjdApwMzAKTnRScDMxCihkcDMyClMnYWRkaW5nJwpwMzMKSTAwCnNTJ2RiJwpwMzQKUydkZWZh\ndWx0JwpwMzUKc2JzUydlbWFpbCcKcDM2ClZyYXltb25kLnllZUBkYXRhdW5ib3VuZC5jb20KcDM3\nCnNTJ2lzX3N1cGVydXNlcicKcDM4CkkwMApzUydpc19zdGFmZicKcDM5CkkwMApzUydsYXN0X2xv\nZ2luJwpwNDAKZzE1CihTJ1x4MDdceGRjXHgwM1xyXHgxM1x4MGVceDFiXHgwMFx4MDBceDAwJwp0\nUnA0MQpzUydwYXNzd29yZCcKcDQyClZzaGExJDFiZDM3JDAyYjk5OTEzZjYwMmE4MGM1ZjgxMDQ0\nM2NlODJkNzNmMzM2YzI2ZDMKcDQzCnNTJ2lkJwpwNDQKTDNMCnNTJ2RhdGVfam9pbmVkJwpwNDUK\nZzE1CihTJ1x4MDdceGRjXHgwM1xyXHgxM1x4MGIgXHgwMFx4MDBceDAwJwp0UnA0NgpzYnNnMjcK\nZzI4CihnMjkKZzMwCk50UnA0NwooZHA0OApnMzMKSTAwCnNnMzQKZzM1CnNic1MncmlnaHRzX2hv\nbGRlcl9pZCcKcDQ5CkwxTApzUydfcmlnaHRzX2hvbGRlcl9jYWNoZScKcDUwCmc1CigoVmNvcmUK\ncDUxClMnUmlnaHRzSG9sZGVyJwpwNTIKdChsZzgKdFJwNTMKKGRwNTQKUydjYW5fc2VsbCcKcDU1\nCkkwMQpzZzE0CmcxNQooUydceDA3XHhlMFx4MDRceDE1XHgwYzRceDAwXHgwMFx4MDBceDAwJwp0\nUnA1NgpzZzI3CmcyOAooZzI5CmczMApOdFJwNTcKKGRwNTgKZzMzCkkwMApzZzM0CmczNQpzYnNn\nNDQKTDFMCnNTJ19vd25lcl9jYWNoZScKcDU5Cmc1CigoZzE4CmcxOQp0KGxnOAp0UnA2MAooZHA2\nMQpnMjIKVnJkaHllZXRlc3QKcDYyCnNnMjQKVgpzZzI1ClYKc2cyNgpJMDEKc2cyNwpnMjgKKGcy\nOQpnMzAKTnRScDYzCihkcDY0CmczMwpJMDAKc2czNApnMzUKc2JzZzM2ClZyYXltb25kLnllZUBk\nYXRhdW5ib3VuZC5jb20KcDY1CnNnMzgKSTAwCnNnMzkKSTAwCnNnNDAKZzE1CihTJ1x4MDdceGRj\nXHgwM1xyXHgxM1x4MGVceDFiXHgwMFx4MDBceDAwJwp0UnA2NgpzZzQyClZzaGExJDFiZDM3JDAy\nYjk5OTEzZjYwMmE4MGM1ZjgxMDQ0M2NlODJkNzNmMzM2YzI2ZDMKcDY3CnNnNDQKTDNMCnNnNDUK\nZzE1CihTJ1x4MDdceGRjXHgwM1xyXHgxM1x4MGIgXHgwMFx4MDBceDAwJwp0UnA2OApzYnNnMzYK\nVnJheW1vbmQueWVlQGRhdGF1bmJvdW5kLmNvbQpwNjkKc1MncmlnaHRzX2hvbGRlcl9uYW1lJwpw\nNzAKVlJZIEluYwpwNzEKc1Mnb3duZXJfaWQnCnA3MgpMM0wKc2JzZzQ0CkwxTApzUyd3b3JrX2lk\nJwpwNzMKTDUyTApzYnNJMDEKTnRwNzQKYShMNkwKZzIKZzMKSTAxCk50cDc1CmEu\n'),(4,'KGxwMQooTDNMClMncmlnaHRzX2hvbGRlcl9jbGFpbScKcDIKKGRwMwpTJ2NsYWltJwpwNApjZGph\nbmdvLmRiLm1vZGVscy5iYXNlCm1vZGVsX3VucGlja2xlCnA1CigoVmNvcmUKcDYKUydDbGFpbScK\ncDcKdChsY2RqYW5nby5kYi5tb2RlbHMuYmFzZQpzaW1wbGVfY2xhc3NfZmFjdG9yeQpwOAp0UnA5\nCihkcDEwClMnc3RhdHVzJwpwMTEKUydhY3RpdmUnCnAxMgpzUyd1c2VyX2lkJwpwMTMKTDNMCnNT\nJ2NyZWF0ZWQnCnAxNApjZGF0ZXRpbWUKZGF0ZXRpbWUKcDE1CihTJ1x4MDdceGUwXHgwNFx4MTVc\neDBjNFx4MDFceDA1XG5ceGQ1Jwp0UnAxNgpzUydfd29ya19jYWNoZScKcDE3Cmc1CigoVmNvcmUK\ncDE4ClMnV29yaycKcDE5CnQobGc4CnRScDIwCihkcDIxClMnc2VsZWN0ZWRfZWRpdGlvbl9pZCcK\ncDIyCk5zUydfbGFzdF9jYW1wYWlnbicKcDIzCk5zUydsYW5ndWFnZScKcDI0ClZlbgpwMjUKc1Mn\ndGl0bGUnCnAyNgpWUHJvIFdlYiAyLjAgTWFzaHVwcwpwMjcKc1Mnb3BlbmxpYnJhcnlfbG9va3Vw\nJwpwMjgKTnNnMTQKZzE1CihTJ1x4MDdceGUwXHgwNFx4MTVceDBjNFx4MDFceDAwXHgwMFx4MDAn\nCnRScDI5CnNTJ19zdGF0ZScKcDMwCmNjb3B5X3JlZwpfcmVjb25zdHJ1Y3RvcgpwMzEKKGNkamFu\nZ28uZGIubW9kZWxzLmJhc2UKTW9kZWxTdGF0ZQpwMzIKY19fYnVpbHRpbl9fCm9iamVjdApwMzMK\nTnRScDM0CihkcDM1ClMnYWRkaW5nJwpwMzYKSTAwCnNTJ2RiJwpwMzcKUydkZWZhdWx0JwpwMzgK\nc2JzUydwdWJsaWNhdGlvbl9yYW5nZScKcDM5Ck5zUydpc19mcmVlJwpwNDAKSTAwCnNTJ2ZlYXR1\ncmVkJwpwNDEKTnNTJ251bV93aXNoZXMnCnA0MgpMMEwKc1MnaWQnCnA0MwpMNTJMCnNTJ2Rlc2Ny\naXB0aW9uJwpwNDQKVgpzYnNTJ191c2VyX2NhY2hlJwpwNDUKZzUKKChWYXV0aApwNDYKUydVc2Vy\nJwpwNDcKdChsZzgKdFJwNDgKKGRwNDkKUyd1c2VybmFtZScKcDUwClZyZGh5ZWV0ZXN0CnA1MQpz\nUydmaXJzdF9uYW1lJwpwNTIKVgpzUydsYXN0X25hbWUnCnA1MwpWCnNTJ2lzX2FjdGl2ZScKcDU0\nCkkwMQpzZzMwCmczMQooZzMyCmczMwpOdFJwNTUKKGRwNTYKZzM2CkkwMApzZzM3CmczOApzYnNT\nJ2VtYWlsJwpwNTcKVnJheW1vbmQueWVlQGRhdGF1bmJvdW5kLmNvbQpwNTgKc1MnaXNfc3VwZXJ1\nc2VyJwpwNTkKSTAwCnNTJ2lzX3N0YWZmJwpwNjAKSTAwCnNTJ2xhc3RfbG9naW4nCnA2MQpnMTUK\nKFMnXHgwN1x4ZGNceDAzXHJceDEzXHgwZVx4MWJceDAwXHgwMFx4MDAnCnRScDYyCnNTJ3Bhc3N3\nb3JkJwpwNjMKVnNoYTEkMWJkMzckMDJiOTk5MTNmNjAyYTgwYzVmODEwNDQzY2U4MmQ3M2YzMzZj\nMjZkMwpwNjQKc2c0MwpMM0wKc1MnZGF0ZV9qb2luZWQnCnA2NQpnMTUKKFMnXHgwN1x4ZGNceDAz\nXHJceDEzXHgwYiBceDAwXHgwMFx4MDAnCnRScDY2CnNic2czMApnMzEKKGczMgpnMzMKTnRScDY3\nCihkcDY4CmczNgpJMDAKc2czNwpnMzgKc2JzUydyaWdodHNfaG9sZGVyX2lkJwpwNjkKTDFMCnNT\nJ19yaWdodHNfaG9sZGVyX2NhY2hlJwpwNzAKZzUKKChWY29yZQpwNzEKUydSaWdodHNIb2xkZXIn\nCnA3Mgp0KGxnOAp0UnA3MwooZHA3NApTJ2Nhbl9zZWxsJwpwNzUKSTAxCnNnMTQKZzE1CihTJ1x4\nMDdceGUwXHgwNFx4MTVceDBjNFx4MDBceDAwXHgwMFx4MDAnCnRScDc2CnNnMzAKZzMxCihnMzIK\nZzMzCk50UnA3NwooZHA3OApnMzYKSTAwCnNnMzcKZzM4CnNic2c0MwpMMUwKc1MnX293bmVyX2Nh\nY2hlJwpwNzkKZzUKKChnNDYKZzQ3CnQobGc4CnRScDgwCihkcDgxCmc1MApWcmRoeWVldGVzdApw\nODIKc2c1MgpWCnNnNTMKVgpzZzU0CkkwMQpzZzMwCmczMQooZzMyCmczMwpOdFJwODMKKGRwODQK\nZzM2CkkwMApzZzM3CmczOApzYnNnNTcKVnJheW1vbmQueWVlQGRhdGF1bmJvdW5kLmNvbQpwODUK\nc2c1OQpJMDAKc2c2MApJMDAKc2c2MQpnMTUKKFMnXHgwN1x4ZGNceDAzXHJceDEzXHgwZVx4MWJc\neDAwXHgwMFx4MDAnCnRScDg2CnNnNjMKVnNoYTEkMWJkMzckMDJiOTk5MTNmNjAyYTgwYzVmODEw\nNDQzY2U4MmQ3M2YzMzZjMjZkMwpwODcKc2c0MwpMM0wKc2c2NQpnMTUKKFMnXHgwN1x4ZGNceDAz\nXHJceDEzXHgwYiBceDAwXHgwMFx4MDAnCnRScDg4CnNic2c1NwpWcmF5bW9uZC55ZWVAZGF0YXVu\nYm91bmQuY29tCnA4OQpzUydyaWdodHNfaG9sZGVyX25hbWUnCnA5MApWUlkgSW5jCnA5MQpzUydv\nd25lcl9pZCcKcDkyCkwzTApzYnNnNDMKTDFMCnNTJ3dvcmtfaWQnCnA5MwpMNTJMCnNic0kwMQpO\ndHA5NAphKEw2TApnMgpnMwpJMDEKTnRwOTUKYS4=\n'),(5,'KGxwMQooTDNMClMncGxlZGdlX3lvdV9oYXZlX3BsZWRnZWQnCnAyCihkcDMKUyd0cmFuc2FjdGlv\nbicKcDQKY2RqYW5nby5kYi5tb2RlbHMuYmFzZQptb2RlbF91bnBpY2tsZQpwNQooKFZwYXltZW50\nCnA2ClMnVHJhbnNhY3Rpb24nCnA3CnQobGNkamFuZ28uZGIubW9kZWxzLmJhc2UKc2ltcGxlX2Ns\nYXNzX2ZhY3RvcnkKcDgKdFJwOQooZHAxMApTJ2V4dHJhJwpwMTEKKGRwMTIKc1MncGF5X2tleScK\ncDEzCk5zUydyZWNlaXB0JwpwMTQKTnNTJ19zdGF0ZScKcDE1CmNjb3B5X3JlZwpfcmVjb25zdHJ1\nY3RvcgpwMTYKKGNkamFuZ28uZGIubW9kZWxzLmJhc2UKTW9kZWxTdGF0ZQpwMTcKY19fYnVpbHRp\nbl9fCm9iamVjdApwMTgKTnRScDE5CihkcDIwClMnYWRkaW5nJwpwMjEKSTAwCnNTJ2RiJwpwMjIK\nUydkZWZhdWx0JwpwMjMKc2JzUydjYW1wYWlnbl9pZCcKcDI0CkwzTApzUydjdXJyZW5jeScKcDI1\nClMnVVNEJwpwMjYKc1MnaWQnCnAyNwpMMUwKc1MnbG9jYWxfc3RhdHVzJwpwMjgKVk5PTkUKcDI5\nCnNTJ2RhdGVfYXV0aG9yaXplZCcKcDMwCmNkYXRldGltZQpkYXRldGltZQpwMzEKKFMnXHgwN1x4\nZTBceDA0XHgxNVx4MGM1Nlx4MDNceDE0XHhjYycKdFJwMzIKc1MndXNlcl9pZCcKcDMzCkwzTApz\nUydtYXhfYW1vdW50JwpwMzQKY2RlY2ltYWwKRGVjaW1hbApwMzUKKFMnMTAuMDAnCnRScDM2CnNT\nJ191c2VyX2NhY2hlJwpwMzcKZzUKKChWYXV0aApwMzgKUydVc2VyJwpwMzkKdChsZzgKdFJwNDAK\nKGRwNDEKUyd1c2VybmFtZScKcDQyClZyZGh5ZWV0ZXN0CnA0MwpzUydmaXJzdF9uYW1lJwpwNDQK\nVgpzUydsYXN0X25hbWUnCnA0NQpWCnNTJ19wcm9maWxlX2NhY2hlJwpwNDYKZzUKKChWY29yZQpw\nNDcKUydVc2VyUHJvZmlsZScKcDQ4CnQobGc4CnRScDQ5CihkcDUwClMnZ29vZHJlYWRzX2F1dGhf\nc2VjcmV0JwpwNTEKTnNnMzMKTDNMCnNTJ2dvb2RyZWFkc191c2VyX25hbWUnCnA1MgpOc1MnY3Jl\nYXRlZCcKcDUzCmczMQooUydceDA3XHhkY1x4MDNcclx4MTNceDBiIFx4MDBceDAwXHgwMCcKdFJw\nNTQKc1MnYXZhdGFyX3NvdXJjZScKcDU1Ck5zUyd0YWdsaW5lJwpwNTYKVgpzUydraW5kbGVfZW1h\naWwnCnA1NwpWCnNnMTUKZzE2CihnMTcKZzE4Ck50UnA1OAooZHA1OQpnMjEKSTAwCnNnMjIKZzIz\nCnNic1MndHdpdHRlcl9pZCcKcDYwClYKc1MncGljX3VybCcKcDYxClYKc1MnZ29vZHJlYWRzX3Vz\nZXJfaWQnCnA2MgpOc2czNwpnNDAKc1MnZ29vZHJlYWRzX3VzZXJfbGluaycKcDYzCk5zUydmYWNl\nYm9va19pZCcKcDY0Ck5zUydsaWJyYXJ5dGhpbmdfaWQnCnA2NQpWCnNTJ2hvbWVfdXJsJwpwNjYK\nVgpzUydnb29kcmVhZHNfYXV0aF90b2tlbicKcDY3Ck5zZzI3CkwzTApzYnNTJ2lzX2FjdGl2ZScK\ncDY4CkkwMQpzZzE1CmcxNgooZzE3CmcxOApOdFJwNjkKKGRwNzAKZzIxCkkwMApzZzIyCmcyMwpz\nYnNTJ19jcmVkaXRfY2FjaGUnCnA3MQpnNQooKFZwYXltZW50CnA3MgpTJ0NyZWRpdCcKcDczCnQo\nbGc4CnRScDc0CihkcDc1CmczMwpMM0wKc1MncGxlZGdlZCcKcDc2CmczNQooUycwLjAwJwp0UnA3\nNwpzZzE1CmcxNgooZzE3CmcxOApOdFJwNzgKKGRwNzkKZzIxCkkwMApzZzIyCmcyMwpzYnNnMzcK\nZzQwCnNTJ2xhc3RfYWN0aXZpdHknCnA4MApnMzEKKFMnXHgwN1x4ZTBceDA0XHgxNVx4MGMzOFx4\nMDBceDAwXHgwMCcKdFJwODEKc1MnYmFsYW5jZScKcDgyCmczNQooUycwLjAwJwp0UnA4MwpzZzI3\nCkwzTApzYnNTJ2VtYWlsJwpwODQKVnJheW1vbmQueWVlQGRhdGF1bmJvdW5kLmNvbQpwODUKc1Mn\naXNfc3VwZXJ1c2VyJwpwODYKSTAwCnNTJ2lzX3N0YWZmJwpwODcKSTAwCnNTJ2xhc3RfbG9naW4n\nCnA4OApnMzEKKFMnXHgwN1x4ZTBceDA0XHgxNVx4MGM1KFx4MDBceDAwXHgwMCcKdFJwODkKc1Mn\ncGFzc3dvcmQnCnA5MApWcGJrZGYyX3NoYTI1NiQxMjAwMCRwaFZNT3hCTDdKZlckM0d4WDRGOWlI\nYTJvM0hJVmhIUjJQMXVmUFVjVFpwTmtCenhPRDBhM0gwMD0KcDkxCnNnMjcKTDNMCnNTJ2RhdGVf\nam9pbmVkJwpwOTIKZzMxCihTJ1x4MDdceGRjXHgwM1xyXHgxM1x4MGIgXHgwMFx4MDBceDAwJwp0\nUnA5MwpzYnNTJ2FwcHJvdmVkJwpwOTQKSTAxCnNTJ3NlY3JldCcKcDk1ClY5ZDNhNzc0Zi0wN2Ux\nLTExZTYtYWFjYS0zYzE1YzJlYjYyYmMKcDk2CnNTJ3ByZWFwcHJvdmFsX2tleScKcDk3ClZjdXNf\nOEpOcHVXOFJNN0ttc1cKcDk4CnNTJ2RhdGVfcGF5bWVudCcKcDk5Ck5zUyd0eXBlJwpwMTAwCkky\nCnNTJ3N0YXR1cycKcDEwMQpTJ0FjdGl2ZScKcDEwMgpzUydkYXRlX2V4cGlyZWQnCnAxMDMKZzMx\nCihTJ1x4MDdceGUxXHgwNFx4MTVceDBjNTZceDAzXHgxNFx4Y2MnCnRScDEwNApzUydvZmZlcl9p\nZCcKcDEwNQpOc1MnaG9zdCcKcDEwNgpTJ3N0cmlwZWxpYicKcDEwNwpzUydhbm9ueW1vdXMnCnAx\nMDgKSTAwCnNTJ2V4ZWN1dGlvbicKcDEwOQpMMEwKc1MnZGF0ZV9leGVjdXRlZCcKcDExMApOc1Mn\nX2NhbXBhaWduX2NhY2hlJwpwMTExCmc1CigoVmNvcmUKcDExMgpTJ0NhbXBhaWduJwpwMTEzCnQo\nbGc4CnRScDExNAooZHAxMTUKUydkb193YXRlcm1hcmsnCnAxMTYKSTAxCnNnMTUKZzE2CihnMTcK\nZzE4Ck50UnAxMTcKKGRwMTE4CmcyMQpJMDAKc2cyMgpnMjMKc2JzUyd1c2VfYWRkX2FzaycKcDEx\nOQpJMDEKc1MnZGVhZGxpbmUnCnAxMjAKZzMxCihTJ1x4MDdceGRjXHgwM1x4MDdceDExXHgxYTZc\neDAwXHgwMFx4MDAnCnRScDEyMQpzZzI3CkwzTApzUydhbWF6b25fcmVjZWl2ZXInCnAxMjIKVgpz\nUydkZXRhaWxzJwpwMTIzCk5zUydfY3VycmVudF90b3RhbCcKcDEyNApnMzUKKFMnMTAuMDAnCnRS\ncDEyNQpzUydwdWJsaXNoZXJfaWQnCnAxMjYKTnNnODQKVgpzZzEwMQpWQUNUSVZFCnAxMjcKc1Mn\nZGVzY3JpcHRpb24nCnAxMjgKVlRlc3QgQ2FtcGFpZ24KcDEyOQpzUydwYXlwYWxfcmVjZWl2ZXIn\nCnAxMzAKVnJoMV8xMzE3MzM2MjUxX2JpekBnbHVlamFyLmNvbQpwMTMxCnNTJ2FjdGl2YXRlZCcK\ncDEzMgpOc1MnX3dvcmtfY2FjaGUnCnAxMzMKZzUKKChWY29yZQpwMTM0ClMnV29yaycKcDEzNQp0\nKGxnOAp0UnAxMzYKKGRwMTM3ClMnc2VsZWN0ZWRfZWRpdGlvbl9pZCcKcDEzOApMNDhMCnNTJ19s\nYXN0X2NhbXBhaWduJwpwMTM5Ck5zUydsYW5ndWFnZScKcDE0MApWZW4KcDE0MQpzUyd0aXRsZScK\ncDE0MgpWQSBXaXphcmQgb2YgRWFydGhzZWEKcDE0MwpzUydvcGVubGlicmFyeV9sb29rdXAnCnAx\nNDQKTnNnNTMKZzMxCihTJ1x4MDdceGRjXHgwM1x4MDJcclx4MDNceDFlXHgwMFx4MDBceDAwJwp0\nUnAxNDUKc2cxNQpnMTYKKGcxNwpnMTgKTnRScDE0NgooZHAxNDcKZzIxCkkwMApzZzIyCmcyMwpz\nYnNTJ3B1YmxpY2F0aW9uX3JhbmdlJwpwMTQ4ClYyMDA0CnAxNDkKc1MnaXNfZnJlZScKcDE1MApJ\nMDAKc1MnZmVhdHVyZWQnCnAxNTEKTnNTJ251bV93aXNoZXMnCnAxNTIKTDBMCnNnMjcKTDQ4TApz\nZzEyOApWVXJzdWxhIEsuIExlIEd1aW4ncyBmaXJzdCBib29rIG9mIEVhcnRoc2VhLS1hIHRyZWFz\ndXJlZCBjbGFzc2ljIG5vdmVsIG9mIHdpc2RvbSBhbmQgd2l6YXJkcnktLWludHJvZHVjZXMgYSBi\nb3kgd2hvIGdyb3dzIHRvIG1hbmhvb2Qgd2hpbGUgYXR0ZW1wdGluZyB0byBzdWJkdWUgdGhlIGV2\naWwgaGUgdW5sZWFzaGVkIG9uIHRoZSB3b3JsZCBhcyBhbiBhcHByZW50aWNlIHRvIHRoZSBNYXN0\nZXIgV2l6YXJkLiBZb3VuZyBBZHVsdC4KcDE1MwpzYnNTJ3Byb2JsZW1zJwpwMTU0CihscDE1NQpz\nUydkb2xsYXJfcGVyX2RheScKcDE1NgpOc1MnY2NfZGF0ZV9pbml0aWFsJwpwMTU3Ck5zUyduYW1l\nJwpwMTU4ClZBIFdpemFyZCBvZiBFYXJ0aHNlYQpwMTU5CnNTJ3RhcmdldCcKcDE2MApnMzUKKFMn\nMTYzNi4wMCcKdFJwMTYxCnNTJ2xpY2Vuc2UnCnAxNjIKVkNDIEJZLU5DLU5ECnAxNjMKc2c1Mwpn\nMzEKKFMnXHgwN1x4ZGNceDAzXHgwMlxyXHgwNFx4MDNceDAwXHgwMFx4MDAnCnRScDE2NApzZzEw\nMApJMQpzUydlZGl0aW9uX2lkJwpwMTY1Ck5zUyd3b3JrX2lkJwpwMTY2Ckw0OEwKc1MnbGVmdCcK\ncDE2NwpnMzUKKFMnMTYyNi4wMCcKdFJwMTY4CnNic1MnZGF0ZV9tb2RpZmllZCcKcDE2OQpnMzEK\nKFMnXHgwN1x4ZTBceDA0XHgxNVx4MGM1Nlx4MDM0WCcKdFJwMTcwCnNTJ3JlYXNvbicKcDE3MQpO\nc1MncHJlbWl1bV9pZCcKcDE3MgpMMTUwTApzUydhbW91bnQnCnAxNzMKZzM2CnNTJ2Vycm9yJwpw\nMTc0Ck5zUydkYXRlX2NyZWF0ZWQnCnAxNzUKZzMxCihTJ1x4MDdceGUwXHgwNFx4MTVceDBjNS5c\neDAwXHgwMFx4MDAnCnRScDE3NgpzYnNJMDEKTnRwMTc3CmEu\n'),(6,'KGxwMQooTDNMClMncGxlZGdlX3N0YXR1c19jaGFuZ2UnCnAyCihkcDMKUyd1cF9vcl9kb3duJwpw\nNApTJ2RlY3JlYXNlZCcKcDUKc1MndHJhbnNhY3Rpb24nCnA2CmNkamFuZ28uZGIubW9kZWxzLmJh\nc2UKbW9kZWxfdW5waWNrbGUKcDcKKChWcGF5bWVudApwOApTJ1RyYW5zYWN0aW9uJwpwOQp0KGxj\nZGphbmdvLmRiLm1vZGVscy5iYXNlCnNpbXBsZV9jbGFzc19mYWN0b3J5CnAxMAp0UnAxMQooZHAx\nMgpTJ2V4dHJhJwpwMTMKKGRwMTQKc1MncGF5X2tleScKcDE1Ck5zUydyZWNlaXB0JwpwMTYKTnNT\nJ19zdGF0ZScKcDE3CmNjb3B5X3JlZwpfcmVjb25zdHJ1Y3RvcgpwMTgKKGNkamFuZ28uZGIubW9k\nZWxzLmJhc2UKTW9kZWxTdGF0ZQpwMTkKY19fYnVpbHRpbl9fCm9iamVjdApwMjAKTnRScDIxCihk\ncDIyClMnYWRkaW5nJwpwMjMKSTAwCnNTJ2RiJwpwMjQKUydkZWZhdWx0JwpwMjUKc2JzUydjYW1w\nYWlnbl9pZCcKcDI2CkwzTApzUydjdXJyZW5jeScKcDI3ClZVU0QKcDI4CnNTJ2lkJwpwMjkKTDFM\nCnNTJ2xvY2FsX3N0YXR1cycKcDMwClZOT05FCnAzMQpzUydkYXRlX2F1dGhvcml6ZWQnCnAzMgpj\nZGF0ZXRpbWUKZGF0ZXRpbWUKcDMzCihTJ1x4MDdceGUwXHgwNFx4MTVceDBjNTZceDAwXHgwMFx4\nMDAnCnRScDM0CnNTJ3VzZXJfaWQnCnAzNQpMM0wKc1MnbWF4X2Ftb3VudCcKcDM2CmNkZWNpbWFs\nCkRlY2ltYWwKcDM3CihTJzEwLjAwJwp0UnAzOApzUydfb2ZmZXJfY2FjaGUnCnAzOQpOc1MnX3Vz\nZXJfY2FjaGUnCnA0MApnNwooKFZhdXRoCnA0MQpTJ1VzZXInCnA0Mgp0KGxnMTAKdFJwNDMKKGRw\nNDQKUyd1c2VybmFtZScKcDQ1ClZyZGh5ZWV0ZXN0CnA0NgpzUydmaXJzdF9uYW1lJwpwNDcKVgpz\nUydsYXN0X25hbWUnCnA0OApWCnNTJ2lzX2FjdGl2ZScKcDQ5CkkwMQpzZzE3CmcxOAooZzE5Cmcy\nMApOdFJwNTAKKGRwNTEKZzIzCkkwMApzZzI0CmcyNQpzYnNTJ2VtYWlsJwpwNTIKVnJheW1vbmQu\neWVlQGRhdGF1bmJvdW5kLmNvbQpwNTMKc1MnaXNfc3VwZXJ1c2VyJwpwNTQKSTAwCnNTJ2lzX3N0\nYWZmJwpwNTUKSTAwCnNTJ2xhc3RfbG9naW4nCnA1NgpnMzMKKFMnXHgwN1x4ZTBceDA0XHgxNVx4\nMGM1KFx4MDBceDAwXHgwMCcKdFJwNTcKc1MncGFzc3dvcmQnCnA1OApWcGJrZGYyX3NoYTI1NiQx\nMjAwMCRwaFZNT3hCTDdKZlckM0d4WDRGOWlIYTJvM0hJVmhIUjJQMXVmUFVjVFpwTmtCenhPRDBh\nM0gwMD0KcDU5CnNnMjkKTDNMCnNTJ2RhdGVfam9pbmVkJwpwNjAKZzMzCihTJ1x4MDdceGRjXHgw\nM1xyXHgxM1x4MGIgXHgwMFx4MDBceDAwJwp0UnA2MQpzYnNTJ2FwcHJvdmVkJwpwNjIKSTAxCnNT\nJ3NlY3JldCcKcDYzClY5ZDNhNzc0Zi0wN2UxLTExZTYtYWFjYS0zYzE1YzJlYjYyYmMKcDY0CnNT\nJ3ByZWFwcHJvdmFsX2tleScKcDY1ClZjdXNfOEpOcHVXOFJNN0ttc1cKcDY2CnNTJ2RhdGVfcGF5\nbWVudCcKcDY3Ck5zUyd0eXBlJwpwNjgKTDJMCnNTJ3N0YXR1cycKcDY5ClZBY3RpdmUKcDcwCnNT\nJ19wcmVtaXVtX2NhY2hlJwpwNzEKZzcKKChWY29yZQpwNzIKUydQcmVtaXVtJwpwNzMKdChsZzEw\nCnRScDc0CihkcDc1ClMnZGVzY3JpcHRpb24nCnA3NgpWTm8gcHJlbWl1bSwgdGhhbmtzISAgSSBq\ndXN0IHdhbnQgdG8gaGVscCB1bmdsdWUuCnA3NwpzUydjcmVhdGVkJwpwNzgKZzMzCihTJ1x4MDdc\neGRiXHgwYlx4MTFceDE2XHgwMyVceDAwXHgwMFx4MDAnCnRScDc5CnNnMTcKZzE4CihnMTkKZzIw\nCk50UnA4MAooZHA4MQpnMjMKSTAwCnNnMjQKZzI1CnNic2cyNgpOc1MnYW1vdW50JwpwODIKZzM3\nCihTJzAnCnRScDgzCnNTJ2xpbWl0JwpwODQKTDBMCnNnNjgKVjAwCnA4NQpzZzI5CkwxNTBMCnNi\nc1MnZGF0ZV9leHBpcmVkJwpwODYKZzMzCihTJ1x4MDdceGUxXHgwNFx4MTVceDBjNTZceDAwXHgw\nMFx4MDAnCnRScDg3CnNTJ29mZmVyX2lkJwpwODgKTnNTJ2hvc3QnCnA4OQpWc3RyaXBlbGliCnA5\nMApzUydhbm9ueW1vdXMnCnA5MQpJMDAKc1MnZXhlY3V0aW9uJwpwOTIKTDBMCnNTJ2RhdGVfZXhl\nY3V0ZWQnCnA5MwpOc1MnX2NhbXBhaWduX2NhY2hlJwpwOTQKZzcKKChWY29yZQpwOTUKUydDYW1w\nYWlnbicKcDk2CnQobGcxMAp0UnA5NwooZHA5OApTJ2RvX3dhdGVybWFyaycKcDk5CkkwMQpzZzE3\nCmcxOAooZzE5CmcyMApOdFJwMTAwCihkcDEwMQpnMjMKSTAwCnNnMjQKZzI1CnNic1MndXNlX2Fk\nZF9hc2snCnAxMDIKSTAxCnNTJ2RlYWRsaW5lJwpwMTAzCmczMwooUydceDA3XHhkY1x4MDNceDA3\nXHgxMVx4MWE2XHgwMFx4MDBceDAwJwp0UnAxMDQKc2cyOQpMM0wKc1MnYW1hem9uX3JlY2VpdmVy\nJwpwMTA1ClYKc1MnZGV0YWlscycKcDEwNgpOc1MnX2N1cnJlbnRfdG90YWwnCnAxMDcKZzM3CihT\nJzUuMDAnCnRScDEwOApzUydwdWJsaXNoZXJfaWQnCnAxMDkKTnNnNTIKVgpzZzY5ClZBQ1RJVkUK\ncDExMApzZzc2ClZUZXN0IENhbXBhaWduCnAxMTEKc1MncGF5cGFsX3JlY2VpdmVyJwpwMTEyClZy\naDFfMTMxNzMzNjI1MV9iaXpAZ2x1ZWphci5jb20KcDExMwpzUydhY3RpdmF0ZWQnCnAxMTQKTnNT\nJ3Byb2JsZW1zJwpwMTE1CihscDExNgpzUydkb2xsYXJfcGVyX2RheScKcDExNwpOc1MnY2NfZGF0\nZV9pbml0aWFsJwpwMTE4Ck5zUyduYW1lJwpwMTE5ClZBIFdpemFyZCBvZiBFYXJ0aHNlYQpwMTIw\nCnNTJ3RhcmdldCcKcDEyMQpnMzcKKFMnMTYzNi4wMCcKdFJwMTIyCnNTJ2xpY2Vuc2UnCnAxMjMK\nVkNDIEJZLU5DLU5ECnAxMjQKc2c3OApnMzMKKFMnXHgwN1x4ZGNceDAzXHgwMlxyXHgwNFx4MDNc\neDAwXHgwMFx4MDAnCnRScDEyNQpzZzY4CkkxCnNTJ2VkaXRpb25faWQnCnAxMjYKTnNTJ3dvcmtf\naWQnCnAxMjcKTDQ4TApzUydsZWZ0JwpwMTI4CmczNwooUycxNjMxLjAwJwp0UnAxMjkKc2JzUydk\nYXRlX21vZGlmaWVkJwpwMTMwCmczMwooUydceDA3XHhlMFx4MDRceDE1XHgwYzU3XHgwZVx4ZmZc\neDFiJwp0UnAxMzEKc1MncmVhc29uJwpwMTMyCk5zUydwcmVtaXVtX2lkJwpwMTMzCkwxNTBMCnNn\nODIKZzM3CihTJzUnCnRScDEzNApzUydlcnJvcicKcDEzNQpOc1MnZGF0ZV9jcmVhdGVkJwpwMTM2\nCmczMwooUydceDA3XHhlMFx4MDRceDE1XHgwYzUuXHgwMFx4MDBceDAwJwp0UnAxMzcKc2JzSTAx\nCk50cDEzOAphLg==\n'),(7,'KGxwMQooTDNMClMncGxlZGdlX3N0YXR1c19jaGFuZ2UnCnAyCihkcDMKUyd1cF9vcl9kb3duJwpw\nNApTJ2luY3JlYXNlZCcKcDUKc1MndHJhbnNhY3Rpb24nCnA2CmNkamFuZ28uZGIubW9kZWxzLmJh\nc2UKbW9kZWxfdW5waWNrbGUKcDcKKChWcGF5bWVudApwOApTJ1RyYW5zYWN0aW9uJwpwOQp0KGxj\nZGphbmdvLmRiLm1vZGVscy5iYXNlCnNpbXBsZV9jbGFzc19mYWN0b3J5CnAxMAp0UnAxMQooZHAx\nMgpTJ2V4dHJhJwpwMTMKKGRwMTQKc1MncGF5X2tleScKcDE1Ck5zUydyZWNlaXB0JwpwMTYKTnNT\nJ19zdGF0ZScKcDE3CmNjb3B5X3JlZwpfcmVjb25zdHJ1Y3RvcgpwMTgKKGNkamFuZ28uZGIubW9k\nZWxzLmJhc2UKTW9kZWxTdGF0ZQpwMTkKY19fYnVpbHRpbl9fCm9iamVjdApwMjAKTnRScDIxCihk\ncDIyClMnYWRkaW5nJwpwMjMKSTAwCnNTJ2RiJwpwMjQKUydkZWZhdWx0JwpwMjUKc2JzUydjYW1w\nYWlnbl9pZCcKcDI2CkwzTApzUydjdXJyZW5jeScKcDI3ClZVU0QKcDI4CnNTJ2lkJwpwMjkKTDFM\nCnNTJ2xvY2FsX3N0YXR1cycKcDMwClZOT05FCnAzMQpzUydkYXRlX2F1dGhvcml6ZWQnCnAzMgpj\nZGF0ZXRpbWUKZGF0ZXRpbWUKcDMzCihTJ1x4MDdceGUwXHgwNFx4MTVceDBjNTZceDAwXHgwMFx4\nMDAnCnRScDM0CnNTJ3VzZXJfaWQnCnAzNQpMM0wKc1MnbWF4X2Ftb3VudCcKcDM2CmNkZWNpbWFs\nCkRlY2ltYWwKcDM3CihTJzEwLjAwJwp0UnAzOApzUydfb2ZmZXJfY2FjaGUnCnAzOQpOc1MnX3Vz\nZXJfY2FjaGUnCnA0MApnNwooKFZhdXRoCnA0MQpTJ1VzZXInCnA0Mgp0KGxnMTAKdFJwNDMKKGRw\nNDQKUyd1c2VybmFtZScKcDQ1ClZyZGh5ZWV0ZXN0CnA0NgpzUydmaXJzdF9uYW1lJwpwNDcKVgpz\nUydsYXN0X25hbWUnCnA0OApWCnNTJ2lzX2FjdGl2ZScKcDQ5CkkwMQpzZzE3CmcxOAooZzE5Cmcy\nMApOdFJwNTAKKGRwNTEKZzIzCkkwMApzZzI0CmcyNQpzYnNTJ2VtYWlsJwpwNTIKVnJheW1vbmQu\neWVlQGRhdGF1bmJvdW5kLmNvbQpwNTMKc1MnaXNfc3VwZXJ1c2VyJwpwNTQKSTAwCnNTJ2lzX3N0\nYWZmJwpwNTUKSTAwCnNTJ2xhc3RfbG9naW4nCnA1NgpnMzMKKFMnXHgwN1x4ZTBceDA0XHgxNVx4\nMGM1KFx4MDBceDAwXHgwMCcKdFJwNTcKc1MncGFzc3dvcmQnCnA1OApWcGJrZGYyX3NoYTI1NiQx\nMjAwMCRwaFZNT3hCTDdKZlckM0d4WDRGOWlIYTJvM0hJVmhIUjJQMXVmUFVjVFpwTmtCenhPRDBh\nM0gwMD0KcDU5CnNnMjkKTDNMCnNTJ2RhdGVfam9pbmVkJwpwNjAKZzMzCihTJ1x4MDdceGRjXHgw\nM1xyXHgxM1x4MGIgXHgwMFx4MDBceDAwJwp0UnA2MQpzYnNTJ2FwcHJvdmVkJwpwNjIKSTAxCnNT\nJ3NlY3JldCcKcDYzClY5ZDNhNzc0Zi0wN2UxLTExZTYtYWFjYS0zYzE1YzJlYjYyYmMKcDY0CnNT\nJ3ByZWFwcHJvdmFsX2tleScKcDY1ClZjdXNfOEpOcHVXOFJNN0ttc1cKcDY2CnNTJ2RhdGVfcGF5\nbWVudCcKcDY3Ck5zUyd0eXBlJwpwNjgKTDJMCnNTJ3N0YXR1cycKcDY5ClZBY3RpdmUKcDcwCnNT\nJ19wcmVtaXVtX2NhY2hlJwpwNzEKZzcKKChWY29yZQpwNzIKUydQcmVtaXVtJwpwNzMKdChsZzEw\nCnRScDc0CihkcDc1ClMnZGVzY3JpcHRpb24nCnA3NgpWTm8gcHJlbWl1bSwgdGhhbmtzISAgSSBq\ndXN0IHdhbnQgdG8gaGVscCB1bmdsdWUuCnA3NwpzUydjcmVhdGVkJwpwNzgKZzMzCihTJ1x4MDdc\neGRiXHgwYlx4MTFceDE2XHgwMyVceDAwXHgwMFx4MDAnCnRScDc5CnNnMTcKZzE4CihnMTkKZzIw\nCk50UnA4MAooZHA4MQpnMjMKSTAwCnNnMjQKZzI1CnNic2cyNgpOc1MnYW1vdW50JwpwODIKZzM3\nCihTJzAnCnRScDgzCnNTJ2xpbWl0JwpwODQKTDBMCnNnNjgKVjAwCnA4NQpzZzI5CkwxNTBMCnNi\nc1MnZGF0ZV9leHBpcmVkJwpwODYKZzMzCihTJ1x4MDdceGUxXHgwNFx4MTVceDBjNTZceDAwXHgw\nMFx4MDAnCnRScDg3CnNTJ29mZmVyX2lkJwpwODgKTnNTJ2hvc3QnCnA4OQpWc3RyaXBlbGliCnA5\nMApzUydhbm9ueW1vdXMnCnA5MQpJMDAKc1MnZXhlY3V0aW9uJwpwOTIKTDBMCnNTJ2RhdGVfZXhl\nY3V0ZWQnCnA5MwpOc1MnX2NhbXBhaWduX2NhY2hlJwpwOTQKZzcKKChWY29yZQpwOTUKUydDYW1w\nYWlnbicKcDk2CnQobGcxMAp0UnA5NwooZHA5OApTJ2RvX3dhdGVybWFyaycKcDk5CkkwMQpzZzE3\nCmcxOAooZzE5CmcyMApOdFJwMTAwCihkcDEwMQpnMjMKSTAwCnNnMjQKZzI1CnNic1MndXNlX2Fk\nZF9hc2snCnAxMDIKSTAxCnNTJ2RlYWRsaW5lJwpwMTAzCmczMwooUydceDA3XHhkY1x4MDNceDA3\nXHgxMVx4MWE2XHgwMFx4MDBceDAwJwp0UnAxMDQKc2cyOQpMM0wKc1MnYW1hem9uX3JlY2VpdmVy\nJwpwMTA1ClYKc1MnZGV0YWlscycKcDEwNgpOc1MnX2N1cnJlbnRfdG90YWwnCnAxMDcKZzM3CihT\nJzI1LjAwJwp0UnAxMDgKc1MncHVibGlzaGVyX2lkJwpwMTA5Ck5zZzUyClYKc2c2OQpWQUNUSVZF\nCnAxMTAKc2c3NgpWVGVzdCBDYW1wYWlnbgpwMTExCnNTJ3BheXBhbF9yZWNlaXZlcicKcDExMgpW\ncmgxXzEzMTczMzYyNTFfYml6QGdsdWVqYXIuY29tCnAxMTMKc1MnYWN0aXZhdGVkJwpwMTE0Ck5z\nUydwcm9ibGVtcycKcDExNQoobHAxMTYKc1MnZG9sbGFyX3Blcl9kYXknCnAxMTcKTnNTJ2NjX2Rh\ndGVfaW5pdGlhbCcKcDExOApOc1MnbmFtZScKcDExOQpWQSBXaXphcmQgb2YgRWFydGhzZWEKcDEy\nMApzUyd0YXJnZXQnCnAxMjEKZzM3CihTJzE2MzYuMDAnCnRScDEyMgpzUydsaWNlbnNlJwpwMTIz\nClZDQyBCWS1OQy1ORApwMTI0CnNnNzgKZzMzCihTJ1x4MDdceGRjXHgwM1x4MDJcclx4MDRceDAz\nXHgwMFx4MDBceDAwJwp0UnAxMjUKc2c2OApJMQpzUydlZGl0aW9uX2lkJwpwMTI2Ck5zUyd3b3Jr\nX2lkJwpwMTI3Ckw0OEwKc1MnbGVmdCcKcDEyOApnMzcKKFMnMTYxMS4wMCcKdFJwMTI5CnNic1Mn\nZGF0ZV9tb2RpZmllZCcKcDEzMApnMzMKKFMnXHgwN1x4ZTBceDA0XHgxNVx4MGM1OFxyY1x4YjMn\nCnRScDEzMQpzUydyZWFzb24nCnAxMzIKTnNTJ3ByZW1pdW1faWQnCnAxMzMKTDE1MEwKc2c4Mgpn\nMzcKKFMnMjUnCnAxMzQKdFJwMTM1CnNTJ2Vycm9yJwpwMTM2Ck5zUydkYXRlX2NyZWF0ZWQnCnAx\nMzcKZzMzCihTJ1x4MDdceGUwXHgwNFx4MTVceDBjNS5ceDAwXHgwMFx4MDAnCnRScDEzOApzYnNJ\nMDEKTnRwMTM5CmEu\n'),(8,'KGxwMQooTDNMClMncGxlZGdlX3N0YXR1c19jaGFuZ2UnCnAyCihkcDMKUyd1cF9vcl9kb3duJwpw\nNApTJ2NhbmNlbGVkJwpwNQpzUyd0cmFuc2FjdGlvbicKcDYKY2RqYW5nby5kYi5tb2RlbHMuYmFz\nZQptb2RlbF91bnBpY2tsZQpwNwooKFZwYXltZW50CnA4ClMnVHJhbnNhY3Rpb24nCnA5CnQobGNk\namFuZ28uZGIubW9kZWxzLmJhc2UKc2ltcGxlX2NsYXNzX2ZhY3RvcnkKcDEwCnRScDExCihkcDEy\nClMnZXh0cmEnCnAxMwooZHAxNApzUydwYXlfa2V5JwpwMTUKTnNTJ3JlY2VpcHQnCnAxNgpOc1Mn\nX3N0YXRlJwpwMTcKY2NvcHlfcmVnCl9yZWNvbnN0cnVjdG9yCnAxOAooY2RqYW5nby5kYi5tb2Rl\nbHMuYmFzZQpNb2RlbFN0YXRlCnAxOQpjX19idWlsdGluX18Kb2JqZWN0CnAyMApOdFJwMjEKKGRw\nMjIKUydhZGRpbmcnCnAyMwpJMDAKc1MnZGInCnAyNApTJ2RlZmF1bHQnCnAyNQpzYnNTJ2NhbXBh\naWduX2lkJwpwMjYKTDNMCnNTJ2N1cnJlbmN5JwpwMjcKVlVTRApwMjgKc1MnaWQnCnAyOQpMMUwK\nc1MnbG9jYWxfc3RhdHVzJwpwMzAKVk5PTkUKcDMxCnNTJ2RhdGVfYXV0aG9yaXplZCcKcDMyCmNk\nYXRldGltZQpkYXRldGltZQpwMzMKKFMnXHgwN1x4ZTBceDA0XHgxNVx4MGM1Nlx4MDBceDAwXHgw\nMCcKdFJwMzQKc1MndXNlcl9pZCcKcDM1CkwzTApzUydtYXhfYW1vdW50JwpwMzYKY2RlY2ltYWwK\nRGVjaW1hbApwMzcKKFMnMTAuMDAnCnRScDM4CnNTJ191c2VyX2NhY2hlJwpwMzkKZzcKKChWYXV0\naApwNDAKUydVc2VyJwpwNDEKdChsZzEwCnRScDQyCihkcDQzClMndXNlcm5hbWUnCnA0NApWcmRo\neWVldGVzdApwNDUKc1MnZmlyc3RfbmFtZScKcDQ2ClYKc1MnbGFzdF9uYW1lJwpwNDcKVgpzUydf\ncHJvZmlsZV9jYWNoZScKcDQ4Cmc3CigoVmNvcmUKcDQ5ClMnVXNlclByb2ZpbGUnCnA1MAp0KGxn\nMTAKdFJwNTEKKGRwNTIKUydnb29kcmVhZHNfYXV0aF9zZWNyZXQnCnA1MwpOc2czNQpMM0wKc1Mn\nZ29vZHJlYWRzX3VzZXJfbmFtZScKcDU0Ck5zUydjcmVhdGVkJwpwNTUKZzMzCihTJ1x4MDdceGRj\nXHgwM1xyXHgxM1x4MGIgXHgwMFx4MDBceDAwJwp0UnA1NgpzUydhdmF0YXJfc291cmNlJwpwNTcK\nTnNTJ3RhZ2xpbmUnCnA1OApWCnNTJ2tpbmRsZV9lbWFpbCcKcDU5ClYKc2cxNwpnMTgKKGcxOQpn\nMjAKTnRScDYwCihkcDYxCmcyMwpJMDAKc2cyNApnMjUKc2JzUyd0d2l0dGVyX2lkJwpwNjIKVgpz\nUydwaWNfdXJsJwpwNjMKVgpzUydnb29kcmVhZHNfdXNlcl9pZCcKcDY0Ck5zZzM5Cmc0MgpzUydn\nb29kcmVhZHNfdXNlcl9saW5rJwpwNjUKTnNTJ2ZhY2Vib29rX2lkJwpwNjYKTnNTJ2xpYnJhcnl0\naGluZ19pZCcKcDY3ClYKc1MnaG9tZV91cmwnCnA2OApWCnNTJ2dvb2RyZWFkc19hdXRoX3Rva2Vu\nJwpwNjkKTnNnMjkKTDNMCnNic1MnaXNfYWN0aXZlJwpwNzAKSTAxCnNnMTcKZzE4CihnMTkKZzIw\nCk50UnA3MQooZHA3MgpnMjMKSTAwCnNnMjQKZzI1CnNic1MnZW1haWwnCnA3MwpWcmF5bW9uZC55\nZWVAZGF0YXVuYm91bmQuY29tCnA3NApzUydpc19zdXBlcnVzZXInCnA3NQpJMDAKc1MnaXNfc3Rh\nZmYnCnA3NgpJMDAKc1MnbGFzdF9sb2dpbicKcDc3CmczMwooUydceDA3XHhlMFx4MDRceDE1XHgw\nYzUoXHgwMFx4MDBceDAwJwp0UnA3OApzUydwYXNzd29yZCcKcDc5ClZwYmtkZjJfc2hhMjU2JDEy\nMDAwJHBoVk1PeEJMN0pmVyQzR3hYNEY5aUhhMm8zSElWaEhSMlAxdWZQVWNUWnBOa0J6eE9EMGEz\nSDAwPQpwODAKc2cyOQpMM0wKc1MnZGF0ZV9qb2luZWQnCnA4MQpnMzMKKFMnXHgwN1x4ZGNceDAz\nXHJceDEzXHgwYiBceDAwXHgwMFx4MDAnCnRScDgyCnNic1MnYXBwcm92ZWQnCnA4MwpJMDEKc1Mn\nc2VjcmV0JwpwODQKVjlkM2E3NzRmLTA3ZTEtMTFlNi1hYWNhLTNjMTVjMmViNjJiYwpwODUKc1Mn\ncHJlYXBwcm92YWxfa2V5JwpwODYKVmN1c184Sk5wdVc4Uk03S21zVwpwODcKc1MnZGF0ZV9wYXlt\nZW50JwpwODgKTnNTJ3R5cGUnCnA4OQpMMkwKc1Mnc3RhdHVzJwpwOTAKUydDYW5jZWxlZCcKcDkx\nCnNTJ2RhdGVfZXhwaXJlZCcKcDkyCmczMwooUydceDA3XHhlMVx4MDRceDE1XHgwYzU2XHgwMFx4\nMDBceDAwJwp0UnA5MwpzUydvZmZlcl9pZCcKcDk0Ck5zUydob3N0JwpwOTUKVnN0cmlwZWxpYgpw\nOTYKc1MnYW5vbnltb3VzJwpwOTcKSTAwCnNTJ2V4ZWN1dGlvbicKcDk4CkwwTApzUydkYXRlX2V4\nZWN1dGVkJwpwOTkKTnNTJ19jYW1wYWlnbl9jYWNoZScKcDEwMApnNwooKFZjb3JlCnAxMDEKUydD\nYW1wYWlnbicKcDEwMgp0KGxnMTAKdFJwMTAzCihkcDEwNApTJ2RvX3dhdGVybWFyaycKcDEwNQpJ\nMDEKc2cxNwpnMTgKKGcxOQpnMjAKTnRScDEwNgooZHAxMDcKZzIzCkkwMApzZzI0CmcyNQpzYnNT\nJ3VzZV9hZGRfYXNrJwpwMTA4CkkwMQpzUydkZWFkbGluZScKcDEwOQpnMzMKKFMnXHgwN1x4ZGNc\neDAzXHgwN1x4MTFceDFhNlx4MDBceDAwXHgwMCcKdFJwMTEwCnNnMjkKTDNMCnNTJ2FtYXpvbl9y\nZWNlaXZlcicKcDExMQpWCnNTJ2RldGFpbHMnCnAxMTIKTnNTJ19jdXJyZW50X3RvdGFsJwpwMTEz\nCmczNwooUycwLjAwJwp0UnAxMTQKc1MncHVibGlzaGVyX2lkJwpwMTE1Ck5zZzczClYKc2c5MApW\nQUNUSVZFCnAxMTYKc1MnZGVzY3JpcHRpb24nCnAxMTcKVlRlc3QgQ2FtcGFpZ24KcDExOApzUydw\nYXlwYWxfcmVjZWl2ZXInCnAxMTkKVnJoMV8xMzE3MzM2MjUxX2JpekBnbHVlamFyLmNvbQpwMTIw\nCnNTJ2FjdGl2YXRlZCcKcDEyMQpOc1MncHJvYmxlbXMnCnAxMjIKKGxwMTIzCnNTJ2RvbGxhcl9w\nZXJfZGF5JwpwMTI0Ck5zUydjY19kYXRlX2luaXRpYWwnCnAxMjUKTnNTJ25hbWUnCnAxMjYKVkEg\nV2l6YXJkIG9mIEVhcnRoc2VhCnAxMjcKc1MndGFyZ2V0JwpwMTI4CmczNwooUycxNjM2LjAwJwp0\nUnAxMjkKc1MnbGljZW5zZScKcDEzMApWQ0MgQlktTkMtTkQKcDEzMQpzZzU1CmczMwooUydceDA3\nXHhkY1x4MDNceDAyXHJceDA0XHgwM1x4MDBceDAwXHgwMCcKdFJwMTMyCnNnODkKSTEKc1MnZWRp\ndGlvbl9pZCcKcDEzMwpOc1Mnd29ya19pZCcKcDEzNApMNDhMCnNTJ2xlZnQnCnAxMzUKZzM3CihT\nJzE2MzYuMDAnCnRScDEzNgpzYnNTJ2RhdGVfbW9kaWZpZWQnCnAxMzcKZzMzCihTJ1x4MDdceGUw\nXHgwNFx4MTVceDBjNTlceDBjXHhmZFx4ZmEnCnRScDEzOApzUydyZWFzb24nCnAxMzkKTnNTJ3By\nZW1pdW1faWQnCnAxNDAKTDE1MEwKc1MnYW1vdW50JwpwMTQxCmczNwooUycyNS4wMCcKdFJwMTQy\nCnNTJ2Vycm9yJwpwMTQzCk5zUydkYXRlX2NyZWF0ZWQnCnAxNDQKZzMzCihTJ1x4MDdceGUwXHgw\nNFx4MTVceDBjNS5ceDAwXHgwMFx4MDAnCnRScDE0NQpzYnNJMDEKTnRwMTQ2CmEu\n'),(9,'KGxwMQou\n'),(10,'KGxwMQooTDdMClMnbGlicmFyeV9qb2luJwpwMgooZHAzClMndXNlcicKcDQKY2RqYW5nby5kYi5t\nb2RlbHMuYmFzZQptb2RlbF91bnBpY2tsZQpwNQooKFZhdXRoCnA2ClMnVXNlcicKcDcKdChsY2Rq\nYW5nby5kYi5tb2RlbHMuYmFzZQpzaW1wbGVfY2xhc3NfZmFjdG9yeQpwOAp0UnA5CihkcDEwClMn\ndXNlcm5hbWUnCnAxMQpWcnlsaWJyYXJ5CnAxMgpzUydmaXJzdF9uYW1lJwpwMTMKVgpzUydsYXN0\nX25hbWUnCnAxNApWCnNTJ19wcm9maWxlX2NhY2hlJwpwMTUKZzUKKChWY29yZQpwMTYKUydVc2Vy\nUHJvZmlsZScKcDE3CnQobGc4CnRScDE4CihkcDE5ClMnZ29vZHJlYWRzX2F1dGhfc2VjcmV0Jwpw\nMjAKTnNTJ3VzZXJfaWQnCnAyMQpMN0wKc1MnZ29vZHJlYWRzX3VzZXJfbmFtZScKcDIyCk5zUydj\ncmVhdGVkJwpwMjMKY2RhdGV0aW1lCmRhdGV0aW1lCnAyNAooUydceDA3XHhlMFx4MDRceDE1XHgw\nYzY3XHgwYlx4ZDJceGM3Jwp0UnAyNQpzUydhdmF0YXJfc291cmNlJwpwMjYKSTQKc1MndGFnbGlu\nZScKcDI3ClYKc1MnX3VzZXJfY2FjaGUnCnAyOApnOQpzUydfc3RhdGUnCnAyOQpjY29weV9yZWcK\nX3JlY29uc3RydWN0b3IKcDMwCihjZGphbmdvLmRiLm1vZGVscy5iYXNlCk1vZGVsU3RhdGUKcDMx\nCmNfX2J1aWx0aW5fXwpvYmplY3QKcDMyCk50UnAzMwooZHAzNApTJ2FkZGluZycKcDM1CkkwMApz\nUydkYicKcDM2ClMnZGVmYXVsdCcKcDM3CnNic1MndHdpdHRlcl9pZCcKcDM4ClYKc1MncGljX3Vy\nbCcKcDM5ClYKc1MnZ29vZHJlYWRzX3VzZXJfaWQnCnA0MApOc1Mna2luZGxlX2VtYWlsJwpwNDEK\nVgpzUydnb29kcmVhZHNfdXNlcl9saW5rJwpwNDIKTnNTJ2ZhY2Vib29rX2lkJwpwNDMKTnNTJ2xp\nYnJhcnl0aGluZ19pZCcKcDQ0ClYKc1MnaG9tZV91cmwnCnA0NQpWCnNTJ2dvb2RyZWFkc19hdXRo\nX3Rva2VuJwpwNDYKTnNTJ2lkJwpwNDcKTDdMCnNic1MnaXNfYWN0aXZlJwpwNDgKSTAxCnNnMjkK\nZzMwCihnMzEKZzMyCk50UnA0OQooZHA1MApnMzUKSTAwCnNnMzYKZzM3CnNic1MnX2NyZWRpdF9j\nYWNoZScKcDUxCmc1CigoVnBheW1lbnQKcDUyClMnQ3JlZGl0JwpwNTMKdChsZzgKdFJwNTQKKGRw\nNTUKZzIxCkw3TApzUydwbGVkZ2VkJwpwNTYKY2RlY2ltYWwKRGVjaW1hbApwNTcKKFMnMC4wMCcK\ndFJwNTgKc2cyOQpnMzAKKGczMQpnMzIKTnRScDU5CihkcDYwCmczNQpJMDAKc2czNgpnMzcKc2Jz\nZzQ3Ckw3TApzUydsYXN0X2FjdGl2aXR5JwpwNjEKZzI0CihTJ1x4MDdceGUwXHgwNFx4MTVceDBj\nNjdceDBiXHhjYUEnCnRScDYyCnNTJ2JhbGFuY2UnCnA2MwpnNTcKKFMnMC4wMCcKdFJwNjQKc2cy\nOApnOQpzYnNTJ2VtYWlsJwpwNjUKVnJ5bGlicmFyeUBleGFtcGxlLm9yZwpwNjYKc1MnX2FwaV9r\nZXlfY2FjaGUnCnA2NwpnNQooKFZ0YXN0eXBpZQpwNjgKUydBcGlLZXknCnA2OQp0KGxnOAp0UnA3\nMAooZHA3MQpnMjEKTDdMCnNnMjMKZzI0CihTJ1x4MDdceGUwXHgwNFx4MTVceDBjNjdceDBiXHhk\nNmonCnRScDcyCnNnMjgKZzkKc2cyOQpnMzAKKGczMQpnMzIKTnRScDczCihkcDc0CmczNQpJMDAK\nc2czNgpnMzcKc2JzUydrZXknCnA3NQpTJzgzYzhjNTVkNGQ3MjIwZmViN2U1ZWQzOGMzNTI0MzBi\nYTQ0MzE5MjYnCnA3NgpzZzQ3Ckw3TApzYnNTJ2lzX3N1cGVydXNlcicKcDc3CkkwMApzUydpc19z\ndGFmZicKcDc4CkkwMApzUydsYXN0X2xvZ2luJwpwNzkKZzI0CihTJ1x4MDdceGUwXHgwNFx4MTVc\neDBjNjdceDBiXHhjMlx4OTUnCnRScDgwCnNTJ193aXNobGlzdF9jYWNoZScKcDgxCmc1CigoVmNv\ncmUKcDgyClMnV2lzaGxpc3QnCnA4Mwp0KGxnOAp0UnA4NAooZHA4NQpnMjEKTDdMCnNnMjgKZzkK\nc2cyOQpnMzAKKGczMQpnMzIKTnRScDg2CihkcDg3CmczNQpJMDAKc2czNgpnMzcKc2JzZzQ3Ckw3\nTApzZzIzCmcyNAooUydceDA3XHhlMFx4MDRceDE1XHgwYzY3XHgwYlx4Y2VceGE3Jwp0UnA4OApz\nYnNTJ19saWJyYXJ5X2NhY2hlJwpwODkKZzUKKChWbGlicmFyeWF1dGgKcDkwClMnTGlicmFyeScK\ncDkxCnQobGc4CnRScDkyCihkcDkzCmcyMQpMN0wKc1MnbmFtZScKcDk0ClZSWSBMaWJyYXJ5CnA5\nNQpzUydfb3duZXJfY2FjaGUnCnA5NgpnMzAKKGNkamFuZ28uY29udHJpYi5hdXRoLm1vZGVscwpV\nc2VyCnA5NwpnMzIKTnRScDk4CihkcDk5CmcxMQpWeWVlLWV4YW1wbGUKcDEwMApzZzEzClYKc2cx\nNApWCnNnNDgKSTAxCnNnMjkKZzMwCihnMzEKZzMyCk50UnAxMDEKKGRwMTAyCmczNQpJMDAKc2cz\nNgpnMzcKc2JzZzY1ClZ5ZWVAZXhhbXBsZS5vcmcKcDEwMwpzZzc3CkkwMApzZzc4CkkwMApzZzc5\nCmcyNAooUydceDA3XHhlMFx4MDRceDE1XHgwYzY2XHgwMFx4MDBceDAwJwp0UnAxMDQKc1MncGFz\nc3dvcmQnCnAxMDUKVnBia2RmMl9zaGEyNTYkMTIwMDAkNmVsTDBsdHhKUE9ZJFBFQmFWZE5FYWlr\ncXhQWFhaWCtHQUpCYTBPaTBIaUVGdjBHa1hOcEI0UWM9CnAxMDYKc2c0NwpMNUwKc1MnZGF0ZV9q\nb2luZWQnCnAxMDcKZzI0CihTJ1x4MDdceGUwXHgwNFx4MTVceDBjNFx4MDBceDAwXHgwMFx4MDAn\nCnRScDEwOApzYnNnMjgKZzkKc2cyOQpnMzAKKGczMQpnMzIKTnRScDEwOQooZHAxMTAKZzM1Ckkw\nMApzZzM2CmczNwpzYnNTJ293bmVyX2lkJwpwMTExCkw1TApzUydhcHByb3ZlZCcKcDExMgpJMDAK\nc1MnX2dyb3VwX2NhY2hlJwpwMTEzCmc1CigoVmF1dGgKcDExNApTJ0dyb3VwJwpwMTE1CnQobGc4\nCnRScDExNgooZHAxMTcKZzg5Cmc5MgpzZzI5CmczMAooZzMxCmczMgpOdFJwMTE4CihkcDExOQpn\nMzUKSTAwCnNnMzYKZzM3CnNic2c0NwpMMUwKc2c5NApnMTIKc2JzUydncm91cF9pZCcKcDEyMApM\nMUwKc2c0NwpMMUwKc1MnYmFja2VuZCcKcDEyMQpWZW1haWwKcDEyMgpzYnNnMTA1ClYKc2c0NwpM\nN0wKc2cxMDcKZzI0CihTJ1x4MDdceGUwXHgwNFx4MTVceDBjNjdceDBiXHhjMlx4YjMnCnRScDEy\nMwpzYnNTJ2xpYnJhcnknCnAxMjQKZzkyCnNJMDEKTnRwMTI1CmEoTDdMCmcyCmczCkkwMQpOdHAx\nMjYKYS4=\n'),(11,'KGxwMQooTDVMClMnbGlicmFyeV9qb2luJwpwMgooZHAzClMndXNlcicKcDQKY2NvcHlfcmVnCl9y\nZWNvbnN0cnVjdG9yCnA1CihjZGphbmdvLmNvbnRyaWIuYXV0aC5tb2RlbHMKVXNlcgpwNgpjX19i\ndWlsdGluX18Kb2JqZWN0CnA3Ck50UnA4CihkcDkKUyd1c2VybmFtZScKcDEwClZ5ZWUtZXhhbXBs\nZQpwMTEKc1MnZmlyc3RfbmFtZScKcDEyClYKc1MnbGFzdF9uYW1lJwpwMTMKVgpzUydpc19hY3Rp\ndmUnCnAxNApJMDEKc1MnX3N0YXRlJwpwMTUKZzUKKGNkamFuZ28uZGIubW9kZWxzLmJhc2UKTW9k\nZWxTdGF0ZQpwMTYKZzcKTnRScDE3CihkcDE4ClMnYWRkaW5nJwpwMTkKSTAwCnNTJ2RiJwpwMjAK\nUydkZWZhdWx0JwpwMjEKc2JzUydlbWFpbCcKcDIyClZ5ZWVAZXhhbXBsZS5vcmcKcDIzCnNTJ2lz\nX3N1cGVydXNlcicKcDI0CkkwMApzUydpc19zdGFmZicKcDI1CkkwMApzUydsYXN0X2xvZ2luJwpw\nMjYKY2RhdGV0aW1lCmRhdGV0aW1lCnAyNwooUydceDA3XHhlMFx4MDRceDE1XHgwYzY2XHgwMFx4\nMDBceDAwJwp0UnAyOApzUydwYXNzd29yZCcKcDI5ClZwYmtkZjJfc2hhMjU2JDEyMDAwJDZlbEww\nbHR4SlBPWSRQRUJhVmRORWFpa3F4UFhYWlgrR0FKQmEwT2kwSGlFRnYwR2tYTnBCNFFjPQpwMzAK\nc1MnaWQnCnAzMQpMNUwKc1MnZGF0ZV9qb2luZWQnCnAzMgpnMjcKKFMnXHgwN1x4ZTBceDA0XHgx\nNVx4MGM0XHgwMFx4MDBceDAwXHgwMCcKdFJwMzMKc2JzUydsaWJyYXJ5JwpwMzQKY2RqYW5nby5k\nYi5tb2RlbHMuYmFzZQptb2RlbF91bnBpY2tsZQpwMzUKKChWbGlicmFyeWF1dGgKcDM2ClMnTGli\ncmFyeScKcDM3CnQobGNkamFuZ28uZGIubW9kZWxzLmJhc2UKc2ltcGxlX2NsYXNzX2ZhY3RvcnkK\ncDM4CnRScDM5CihkcDQwClMndXNlcl9pZCcKcDQxCkw3TApzUyduYW1lJwpwNDIKVlJZIExpYnJh\ncnkKcDQzCnNTJ19vd25lcl9jYWNoZScKcDQ0Cmc4CnNTJ191c2VyX2NhY2hlJwpwNDUKZzM1Cigo\nVmF1dGgKcDQ2ClMnVXNlcicKcDQ3CnQobGczOAp0UnA0OAooZHA0OQpnMTAKVnJ5bGlicmFyeQpw\nNTAKc2cxMgpWCnNnMTMKVgpzUydfcHJvZmlsZV9jYWNoZScKcDUxCmczNQooKFZjb3JlCnA1MgpT\nJ1VzZXJQcm9maWxlJwpwNTMKdChsZzM4CnRScDU0CihkcDU1ClMnZ29vZHJlYWRzX2F1dGhfc2Vj\ncmV0JwpwNTYKTnNnNDEKTDdMCnNTJ2dvb2RyZWFkc191c2VyX25hbWUnCnA1NwpOc1MnY3JlYXRl\nZCcKcDU4CmcyNwooUydceDA3XHhlMFx4MDRceDE1XHgwYzY3XHgwYlx4ZDJceGM3Jwp0UnA1OQpz\nUydhdmF0YXJfc291cmNlJwpwNjAKSTQKc1MndGFnbGluZScKcDYxClYKc2c0NQpnNDgKc2cxNQpn\nNQooZzE2Cmc3Ck50UnA2MgooZHA2MwpnMTkKSTAwCnNnMjAKZzIxCnNic1MndHdpdHRlcl9pZCcK\ncDY0ClYKc1MncGljX3VybCcKcDY1ClYKc1MnZ29vZHJlYWRzX3VzZXJfaWQnCnA2NgpOc1Mna2lu\nZGxlX2VtYWlsJwpwNjcKVgpzUydnb29kcmVhZHNfdXNlcl9saW5rJwpwNjgKTnNTJ2ZhY2Vib29r\nX2lkJwpwNjkKTnNTJ2xpYnJhcnl0aGluZ19pZCcKcDcwClYKc1MnaG9tZV91cmwnCnA3MQpWCnNT\nJ2dvb2RyZWFkc19hdXRoX3Rva2VuJwpwNzIKTnNnMzEKTDdMCnNic2cxNApJMDEKc2cxNQpnNQoo\nZzE2Cmc3Ck50UnA3MwooZHA3NApnMTkKSTAwCnNnMjAKZzIxCnNic1MnX2NyZWRpdF9jYWNoZScK\ncDc1CmczNQooKFZwYXltZW50CnA3NgpTJ0NyZWRpdCcKcDc3CnQobGczOAp0UnA3OAooZHA3OQpn\nNDEKTDdMCnNTJ3BsZWRnZWQnCnA4MApjZGVjaW1hbApEZWNpbWFsCnA4MQooUycwLjAwJwp0UnA4\nMgpzZzE1Cmc1CihnMTYKZzcKTnRScDgzCihkcDg0CmcxOQpJMDAKc2cyMApnMjEKc2JzZzMxCkw3\nTApzUydsYXN0X2FjdGl2aXR5JwpwODUKZzI3CihTJ1x4MDdceGUwXHgwNFx4MTVceDBjNjdceDBi\nXHhjYUEnCnRScDg2CnNTJ2JhbGFuY2UnCnA4NwpnODEKKFMnMC4wMCcKdFJwODgKc2c0NQpnNDgK\nc2JzZzIyClZyeWxpYnJhcnlAZXhhbXBsZS5vcmcKcDg5CnNTJ19hcGlfa2V5X2NhY2hlJwpwOTAK\nZzM1CigoVnRhc3R5cGllCnA5MQpTJ0FwaUtleScKcDkyCnQobGczOAp0UnA5MwooZHA5NApnNDEK\nTDdMCnNnNTgKZzI3CihTJ1x4MDdceGUwXHgwNFx4MTVceDBjNjdceDBiXHhkNmonCnRScDk1CnNn\nNDUKZzQ4CnNnMTUKZzUKKGcxNgpnNwpOdFJwOTYKKGRwOTcKZzE5CkkwMApzZzIwCmcyMQpzYnNT\nJ2tleScKcDk4ClMnODNjOGM1NWQ0ZDcyMjBmZWI3ZTVlZDM4YzM1MjQzMGJhNDQzMTkyNicKcDk5\nCnNnMzEKTDdMCnNic2cyNApJMDAKc2cyNQpJMDAKc2cyNgpnMjcKKFMnXHgwN1x4ZTBceDA0XHgx\nNVx4MGM2N1x4MGJceGMyXHg5NScKdFJwMTAwCnNTJ193aXNobGlzdF9jYWNoZScKcDEwMQpnMzUK\nKChWY29yZQpwMTAyClMnV2lzaGxpc3QnCnAxMDMKdChsZzM4CnRScDEwNAooZHAxMDUKZzQxCkw3\nTApzZzQ1Cmc0OApzZzE1Cmc1CihnMTYKZzcKTnRScDEwNgooZHAxMDcKZzE5CkkwMApzZzIwCmcy\nMQpzYnNnMzEKTDdMCnNnNTgKZzI3CihTJ1x4MDdceGUwXHgwNFx4MTVceDBjNjdceDBiXHhjZVx4\nYTcnCnRScDEwOApzYnNTJ19saWJyYXJ5X2NhY2hlJwpwMTA5CmczOQpzZzI5ClYKc2czMQpMN0wK\nc2czMgpnMjcKKFMnXHgwN1x4ZTBceDA0XHgxNVx4MGM2N1x4MGJceGMyXHhiMycKdFJwMTEwCnNi\nc2cxNQpnNQooZzE2Cmc3Ck50UnAxMTEKKGRwMTEyCmcxOQpJMDAKc2cyMApnMjEKc2JzUydvd25l\ncl9pZCcKcDExMwpMNUwKc1MnYXBwcm92ZWQnCnAxMTQKSTAwCnNTJ19ncm91cF9jYWNoZScKcDEx\nNQpnMzUKKChWYXV0aApwMTE2ClMnR3JvdXAnCnAxMTcKdChsZzM4CnRScDExOAooZHAxMTkKZzEw\nOQpnMzkKc2cxNQpnNQooZzE2Cmc3Ck50UnAxMjAKKGRwMTIxCmcxOQpJMDAKc2cyMApnMjEKc2Jz\nZzMxCkwxTApzZzQyCmc1MApzYnNTJ2dyb3VwX2lkJwpwMTIyCkwxTApzZzMxCkwxTApzUydiYWNr\nZW5kJwpwMTIzClZlbWFpbApwMTI0CnNic0kwMQpOdHAxMjUKYShMN0wKZzIKZzMKSTAxCk50cDEy\nNgphLg==\n'),(12,'KGxwMQooTDdMClMncHVyY2hhc2VfY29tcGxldGUnCnAyCihkcDMKUyd0cmFuc2FjdGlvbicKcDQK\nY2RqYW5nby5kYi5tb2RlbHMuYmFzZQptb2RlbF91bnBpY2tsZQpwNQooKFZwYXltZW50CnA2ClMn\nVHJhbnNhY3Rpb24nCnA3CnQobGNkamFuZ28uZGIubW9kZWxzLmJhc2UKc2ltcGxlX2NsYXNzX2Zh\nY3RvcnkKcDgKdFJwOQooZHAxMApTJ2V4dHJhJwpwMTEKKGRwMTIKVmxpYnJhcnlfaWQKcDEzCkkx\nCnNWY29waWVzCnAxNApJMQpzc1MncGF5X2tleScKcDE1ClZjaF84Sk5xUjJuRzh1V29hUwpwMTYK\nc1MncmVjZWlwdCcKcDE3Ck5zUydfc3RhdGUnCnAxOApjY29weV9yZWcKX3JlY29uc3RydWN0b3IK\ncDE5CihjZGphbmdvLmRiLm1vZGVscy5iYXNlCk1vZGVsU3RhdGUKcDIwCmNfX2J1aWx0aW5fXwpv\nYmplY3QKcDIxCk50UnAyMgooZHAyMwpTJ2FkZGluZycKcDI0CkkwMApzUydkYicKcDI1ClMnZGVm\nYXVsdCcKcDI2CnNic1MnY2FtcGFpZ25faWQnCnAyNwpMNTJMCnNTJ2N1cnJlbmN5JwpwMjgKUydV\nU0QnCnAyOQpzUydpZCcKcDMwCkwyTApzUydsb2NhbF9zdGF0dXMnCnAzMQpWTk9ORQpwMzIKc1Mn\nZGF0ZV9hdXRob3JpemVkJwpwMzMKY2RhdGV0aW1lCmRhdGV0aW1lCnAzNAooUydceDA3XHhlMFx4\nMDRceDE1XHgwYzY6XHgwYlx4ZDdceGVmJwp0UnAzNQpzUyd1c2VyX2lkJwpwMzYKTDdMCnNTJ21h\neF9hbW91bnQnCnAzNwpjZGVjaW1hbApEZWNpbWFsCnAzOAooUycxMC4wMCcKdFJwMzkKc1MnX29m\nZmVyX2NhY2hlJwpwNDAKZzUKKChWY29yZQpwNDEKUydPZmZlcicKcDQyCnQobGc4CnRScDQzCihk\ncDQ0ClMnbGljZW5zZScKcDQ1CkkyCnNTJ3ByaWNlJwpwNDYKZzM4CihTJzEwLjAwJwp0UnA0Nwpz\nZzE4CmcxOQooZzIwCmcyMQpOdFJwNDgKKGRwNDkKZzI0CkkwMApzZzI1CmcyNgpzYnNTJ2FjdGl2\nZScKcDUwCkkwMQpzZzMwCkwyTApzUyd3b3JrX2lkJwpwNTEKTDUyTApzYnNTJ191c2VyX2NhY2hl\nJwpwNTIKZzUKKChWYXV0aApwNTMKUydVc2VyJwpwNTQKdChsZzgKdFJwNTUKKGRwNTYKUyd1c2Vy\nbmFtZScKcDU3ClZyeWxpYnJhcnkKcDU4CnNTJ2ZpcnN0X25hbWUnCnA1OQpWCnNTJ2xhc3RfbmFt\nZScKcDYwClYKc1MnX3Byb2ZpbGVfY2FjaGUnCnA2MQpnNQooKFZjb3JlCnA2MgpTJ1VzZXJQcm9m\naWxlJwpwNjMKdChsZzgKdFJwNjQKKGRwNjUKUydnb29kcmVhZHNfYXV0aF9zZWNyZXQnCnA2NgpO\nc2czNgpMN0wKc1MnZ29vZHJlYWRzX3VzZXJfbmFtZScKcDY3Ck5zUydjcmVhdGVkJwpwNjgKZzM0\nCihTJ1x4MDdceGUwXHgwNFx4MTVceDBjNjdceDAwXHgwMFx4MDAnCnRScDY5CnNTJ2F2YXRhcl9z\nb3VyY2UnCnA3MApJNApzUyd0YWdsaW5lJwpwNzEKVgpzUydraW5kbGVfZW1haWwnCnA3MgpWCnNn\nMTgKZzE5CihnMjAKZzIxCk50UnA3MwooZHA3NApnMjQKSTAwCnNnMjUKZzI2CnNic1MndHdpdHRl\ncl9pZCcKcDc1ClYKc1MncGljX3VybCcKcDc2ClYKc1MnZ29vZHJlYWRzX3VzZXJfaWQnCnA3NwpO\nc2c1MgpnNTUKc1MnZ29vZHJlYWRzX3VzZXJfbGluaycKcDc4Ck5zUydmYWNlYm9va19pZCcKcDc5\nCk5zUydsaWJyYXJ5dGhpbmdfaWQnCnA4MApWCnNTJ2hvbWVfdXJsJwpwODEKVgpzUydnb29kcmVh\nZHNfYXV0aF90b2tlbicKcDgyCk5zZzMwCkw3TApzYnNTJ2lzX2FjdGl2ZScKcDgzCkkwMQpzZzE4\nCmcxOQooZzIwCmcyMQpOdFJwODQKKGRwODUKZzI0CkkwMApzZzI1CmcyNgpzYnNTJ19jcmVkaXRf\nY2FjaGUnCnA4NgpnNQooKFZwYXltZW50CnA4NwpTJ0NyZWRpdCcKcDg4CnQobGc4CnRScDg5Cihk\ncDkwCmczNgpMN0wKc1MncGxlZGdlZCcKcDkxCmczOAooUycwLjAwJwp0UnA5MgpzZzE4CmcxOQoo\nZzIwCmcyMQpOdFJwOTMKKGRwOTQKZzI0CkkwMApzZzI1CmcyNgpzYnNnNTIKZzU1CnNTJ2xhc3Rf\nYWN0aXZpdHknCnA5NQpnMzQKKFMnXHgwN1x4ZTBceDA0XHgxNVx4MGM2N1x4MDBceDAwXHgwMCcK\ndFJwOTYKc1MnYmFsYW5jZScKcDk3CmczOAooUycwLjAwJwp0UnA5OApzZzMwCkw3TApzYnNTJ2Vt\nYWlsJwpwOTkKVnJ5bGlicmFyeUBleGFtcGxlLm9yZwpwMTAwCnNTJ2lzX3N1cGVydXNlcicKcDEw\nMQpJMDAKc1MnaXNfc3RhZmYnCnAxMDIKSTAwCnNTJ2xhc3RfbG9naW4nCnAxMDMKZzM0CihTJ1x4\nMDdceGUwXHgwNFx4MTVceDBjNjhceDAwXHgwMFx4MDAnCnRScDEwNApzUydwYXNzd29yZCcKcDEw\nNQpWCnNnMzAKTDdMCnNTJ2RhdGVfam9pbmVkJwpwMTA2CmczNAooUydceDA3XHhlMFx4MDRceDE1\nXHgwYzY3XHgwMFx4MDBceDAwJwp0UnAxMDcKc2JzUydhcHByb3ZlZCcKcDEwOApJMDEKc1Mnc2Vj\ncmV0JwpwMTA5ClZjNzNkOGRkOS0wN2UxLTExZTYtYjE0YS0zYzE1YzJlYjYyYmMKcDExMApzUydw\ncmVhcHByb3ZhbF9rZXknCnAxMTEKVmN1c184Sk5xMEk3aGh6MmVYRApwMTEyCnNTJ2RhdGVfcGF5\nbWVudCcKcDExMwpnMzQKKFMnXHgwN1x4ZTBceDA0XHgxNVx4MGM2O1x4MDdDUCcKdFJwMTE0CnNT\nJ3R5cGUnCnAxMTUKSTEKc1Mnc3RhdHVzJwpwMTE2ClMnQ29tcGxldGUnCnAxMTcKc1MnZGF0ZV9l\neHBpcmVkJwpwMTE4Ck5zUydvZmZlcl9pZCcKcDExOQpMMkwKc1MnaG9zdCcKcDEyMApTJ3N0cmlw\nZWxpYicKcDEyMQpzUydhbm9ueW1vdXMnCnAxMjIKSTAwCnNTJ2V4ZWN1dGlvbicKcDEyMwpMMEwK\nc1MnZGF0ZV9leGVjdXRlZCcKcDEyNApOc1MnX2NhbXBhaWduX2NhY2hlJwpwMTI1Cmc1CigoVmNv\ncmUKcDEyNgpTJ0NhbXBhaWduJwpwMTI3CnQobGc4CnRScDEyOAooZHAxMjkKUydkb193YXRlcm1h\ncmsnCnAxMzAKSTAxCnNnMTgKZzE5CihnMjAKZzIxCk50UnAxMzEKKGRwMTMyCmcyNApJMDAKc2cy\nNQpnMjYKc2JzUyd1c2VfYWRkX2FzaycKcDEzMwpJMDAKc1MnZGVhZGxpbmUnCnAxMzQKTnNnMzAK\nTDUyTApzUydhbWF6b25fcmVjZWl2ZXInCnAxMzUKVgpzUydkZXRhaWxzJwpwMTM2ClYKc1MnX2N1\ncnJlbnRfdG90YWwnCnAxMzcKZzM4CihTJzEwLjAwJwp0UnAxMzgKc1MncHVibGlzaGVyX2lkJwpw\nMTM5Ck5zZzk5ClYKc2cxMTYKVkFDVElWRQpwMTQwCnNTJ2Rlc2NyaXB0aW9uJwpwMTQxClY8cD4m\ncXVvdDtCdXkgdGhpcyBib29rIGZvciB0aGUgc2FrZSBvZiBodW1hbml0eSE8L3A+DVx1MDAwYQpw\nMTQyCnNTJ3BheXBhbF9yZWNlaXZlcicKcDE0MwpWcmF5bW9uZC55ZWVAZGF0YXVuYm91bmQuY29t\nCnAxNDQKc1MnYWN0aXZhdGVkJwpwMTQ1CmczNAooUydceDA3XHhlMFx4MDRceDE1XHgwYzY1XHgw\nMFx4MDBceDAwJwp0UnAxNDYKc1MnX3dvcmtfY2FjaGUnCnAxNDcKZzUKKChWY29yZQpwMTQ4ClMn\nV29yaycKcDE0OQp0KGxnOAp0UnAxNTAKKGRwMTUxClMnc2VsZWN0ZWRfZWRpdGlvbl9pZCcKcDE1\nMgpMNTJMCnNTJ19sYXN0X2NhbXBhaWduJwpwMTUzCk5zUydsYW5ndWFnZScKcDE1NApWZW4KcDE1\nNQpzUyd0aXRsZScKcDE1NgpWUHJvIFdlYiAyLjAgTWFzaHVwcwpwMTU3CnNTJ29wZW5saWJyYXJ5\nX2xvb2t1cCcKcDE1OApOc2c2OApnMzQKKFMnXHgwN1x4ZTBceDA0XHgxNVx4MGM0XHgwMVx4MDBc\neDAwXHgwMCcKdFJwMTU5CnNnMTgKZzE5CihnMjAKZzIxCk50UnAxNjAKKGRwMTYxCmcyNApJMDAK\nc2cyNQpnMjYKc2JzUydwdWJsaWNhdGlvbl9yYW5nZScKcDE2MgpWMjAwOApwMTYzCnNTJ2lzX2Zy\nZWUnCnAxNjQKSTAwCnNTJ2ZlYXR1cmVkJwpwMTY1Ck5zUydudW1fd2lzaGVzJwpwMTY2CkwwTApz\nZzMwCkw1MkwKc2cxNDEKVgpzYnNTJ3Byb2JsZW1zJwpwMTY3CihscDE2OApzUydkb2xsYXJfcGVy\nX2RheScKcDE2OQpGMC4xOTk5MjAwMzE5ODcyMDUwMQpzUydjY19kYXRlX2luaXRpYWwnCnAxNzAK\nZzM0CihTJ1x4MDdceGVlXHgwMVx4MDFceDAwXHgwMFx4MDBceDAwXHgwMFx4MDAnCnRScDE3MQpz\nUyduYW1lJwpwMTcyClZQcm8gV2ViIDIuMCBNYXNodXBzCnAxNzMKc1MndGFyZ2V0JwpwMTc0Cmcz\nOAooUycxMDAwLjAwJwp0UnAxNzUKc2c0NQpWQ0MgQlktTkMtTkQKcDE3NgpzZzY4CmczNAooUydc\neDA3XHhlMFx4MDRceDE1XHgwYzRceDAxXHgwMFx4MDBceDAwJwp0UnAxNzcKc2cxMTUKSTIKc1Mn\nZWRpdGlvbl9pZCcKcDE3OApMNTJMCnNnNTEKTDUyTApzUydsZWZ0JwpwMTc5CmczOAooUyc5ODku\nOTk5OTk5OTk5OTk5NDMxNTY1ODExMzkxOScKdFJwMTgwCnNic2cxMzcKTnNTJ2RhdGVfbW9kaWZp\nZWQnCnAxODEKZzM0CihTJ1x4MDdceGUwXHgwNFx4MTVceDBjNjtceDA3RUInCnRScDE4MgpzUydy\nZWFzb24nCnAxODMKTnNTJ3ByZW1pdW1faWQnCnAxODQKTnNTJ2Ftb3VudCcKcDE4NQpnMzgKKFMn\nMTAuMDAnCnRScDE4NgpzUydlcnJvcicKcDE4NwpOc1MnZGF0ZV9jcmVhdGVkJwpwMTg4CmczNAoo\nUydceDA3XHhlMFx4MDRceDE1XHgwYzY5XHgwMFx4MDBceDAwJwp0UnAxODkKc2JzUydjdXJyZW50\nX3NpdGUnCnAxOTAKZzUKKChWc2l0ZXMKcDE5MQpTJ1NpdGUnCnAxOTIKdChsZzgKdFJwMTkzCihk\ncDE5NApTJ2RvbWFpbicKcDE5NQpWbG9jYWxob3N0OjgwMDAKcDE5NgpzZzE4CmcxOQooZzIwCmcy\nMQpOdFJwMTk3CihkcDE5OApnMjQKSTAwCnNnMjUKZzI2CnNic2czMApMM0wKc2cxNzIKVnVuZ2x1\nZS5pdCBsb2NhbCBkZXZlbG9wbWVudApwMTk5CnNic0kwMQpOdHAyMDAKYS4=\n'),(13,'KGxwMQooTDNMClMnbmV3X3dpc2hlcicKcDIKKGRwMwpTJ3dvcmsnCnA0CmNkamFuZ28uZGIubW9k\nZWxzLmJhc2UKbW9kZWxfdW5waWNrbGUKcDUKKChWY29yZQpwNgpTJ1dvcmsnCnA3CnQobGNkamFu\nZ28uZGIubW9kZWxzLmJhc2UKc2ltcGxlX2NsYXNzX2ZhY3RvcnkKcDgKdFJwOQooZHAxMApTJ3Nl\nbGVjdGVkX2VkaXRpb25faWQnCnAxMQpMNTJMCnNTJ19sYXN0X2NhbXBhaWduJwpwMTIKTnNTJ2xh\nbmd1YWdlJwpwMTMKVmVuCnAxNApzUyd0aXRsZScKcDE1ClZQcm8gV2ViIDIuMCBNYXNodXBzCnAx\nNgpzUydvcGVubGlicmFyeV9sb29rdXAnCnAxNwpOc1MnY3JlYXRlZCcKcDE4CmNkYXRldGltZQpk\nYXRldGltZQpwMTkKKFMnXHgwN1x4ZTBceDA0XHgxNVx4MGM0XHgwMVx4MDBceDAwXHgwMCcKdFJw\nMjAKc1MnX3N0YXRlJwpwMjEKY2NvcHlfcmVnCl9yZWNvbnN0cnVjdG9yCnAyMgooY2RqYW5nby5k\nYi5tb2RlbHMuYmFzZQpNb2RlbFN0YXRlCnAyMwpjX19idWlsdGluX18Kb2JqZWN0CnAyNApOdFJw\nMjUKKGRwMjYKUydhZGRpbmcnCnAyNwpJMDAKc1MnZGInCnAyOApTJ2RlZmF1bHQnCnAyOQpzYnNT\nJ3B1YmxpY2F0aW9uX3JhbmdlJwpwMzAKVjIwMDgKcDMxCnNTJ2lzX2ZyZWUnCnAzMgpJMDAKc1Mn\nZmVhdHVyZWQnCnAzMwpOc1MnbnVtX3dpc2hlcycKcDM0CkkxCnNTJ2lkJwpwMzUKTDUyTApzUydk\nZXNjcmlwdGlvbicKcDM2ClYKc2JzUydzdXBwb3J0ZXInCnAzNwpnNQooKFZhdXRoCnAzOApTJ1Vz\nZXInCnAzOQp0KGxnOAp0UnA0MAooZHA0MQpTJ3VzZXJuYW1lJwpwNDIKVnJ5bGlicmFyeQpwNDMK\nc1MnZmlyc3RfbmFtZScKcDQ0ClYKc1MnbGFzdF9uYW1lJwpwNDUKVgpzUydpc19hY3RpdmUnCnA0\nNgpJMDEKc2cyMQpnMjIKKGcyMwpnMjQKTnRScDQ3CihkcDQ4CmcyNwpJMDAKc2cyOApnMjkKc2Jz\nUydfd2lzaGxpc3RfY2FjaGUnCnA0OQpnNQooKFZjb3JlCnA1MApTJ1dpc2hsaXN0JwpwNTEKdChs\nZzgKdFJwNTIKKGRwNTMKUyd1c2VyX2lkJwpwNTQKTDdMCnNTJ191c2VyX2NhY2hlJwpwNTUKZzQw\nCnNnMjEKZzIyCihnMjMKZzI0Ck50UnA1NgooZHA1NwpnMjcKSTAwCnNnMjgKZzI5CnNic2czNQpM\nN0wKc2cxOApnMTkKKFMnXHgwN1x4ZTBceDA0XHgxNVx4MGM2N1x4MDBceDAwXHgwMCcKdFJwNTgK\nc2JzUydlbWFpbCcKcDU5ClZyeWxpYnJhcnlAZXhhbXBsZS5vcmcKcDYwCnNTJ2lzX3N1cGVydXNl\ncicKcDYxCkkwMApzUydpc19zdGFmZicKcDYyCkkwMApzUydsYXN0X2xvZ2luJwpwNjMKZzE5CihT\nJ1x4MDdceGUwXHgwNFx4MTVceDBjNjhceDAwXHgwMFx4MDAnCnRScDY0CnNTJ3Bhc3N3b3JkJwpw\nNjUKVgpzZzM1Ckw3TApzUydkYXRlX2pvaW5lZCcKcDY2CmcxOQooUydceDA3XHhlMFx4MDRceDE1\nXHgwYzY3XHgwMFx4MDBceDAwJwp0UnA2NwpzYnNTJ2Jhc2VfdXJsJwpwNjgKUydodHRwOi8vMTI3\nLjAuMC4xOjgwMDAnCnA2OQpzSTAxCk50cDcwCmEu\n');
/*!40000 ALTER TABLE `notification_noticequeuebatch` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification_noticesetting`
--

DROP TABLE IF EXISTS `notification_noticesetting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notification_noticesetting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `notice_type_id` int(11) NOT NULL,
  `medium` varchar(1) NOT NULL,
  `send` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`notice_type_id`,`medium`),
  KEY `notification_noticesetting_403f60f` (`user_id`),
  KEY `notification_noticesetting_d734034` (`notice_type_id`),
  CONSTRAINT `notice_type_id_refs_id_1024de5c` FOREIGN KEY (`notice_type_id`) REFERENCES `notification_noticetype` (`id`),
  CONSTRAINT `user_id_refs_id_8c53966` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification_noticesetting`
--

LOCK TABLES `notification_noticesetting` WRITE;
/*!40000 ALTER TABLE `notification_noticesetting` DISABLE KEYS */;
INSERT INTO `notification_noticesetting` VALUES (1,1,1,'1',1),(2,14,1,'1',1),(3,466,1,'1',1);
/*!40000 ALTER TABLE `notification_noticesetting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification_noticetype`
--

DROP TABLE IF EXISTS `notification_noticetype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notification_noticetype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label` varchar(40) NOT NULL,
  `display` varchar(50) NOT NULL,
  `description` varchar(100) NOT NULL,
  `default` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification_noticetype`
--

LOCK TABLES `notification_noticetype` WRITE;
/*!40000 ALTER TABLE `notification_noticetype` DISABLE KEYS */;
INSERT INTO `notification_noticetype` VALUES (1,'wishlist_comment','Book List Comment','A comment has been received on one of your books.',1),(2,'comment_on_commented','Comment on Commented Work','A comment has been received on a book that you\'ve commented on.',2),(3,'wishlist_work_claimed','Rights Holder is Active','A rights holder has shown up for a book that you\'ve faved.',1),(4,'wishlist_active','New Campaign','A book you\'ve favorited has a newly launched campaign.',2),(5,'wishlist_near_target','Campaign Near Target','A book you want is near its ungluing target.',2),(6,'wishlist_near_deadline','Campaign Near Deadline','A book you want is almost out of time.',2),(7,'wishlist_premium_limited_supply','Only a Few Premiums Left','A limited edition premium is running out on a book you\'ve faved.',2),(8,'wishlist_successful','Successful Campaign','An ungluing campaign that you have supported or faved has succeeded.',2),(9,'wishlist_unsuccessful','Unsuccessful Campaign','An ungluing campaign that you supported didn\'t succeed this time.',2),(10,'wishlist_updated','Campaign Updated','An ungluing campaign you support has been updated.',1),(11,'wishlist_message','Campaign Communication','You have a private message from unglue.it staff or the rights holder about a book you\'ve faved.',2),(12,'wishlist_price_drop','Campaign Price Drop','An ungluing campaign you\'ve faved has a reduced target.',1),(13,'wishlist_unglued_book_released','Unglued Book!','A book you\'ve faved is now available to be downloaded.',2),(14,'pledge_you_have_pledged','Thanks For Your Pledge!','Your ungluing pledge has been entered.',2),(15,'pledge_status_change','Your Pledge Has Been Modified','Your ungluing pledge has been modified.',2),(16,'pledge_charged','Your Pledge has been Executed','You have contributed to a successful ungluing campaign.',2),(17,'rights_holder_created','Agreement Accepted','You have become a verified Unglue.it rights holder.',2),(18,'rights_holder_claim_approved','Claim Accepted','A claim you\'ve entered has been accepted.',2),(19,'wishlist_official_comment','Book List Comment','The author or publisher, or and Unglue.it staffer, has commented on one of your faves.',2),(20,'pledge_failed','Unable to charge your credit card','A charge to your credit card did not go through.',2),(21,'rights_holder_claim','Claim Entered','A claim has been entered.',2),(22,'wishlist_unsuccessful_amazon','Campaign shut down','An ungluing campaign that you supported had to be shut down due to an Amazon Payments policy change.',2),(23,'pledge_gift_credit','Gift Credit Balance','You have a gift credit balance',2),(24,'new_wisher','New wisher','Someone new has faved a book that you\'re the rightsholder for',2),(25,'account_expiring','Credit Card Expiring Soon','Your credit card is about to expire.',2),(26,'account_expired','Credit Card Has Expired','Your credit card has expired.',2),(27,'account_active','Credit Card Number Updated','Payment method updated.',1),(28,'purchase_complete','Your Purchase is Complete','Your Unglue.it Purchase is Complete.',2),(29,'library_borrow','Library eBook Borrowed.','You\'ve borrowed an ebook through a Library participating in Unglue.it',2),(30,'library_reserve','Library eBook Reserved.','An ebook you\'ve reserved is available.',2),(31,'library_join','New Library User.','A library participating in Unglue.it has added a user',2),(32,'purchase_gift','You have a gift.','An ungluer has given you an ebook.',2),(33,'purchase_got_gift','Your gift was received.','The ebook you sent as a gift has been redeemed.',2),(34,'purchase_gift_waiting','Your gift is waiting.','Please claim your ebook.',2),(35,'purchase_notgot_gift','Your gift wasn\'t received.','The ebook you sent as a gift has not yet been redeemed.',2);
/*!40000 ALTER TABLE `notification_noticetype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification_observeditem`
--

DROP TABLE IF EXISTS `notification_observeditem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notification_observeditem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `object_id` int(10) unsigned NOT NULL,
  `notice_type_id` int(11) NOT NULL,
  `added` datetime NOT NULL,
  `signal` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `notification_observeditem_403f60f` (`user_id`),
  KEY `notification_observeditem_1bb8f392` (`content_type_id`),
  KEY `notification_observeditem_d734034` (`notice_type_id`),
  CONSTRAINT `content_type_id_refs_id_6c21f628` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `notice_type_id_refs_id_4b098f3e` FOREIGN KEY (`notice_type_id`) REFERENCES `notification_noticetype` (`id`),
  CONSTRAINT `user_id_refs_id_7555f7d4` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification_observeditem`
--

LOCK TABLES `notification_observeditem` WRITE;
/*!40000 ALTER TABLE `notification_observeditem` DISABLE KEYS */;
/*!40000 ALTER TABLE `notification_observeditem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `page_page`
--

DROP TABLE IF EXISTS `page_page`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `page_page` (
  `slug` varchar(50) NOT NULL,
  `title_en` varchar(256) DEFAULT NULL,
  `body_en` longtext,
  `public` tinyint(1) NOT NULL,
  PRIMARY KEY (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `page_page`
--

LOCK TABLES `page_page` WRITE;
/*!40000 ALTER TABLE `page_page` DISABLE KEYS */;
/*!40000 ALTER TABLE `page_page` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_account`
--

DROP TABLE IF EXISTS `payment_account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payment_account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(32) NOT NULL,
  `account_id` varchar(128) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `card_last4` varchar(4) DEFAULT NULL,
  `card_type` varchar(32) DEFAULT NULL,
  `card_exp_month` int(11) DEFAULT NULL,
  `card_exp_year` int(11) DEFAULT NULL,
  `card_fingerprint` varchar(32) DEFAULT NULL,
  `card_country` varchar(2) DEFAULT NULL,
  `date_created` datetime NOT NULL,
  `date_modified` datetime NOT NULL,
  `date_deactivated` datetime DEFAULT NULL,
  `status` varchar(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `payment_account_6340c63c` (`user_id`),
  CONSTRAINT `user_id_refs_id_1d3caeed` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_account`
--

LOCK TABLES `payment_account` WRITE;
/*!40000 ALTER TABLE `payment_account` DISABLE KEYS */;
INSERT INTO `payment_account` VALUES (1,'stripelib','cus_8JNpuW8RM7KmsW',3,'4242','Visa',1,2018,'rUCVddfMC0GfM3zh','US','2016-04-21 12:53:54','2016-04-21 12:53:54',NULL,'ACTIVE'),(2,'stripelib','cus_8JNq0I7hhz2eXD',7,'4242','Visa',1,2018,'rUCVddfMC0GfM3zh','US','2016-04-21 12:54:58','2016-04-21 12:54:58',NULL,'ACTIVE');
/*!40000 ALTER TABLE `payment_account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_credit`
--

DROP TABLE IF EXISTS `payment_credit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payment_credit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `balance` decimal(14,2) NOT NULL,
  `pledged` decimal(14,2) NOT NULL,
  `last_activity` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_id_refs_id_fd312433` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_credit`
--

LOCK TABLES `payment_credit` WRITE;
/*!40000 ALTER TABLE `payment_credit` DISABLE KEYS */;
INSERT INTO `payment_credit` VALUES (1,1,0.00,0.00,'2016-04-21 12:51:56'),(2,2,0.00,0.00,'2016-04-21 12:51:56'),(3,3,0.00,0.00,'2016-04-21 12:51:56'),(4,4,0.00,0.00,'2016-04-21 12:51:56'),(5,5,0.00,0.00,'2016-04-21 12:52:00'),(6,6,0.00,0.00,'2016-04-21 12:52:01'),(7,7,0.00,0.00,'2016-04-21 12:54:55');
/*!40000 ALTER TABLE `payment_credit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_creditlog`
--

DROP TABLE IF EXISTS `payment_creditlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payment_creditlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `amount` decimal(14,2) NOT NULL,
  `timestamp` datetime NOT NULL,
  `action` varchar(16) NOT NULL,
  `sent` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `payment_creditlog_6340c63c` (`user_id`),
  CONSTRAINT `user_id_refs_id_6148e9bd` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_creditlog`
--

LOCK TABLES `payment_creditlog` WRITE;
/*!40000 ALTER TABLE `payment_creditlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment_creditlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_paymentresponse`
--

DROP TABLE IF EXISTS `payment_paymentresponse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payment_paymentresponse` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `api` varchar(64) NOT NULL,
  `correlation_id` varchar(512) DEFAULT NULL,
  `timestamp` varchar(128) DEFAULT NULL,
  `info` varchar(1024) DEFAULT NULL,
  `transaction_id` int(11) NOT NULL,
  `status` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `payment_paymentresponse_45d19ab3` (`transaction_id`),
  CONSTRAINT `transaction_id_refs_id_1f406d1c` FOREIGN KEY (`transaction_id`) REFERENCES `payment_transaction` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_paymentresponse`
--

LOCK TABLES `payment_paymentresponse` WRITE;
/*!40000 ALTER TABLE `payment_paymentresponse` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment_paymentresponse` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_receiver`
--

DROP TABLE IF EXISTS `payment_receiver`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payment_receiver` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(64) NOT NULL,
  `amount` decimal(14,2) NOT NULL DEFAULT '0.00',
  `currency` varchar(10) NOT NULL,
  `status` varchar(64) NOT NULL,
  `reason` varchar(64) NOT NULL,
  `primary` tinyint(1) NOT NULL DEFAULT '0',
  `txn_id` varchar(64) NOT NULL,
  `transaction_id` int(11) NOT NULL,
  `local_status` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `payment_receiver_45d19ab3` (`transaction_id`),
  CONSTRAINT `transaction_id_refs_id_5b0405ed` FOREIGN KEY (`transaction_id`) REFERENCES `payment_transaction` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_receiver`
--

LOCK TABLES `payment_receiver` WRITE;
/*!40000 ALTER TABLE `payment_receiver` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment_receiver` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_sent`
--

DROP TABLE IF EXISTS `payment_sent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payment_sent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(32) DEFAULT NULL,
  `amount` decimal(14,2) NOT NULL,
  `timestamp` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_sent`
--

LOCK TABLES `payment_sent` WRITE;
/*!40000 ALTER TABLE `payment_sent` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment_sent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_transaction`
--

DROP TABLE IF EXISTS `payment_transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payment_transaction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` int(11) NOT NULL DEFAULT '0',
  `status` varchar(32) NOT NULL DEFAULT 'NONE',
  `amount` decimal(14,2) NOT NULL DEFAULT '0.00',
  `currency` varchar(10) DEFAULT 'USD',
  `secret` varchar(64) DEFAULT NULL,
  `receipt` varchar(256) DEFAULT NULL,
  `error` varchar(256) DEFAULT NULL,
  `reason` varchar(64) DEFAULT NULL,
  `date_created` datetime NOT NULL,
  `date_modified` datetime NOT NULL,
  `date_payment` datetime DEFAULT NULL,
  `date_authorized` datetime DEFAULT NULL,
  `date_expired` datetime DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `campaign_id` int(11) DEFAULT NULL,
  `anonymous` tinyint(1) NOT NULL DEFAULT '0',
  `execution` int(11) NOT NULL,
  `pay_key` varchar(128) DEFAULT NULL,
  `preapproval_key` varchar(128) DEFAULT NULL,
  `date_executed` datetime DEFAULT NULL,
  `max_amount` decimal(14,2) NOT NULL,
  `approved` tinyint(1) DEFAULT NULL,
  `premium_id` int(11) DEFAULT NULL,
  `local_status` varchar(32) DEFAULT NULL,
  `host` varchar(32) NOT NULL,
  `extra` text,
  `offer_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `payment_transaction_403f60f` (`user_id`),
  KEY `payment_transaction_702b94e6` (`campaign_id`),
  KEY `payment_transaction_bf4b5200` (`premium_id`),
  KEY `payment_transaction_ef075ecb` (`offer_id`),
  KEY `payment_transaction_816e0180` (`date_created`),
  CONSTRAINT `campaign_id_refs_id_3d3091ca` FOREIGN KEY (`campaign_id`) REFERENCES `core_campaign` (`id`),
  CONSTRAINT `offer_id_refs_id_e48eaa60` FOREIGN KEY (`offer_id`) REFERENCES `core_offer` (`id`),
  CONSTRAINT `premium_id_refs_id_2e3fbf62e3270f76` FOREIGN KEY (`premium_id`) REFERENCES `core_premium` (`id`),
  CONSTRAINT `user_id_refs_id_54db781c` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_transaction`
--

LOCK TABLES `payment_transaction` WRITE;
/*!40000 ALTER TABLE `payment_transaction` DISABLE KEYS */;
INSERT INTO `payment_transaction` VALUES (1,2,'Canceled',25.00,'USD','9d3a774f-07e1-11e6-aaca-3c15c2eb62bc',NULL,NULL,NULL,'2016-04-21 12:53:46','2016-04-21 12:53:57',NULL,'2016-04-21 12:53:54','2017-04-21 12:53:54',3,3,0,0,NULL,'cus_8JNpuW8RM7KmsW',NULL,10.00,1,150,'NONE','stripelib','{}',NULL),(2,1,'Complete',10.00,'USD','c73d8dd9-07e1-11e6-b14a-3c15c2eb62bc',NULL,NULL,NULL,'2016-04-21 12:54:57','2016-04-21 12:54:59','2016-04-21 12:54:59','2016-04-21 12:54:58',NULL,7,52,0,4,'ch_8JNqR2nG8uWoaS','ch_8JNqR2nG8uWoaS','2016-04-21 12:54:59',10.00,1,NULL,'NONE','stripelib','{\"library_id\": 1, \"copies\": 1}',2);
/*!40000 ALTER TABLE `payment_transaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questionnaire_answer`
--

DROP TABLE IF EXISTS `questionnaire_answer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `questionnaire_answer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `runid` varchar(32) NOT NULL,
  `answer` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `questionnaire_answer_56bb4187` (`subject_id`),
  KEY `questionnaire_answer_25110688` (`question_id`),
  KEY `questionnaire_answer_subject_id_2c66a0aca774dd63` (`subject_id`,`runid`,`id`),
  KEY `questionnaire_answer_subject_id_26abad56736b58d5` (`subject_id`,`runid`),
  CONSTRAINT `question_id_refs_id_95bced6e` FOREIGN KEY (`question_id`) REFERENCES `questionnaire_question` (`id`),
  CONSTRAINT `subject_id_refs_id_e7c19832` FOREIGN KEY (`subject_id`) REFERENCES `questionnaire_subject` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questionnaire_answer`
--

LOCK TABLES `questionnaire_answer` WRITE;
/*!40000 ALTER TABLE `questionnaire_answer` DISABLE KEYS */;
/*!40000 ALTER TABLE `questionnaire_answer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questionnaire_choice`
--

DROP TABLE IF EXISTS `questionnaire_choice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `questionnaire_choice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `question_id` int(11) NOT NULL,
  `sortid` int(11) NOT NULL,
  `value` varchar(64) NOT NULL,
  `text_en` varchar(200) DEFAULT NULL,
  `tags` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `questionnaire_choice_25110688` (`question_id`),
  KEY `questionnaire_choice_f6915675` (`value`),
  CONSTRAINT `question_id_refs_id_645f247c` FOREIGN KEY (`question_id`) REFERENCES `questionnaire_question` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questionnaire_choice`
--

LOCK TABLES `questionnaire_choice` WRITE;
/*!40000 ALTER TABLE `questionnaire_choice` DISABLE KEYS */;
/*!40000 ALTER TABLE `questionnaire_choice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questionnaire_dbstylesheet`
--

DROP TABLE IF EXISTS `questionnaire_dbstylesheet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `questionnaire_dbstylesheet` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `inclusion_tag` varchar(128) NOT NULL,
  `content` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questionnaire_dbstylesheet`
--

LOCK TABLES `questionnaire_dbstylesheet` WRITE;
/*!40000 ALTER TABLE `questionnaire_dbstylesheet` DISABLE KEYS */;
/*!40000 ALTER TABLE `questionnaire_dbstylesheet` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questionnaire_globalstyles`
--

DROP TABLE IF EXISTS `questionnaire_globalstyles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `questionnaire_globalstyles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questionnaire_globalstyles`
--

LOCK TABLES `questionnaire_globalstyles` WRITE;
/*!40000 ALTER TABLE `questionnaire_globalstyles` DISABLE KEYS */;
/*!40000 ALTER TABLE `questionnaire_globalstyles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questionnaire_landing`
--

DROP TABLE IF EXISTS `questionnaire_landing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `questionnaire_landing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nonce` varchar(32) DEFAULT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` int(10) unsigned DEFAULT NULL,
  `label` varchar(64) NOT NULL,
  `questionnaire_id` int(11),
  PRIMARY KEY (`id`),
  KEY `questionnaire_landing_37ef4eb4` (`content_type_id`),
  KEY `questionnaire_landing_dfaab653` (`questionnaire_id`),
  CONSTRAINT `content_type_id_refs_id_6f034f69` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `questionnaire_id_refs_id_fb5808db` FOREIGN KEY (`questionnaire_id`) REFERENCES `questionnaire_questionnaire` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questionnaire_landing`
--

LOCK TABLES `questionnaire_landing` WRITE;
/*!40000 ALTER TABLE `questionnaire_landing` DISABLE KEYS */;
/*!40000 ALTER TABLE `questionnaire_landing` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questionnaire_question`
--

DROP TABLE IF EXISTS `questionnaire_question`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `questionnaire_question` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `questionset_id` int(11) NOT NULL,
  `number` varchar(8) NOT NULL,
  `sort_id` int(11) DEFAULT NULL,
  `text_en` longtext,
  `type` varchar(32) NOT NULL,
  `extra_en` varchar(512) DEFAULT NULL,
  `checks` varchar(512) DEFAULT NULL,
  `footer_en` longtext,
  `parse_html` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `questionnaire_question_6c228d7e` (`questionset_id`),
  KEY `questionnaire_question_number_638db8ebd42279b1` (`number`,`questionset_id`),
  CONSTRAINT `questionset_id_refs_id_594cbcec` FOREIGN KEY (`questionset_id`) REFERENCES `questionnaire_questionset` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questionnaire_question`
--

LOCK TABLES `questionnaire_question` WRITE;
/*!40000 ALTER TABLE `questionnaire_question` DISABLE KEYS */;
/*!40000 ALTER TABLE `questionnaire_question` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questionnaire_questionnaire`
--

DROP TABLE IF EXISTS `questionnaire_questionnaire`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `questionnaire_questionnaire` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `redirect_url` varchar(128) NOT NULL,
  `html` longtext NOT NULL,
  `parse_html` tinyint(1) NOT NULL,
  `admin_access_only` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questionnaire_questionnaire`
--

LOCK TABLES `questionnaire_questionnaire` WRITE;
/*!40000 ALTER TABLE `questionnaire_questionnaire` DISABLE KEYS */;
/*!40000 ALTER TABLE `questionnaire_questionnaire` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questionnaire_questionset`
--

DROP TABLE IF EXISTS `questionnaire_questionset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `questionnaire_questionset` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `questionnaire_id` int(11) NOT NULL,
  `sortid` int(11) NOT NULL,
  `heading` varchar(64) NOT NULL,
  `checks` varchar(256) NOT NULL,
  `text_en` longtext,
  `parse_html` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `questionnaire_questionset_dfaab653` (`questionnaire_id`),
  KEY `questionnaire_questionset_questionnaire_id_4c701c8a8d82d023` (`questionnaire_id`,`sortid`),
  KEY `questionnaire_questionset_007d796c` (`sortid`),
  CONSTRAINT `questionnaire_id_refs_id_3ee12c9b` FOREIGN KEY (`questionnaire_id`) REFERENCES `questionnaire_questionnaire` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questionnaire_questionset`
--

LOCK TABLES `questionnaire_questionset` WRITE;
/*!40000 ALTER TABLE `questionnaire_questionset` DISABLE KEYS */;
/*!40000 ALTER TABLE `questionnaire_questionset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questionnaire_runinfo`
--

DROP TABLE IF EXISTS `questionnaire_runinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `questionnaire_runinfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `random` varchar(32) NOT NULL,
  `runid` varchar(32) NOT NULL,
  `questionset_id` int(11) DEFAULT NULL,
  `emailcount` int(11) NOT NULL,
  `created` datetime NOT NULL,
  `emailsent` datetime DEFAULT NULL,
  `lastemailerror` varchar(64) DEFAULT NULL,
  `state` varchar(16) DEFAULT NULL,
  `cookies` longtext,
  `tags` longtext NOT NULL,
  `skipped` longtext NOT NULL,
  `landing_id` int(11),
  PRIMARY KEY (`id`),
  KEY `questionnaire_runinfo_56bb4187` (`subject_id`),
  KEY `questionnaire_runinfo_6c228d7e` (`questionset_id`),
  KEY `questionnaire_runinfo_e33c130b` (`landing_id`),
  KEY `questionnaire_runinfo_8a2e4a2a` (`random`),
  CONSTRAINT `landing_id_refs_id_257aa55d` FOREIGN KEY (`landing_id`) REFERENCES `questionnaire_landing` (`id`),
  CONSTRAINT `questionset_id_refs_id_4ebb8a59` FOREIGN KEY (`questionset_id`) REFERENCES `questionnaire_questionset` (`id`),
  CONSTRAINT `subject_id_refs_id_5b1039cc` FOREIGN KEY (`subject_id`) REFERENCES `questionnaire_subject` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questionnaire_runinfo`
--

LOCK TABLES `questionnaire_runinfo` WRITE;
/*!40000 ALTER TABLE `questionnaire_runinfo` DISABLE KEYS */;
/*!40000 ALTER TABLE `questionnaire_runinfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questionnaire_runinfohistory`
--

DROP TABLE IF EXISTS `questionnaire_runinfohistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `questionnaire_runinfohistory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `runid` varchar(32) NOT NULL,
  `completed` datetime NOT NULL,
  `tags` longtext NOT NULL,
  `skipped` longtext NOT NULL,
  `questionnaire_id` int(11) NOT NULL,
  `landing_id` int(11),
  PRIMARY KEY (`id`),
  KEY `questionnaire_runinfohistory_56bb4187` (`subject_id`),
  KEY `questionnaire_runinfohistory_dfaab653` (`questionnaire_id`),
  KEY `questionnaire_runinfohistory_e33c130b` (`landing_id`),
  CONSTRAINT `landing_id_refs_id_95e0db4e` FOREIGN KEY (`landing_id`) REFERENCES `questionnaire_landing` (`id`),
  CONSTRAINT `questionnaire_id_refs_id_46574185` FOREIGN KEY (`questionnaire_id`) REFERENCES `questionnaire_questionnaire` (`id`),
  CONSTRAINT `subject_id_refs_id_682c24c0` FOREIGN KEY (`subject_id`) REFERENCES `questionnaire_subject` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questionnaire_runinfohistory`
--

LOCK TABLES `questionnaire_runinfohistory` WRITE;
/*!40000 ALTER TABLE `questionnaire_runinfohistory` DISABLE KEYS */;
/*!40000 ALTER TABLE `questionnaire_runinfohistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questionnaire_subject`
--

DROP TABLE IF EXISTS `questionnaire_subject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `questionnaire_subject` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `state` varchar(16) NOT NULL,
  `surname` varchar(64) DEFAULT NULL,
  `givenname` varchar(64) DEFAULT NULL,
  `email` varchar(75) DEFAULT NULL,
  `gender` varchar(8) NOT NULL,
  `nextrun` date DEFAULT NULL,
  `formtype` varchar(16) NOT NULL,
  `language` varchar(5) NOT NULL,
  `anonymous` tinyint(1) NOT NULL,
  `ip_address` char(39),
  PRIMARY KEY (`id`),
  KEY `questionnaire_subject_givenname_73f5ef8d44fec7cc` (`givenname`,`surname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questionnaire_subject`
--

LOCK TABLES `questionnaire_subject` WRITE;
/*!40000 ALTER TABLE `questionnaire_subject` DISABLE KEYS */;
/*!40000 ALTER TABLE `questionnaire_subject` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registration_registrationprofile`
--

DROP TABLE IF EXISTS `registration_registrationprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `registration_registrationprofile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `activation_key` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_id_refs_id_313280c4` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registration_registrationprofile`
--

LOCK TABLES `registration_registrationprofile` WRITE;
/*!40000 ALTER TABLE `registration_registrationprofile` DISABLE KEYS */;
INSERT INTO `registration_registrationprofile` VALUES (1,3,'ALREADY_ACTIVATED'),(2,4,'ALREADY_ACTIVATED');
/*!40000 ALTER TABLE `registration_registrationprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `social_auth_association`
--

DROP TABLE IF EXISTS `social_auth_association`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `social_auth_association` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_url` varchar(255) NOT NULL,
  `handle` varchar(255) NOT NULL,
  `secret` varchar(255) NOT NULL,
  `issued` int(11) NOT NULL,
  `lifetime` int(11) NOT NULL,
  `assoc_type` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `social_auth_association`
--

LOCK TABLES `social_auth_association` WRITE;
/*!40000 ALTER TABLE `social_auth_association` DISABLE KEYS */;
INSERT INTO `social_auth_association` VALUES (1,'https://www.google.com/accounts/o8/ud','AMlYA9WFUhmJ8_eEopkqPOTgFBPCb-O8pt_rPUUSu4S1E7SZjfbbpgbk','JLHXtrh7XWYR3y8FKhSFdpJTJRY=\n',1330712242,46800,'HMAC-SHA1');
/*!40000 ALTER TABLE `social_auth_association` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `social_auth_code`
--

DROP TABLE IF EXISTS `social_auth_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `social_auth_code` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(254) NOT NULL,
  `code` varchar(32) NOT NULL,
  `verified` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `social_auth_code_c1336794` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `social_auth_code`
--

LOCK TABLES `social_auth_code` WRITE;
/*!40000 ALTER TABLE `social_auth_code` DISABLE KEYS */;
/*!40000 ALTER TABLE `social_auth_code` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `social_auth_nonce`
--

DROP TABLE IF EXISTS `social_auth_nonce`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `social_auth_nonce` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_url` varchar(255) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `salt` varchar(40) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `social_auth_nonce`
--

LOCK TABLES `social_auth_nonce` WRITE;
/*!40000 ALTER TABLE `social_auth_nonce` DISABLE KEYS */;
INSERT INTO `social_auth_nonce` VALUES (1,'https://www.google.com/accounts/o8/ud',1330712243,'ttQdCPzKckEKOQ'),(2,'https://www.google.com/accounts/o8/ud',1330712525,'1lXNbgB3LygDwg');
/*!40000 ALTER TABLE `social_auth_nonce` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `social_auth_usersocialauth`
--

DROP TABLE IF EXISTS `social_auth_usersocialauth`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `social_auth_usersocialauth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `provider` varchar(32) NOT NULL,
  `uid` varchar(255) NOT NULL,
  `extra_data` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `provider` (`provider`,`uid`),
  KEY `social_auth_usersocialauth_403f60f` (`user_id`),
  CONSTRAINT `user_id_refs_id_60fa311b` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `social_auth_usersocialauth`
--

LOCK TABLES `social_auth_usersocialauth` WRITE;
/*!40000 ALTER TABLE `social_auth_usersocialauth` DISABLE KEYS */;
INSERT INTO `social_auth_usersocialauth` VALUES (1,1,'google','rdhyee@gluejar.com','null'),(2,2,'google','raymond.yee@gmail.com','null');
/*!40000 ALTER TABLE `social_auth_usersocialauth` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `south_migrationhistory`
--

DROP TABLE IF EXISTS `south_migrationhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `south_migrationhistory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_name` varchar(255) NOT NULL,
  `migration` varchar(255) NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=118 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `south_migrationhistory`
--

LOCK TABLES `south_migrationhistory` WRITE;
/*!40000 ALTER TABLE `south_migrationhistory` DISABLE KEYS */;
INSERT INTO `south_migrationhistory` VALUES (1,'core','0001_initial','2012-03-02 17:50:54'),(2,'core','0002_add_goodreads_id','2012-03-02 17:50:55'),(3,'core','0003_add_librarything_ids','2012-03-02 17:50:55'),(4,'core','0004_auto__add_field_campaign_status','2012-03-02 17:50:56'),(5,'core','0005_set_status','2012-03-02 17:50:56'),(6,'core','0006_wishes','2012-03-02 17:50:56'),(7,'core','0007_auto__add_field_wishes_created__add_field_wishes_source','2012-03-02 17:50:57'),(8,'core','0008_add_work_language_col','2012-03-02 17:50:58'),(9,'core','0009_add_work_language_data','2012-03-02 17:50:58'),(10,'core','0010_remove_edition_language','2012-03-02 17:50:58'),(11,'core','0011_auto__add_campaignaction__del_field_campaign_suspended_reason__del_fie','2012-03-02 17:50:59'),(12,'core','0012_auto__add_field_campaign_left','2012-03-02 17:51:00'),(13,'core','0013_move_subject_to_work','2012-03-02 17:51:01'),(14,'core','0015_auto__chg_field_subject_name__add_unique_subject_name','2012-03-02 17:51:01'),(15,'core','0016_auto__add_field_work_openlibrary_lookup','2012-03-02 17:51:02'),(16,'core','0017_isbn_to_13','2012-03-02 17:51:02'),(17,'core','0018_auto__del_field_edition_isbn_10','2012-03-02 17:51:02'),(18,'core','0019_googlebooks_id_must_be_unique','2012-03-02 17:51:02'),(19,'core','0020_auto__add_identifier__add_unique_identifier_type_value','2012-03-02 17:51:03'),(20,'core','0021_auto__del_field_work_librarything_id__del_field_work_openlibrary_id__d','2012-03-02 17:51:04'),(21,'core','0022_auto__chg_field_edition_publisher__chg_field_edition_publication_date','2012-03-02 17:51:05'),(22,'core','0023_auto__add_waswork','2012-03-02 17:51:05'),(23,'core','0024_auto__add_field_work_num_wishes','2012-03-02 17:51:06'),(24,'core','0025_count_wishes','2012-03-02 17:51:06'),(25,'core','0026_auto__add_field_ebook_user__add_field_waswork_moved__add_field_waswork','2012-03-02 17:51:08'),(26,'payment','0001_initial','2012-03-02 17:51:10'),(27,'payment','0002_auto__add_paymentresponse__del_field_transaction_reference__add_field_','2012-03-02 17:51:13'),(28,'payment','0003_auto__add_field_transaction_max_amount','2012-03-02 17:51:13'),(29,'payment','0004_auto__add_field_transaction_approved','2012-03-02 17:51:14'),(30,'tastypie','0001_initial','2012-03-02 17:51:14'),(31,'djcelery','0001_initial','2012-03-02 17:51:18'),(32,'payment','0005_auto__add_field_transaction_premium','2012-03-21 22:17:45'),(33,'core','0027_auto__add_field_campaign_license__chg_field_ebook_url','2012-03-28 15:24:25'),(34,'core','0028_auto__add_field_premium_limit','2012-03-28 15:24:25'),(35,'core','0029_https_facebook_avatars','2012-05-03 18:11:34'),(36,'core','0030_twitter_rewrite','2012-05-03 18:11:34'),(37,'core','0031_auto__add_field_campaign_edition','2012-05-03 18:11:35'),(38,'payment','0006_auto__add_field_transaction_local_status__add_field_paymentresponse_st','2012-05-03 18:11:36'),(39,'core','0032_auto__add_field_work_description','2012-05-07 23:51:10'),(40,'core','0033_move_descriptions','2012-05-07 23:51:10'),(41,'core','0034_auto__del_field_edition_description','2012-05-07 23:51:10'),(42,'core','0035_auto__add_key','2012-05-09 17:59:56'),(43,'core','0036_auto__add_unique_key_name','2012-05-09 17:59:56'),(44,'social_auth','0001_initial','2013-03-19 22:22:28'),(45,'default','0001_initial','2016-04-21 12:51:50'),(46,'api','0001_initial','2016-04-21 12:51:51'),(47,'bisac','0001_initial','2016-04-21 12:51:51'),(48,'core','0037_auto__add_field_edition_cover_image','2016-04-21 12:51:51'),(49,'core','0038_auto__chg_field_campaign_description__chg_field_campaign_details__add_','2016-04-21 12:51:51'),(50,'core','0039_auto__del_field_ebook_unglued__add_field_edition_unglued','2016-04-21 12:51:51'),(51,'core','0040_auto__add_badge','2016-04-21 12:51:52'),(52,'core','0041_auto','2016-04-21 12:51:52'),(53,'core','0042_auto__add_field_userprofile_avatar_source','2016-04-21 12:51:52'),(54,'core','0043_auto__add_publishername__add_publisher__add_field_campaign_email__add_','2016-04-21 12:51:52'),(55,'core','0044_pubname_to_model','2016-04-21 12:51:52'),(56,'core','0045_auto__del_field_edition_publisher','2016-04-21 12:51:52'),(57,'core','0046_auto__add_press','2016-04-21 12:51:52'),(58,'core','0047_auto__add_field_ebook_download_count','2016-04-21 12:51:52'),(59,'core','0048_auto__add_field_userprofile_kindle_email','2016-04-21 12:51:52'),(60,'core','0049_auto__add_libpref__add_marcrecord','2016-04-21 12:51:53'),(61,'core','0050_auto__add_ebookfile__add_offer__add_field_campaign_dollar_per_day__add','2016-04-21 12:51:53'),(62,'core','0051_auto__add_acq','2016-04-21 12:51:53'),(63,'core','0052_auto__add_field_acq_watermarked','2016-04-21 12:51:53'),(64,'core','0053_auto__add_field_acq_nonce','2016-04-21 12:51:53'),(65,'core','0054_auto__del_field_marcrecord_xml_record__del_field_marcrecord_mrc_record','2016-04-21 12:51:53'),(66,'core','0055_auto__add_field_acq_refreshes__add_field_acq_lib_acq','2016-04-21 12:51:53'),(67,'core','0056_auto__add_hold__add_field_acq_refreshed','2016-04-21 12:51:53'),(68,'core','0057_auto__add_field_campaign_do_watermark','2016-04-21 12:51:54'),(69,'core','0058_auto__chg_field_campaign_deadline','2016-04-21 12:51:54'),(70,'core','0059_auto__add_field_work_selected_edition__add_field_work_earliest_publica','2016-04-21 12:51:54'),(71,'core','0060_auto__chg_field_work_language','2016-04-21 12:51:54'),(72,'core','0061_auto__add_field_work_featured','2016-04-21 12:51:54'),(73,'core','0062_auto','2016-04-21 12:51:54'),(74,'core','0063_auto__add_field_campaign_use_add_ask__add_field_ebookfile_asking','2016-04-21 12:51:55'),(75,'core','0064_auto__add_field_ebook_active','2016-04-21 12:51:55'),(76,'core','0065_auto__chg_field_identifier_value','2016-04-21 12:51:55'),(77,'core','0066_auto__del_marcrecord','2016-04-21 12:51:55'),(78,'core','0067_auto__add_field_work_is_free','2016-04-21 12:51:55'),(79,'core','0068_auto__add_gift','2016-04-21 12:51:55'),(80,'core','0069_auto__add_field_subject_is_visible','2016-04-21 12:51:55'),(81,'core','0070_auto__add_field_ebook_filesize','2016-04-21 12:51:55'),(82,'core','0071_auto__chg_field_userprofile_facebook_id','2016-04-21 12:51:55'),(83,'core','0072_auto__add_relator__add_relation__add_field_subject_authority','2016-04-21 12:51:55'),(84,'core','0073_auto__del_field_work_earliest_publication__add_field_work_publication_','2016-04-21 12:51:56'),(85,'core','0074_auto__chg_field_author_name__add_unique_author_name__add_unique_publis','2016-04-21 12:51:56'),(86,'marc','0001_initial','2016-04-21 12:51:56'),(87,'marc','0002_auto__add_field_marcrecord_user__add_field_marcrecord_created','2016-04-21 12:51:56'),(88,'payment','0007_auto__add_field_transaction_host','2016-04-21 12:51:56'),(89,'payment','0008_auto__add_credit__add_creditlog__del_field_transaction_target__del_fie','2016-04-21 12:51:57'),(90,'payment','0009_auto__add_sent__add_field_creditlog_sent','2016-04-21 12:51:57'),(91,'payment','0010_auto__add_account','2016-04-21 12:51:57'),(92,'payment','0011_auto__add_field_account_card_last4__add_field_account_card_type__add_f','2016-04-21 12:51:57'),(93,'payment','0012_auto__chg_field_account_date_created','2016-04-21 12:51:57'),(94,'payment','0013_auto__add_field_account_status','2016-04-21 12:51:57'),(95,'payment','0014_init_account_status','2016-04-21 12:51:57'),(96,'payment','0015_auto__chg_field_account_status__add_field_transaction_extra','2016-04-21 12:51:57'),(97,'payment','0016_jsonify','2016-04-21 12:51:57'),(98,'payment','0017_auto__del_field_transaction_ack_name__del_field_transaction_ack_dedica','2016-04-21 12:51:57'),(99,'payment','0018_auto','2016-04-21 12:51:57'),(100,'survey','0001_initial','2016-04-21 12:51:57'),(101,'tastypie','0002_add_apikey_index','2016-04-21 12:51:58'),(102,'djcelery','0002_v25_changes','2016-04-21 12:51:58'),(103,'djcelery','0003_v26_changes','2016-04-21 12:51:58'),(104,'djcelery','0004_v30_changes','2016-04-21 12:51:58'),(105,'booxtream','0001_initial','2016-04-21 12:51:58'),(106,'libraryauth','0001_initial','2016-04-21 12:51:59'),(107,'libraryauth','0002_auto__add_emailpattern','2016-04-21 12:51:59'),(108,'libraryauth','0003_auto__add_field_library_name__add_field_library_approved__add_field_li','2016-04-21 12:51:59'),(109,'distro','0001_initial','2016-08-25 18:30:42'),(110,'questionnaire','0001_initial','2016-08-25 18:30:42'),(111,'questionnaire','0002_auto__chg_field_subject_language','2016-08-25 18:30:43'),(112,'questionnaire','0003_auto__add_globalstyles__add_dbstylesheet__add_field_question_parse_htm','2016-08-25 18:30:43'),(113,'questionnaire','0004_auto__add_landing','2016-08-25 18:30:43'),(114,'questionnaire','0005_move_nonces','2016-08-25 18:30:43'),(115,'questionnaire','0006_auto__add_field_runinfohistory_landing__add_field_runinfo_landing__add','2016-08-25 18:30:43'),(116,'questionnaire','0007_auto__add_field_subject_anonymous__add_field_subject_ip_address','2016-08-25 18:30:43'),(117,'questionnaire','0008_auto__add_index_choice_value__add_index_question_number_questionset__a','2016-08-25 18:30:43');
/*!40000 ALTER TABLE `south_migrationhistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `survey_landing`
--

DROP TABLE IF EXISTS `survey_landing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `survey_landing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nonce` varchar(32) DEFAULT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` int(10) unsigned DEFAULT NULL,
  `label` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `survey_landing_37ef4eb4` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_c1e17b85` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `survey_landing`
--

LOCK TABLES `survey_landing` WRITE;
/*!40000 ALTER TABLE `survey_landing` DISABLE KEYS */;
/*!40000 ALTER TABLE `survey_landing` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tastypie_apiaccess`
--

DROP TABLE IF EXISTS `tastypie_apiaccess`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tastypie_apiaccess` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `identifier` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL DEFAULT '',
  `request_method` varchar(10) NOT NULL DEFAULT '',
  `accessed` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tastypie_apiaccess`
--

LOCK TABLES `tastypie_apiaccess` WRITE;
/*!40000 ALTER TABLE `tastypie_apiaccess` DISABLE KEYS */;
/*!40000 ALTER TABLE `tastypie_apiaccess` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tastypie_apikey`
--

DROP TABLE IF EXISTS `tastypie_apikey`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tastypie_apikey` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `key` varchar(256) NOT NULL DEFAULT '',
  `created` datetime NOT NULL DEFAULT '2012-03-02 12:51:14',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_id_refs_id_56bfdb62` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tastypie_apikey`
--

LOCK TABLES `tastypie_apikey` WRITE;
/*!40000 ALTER TABLE `tastypie_apikey` DISABLE KEYS */;
INSERT INTO `tastypie_apikey` VALUES (1,1,'f48b2cd73b1733f32dc69ff1673265121397c13e','2012-03-02 13:17:24'),(2,2,'dbe45999934851c9370b5be4e1d2dd9e4822ff86','2012-03-02 13:21:21'),(3,3,'f31487e061d226829f298209f82d32fec75e4484','2012-03-13 19:11:32'),(4,4,'1cf3b2a6ef8db1f1ac8f272c37f5d8b62578a4be','2012-05-09 14:34:52'),(5,5,'6a520735da44202376a725e16bed1aa362853a91','2016-04-21 12:52:00'),(6,6,'d89e50e46fe2f3d837dd4c124557dfca6afa02c6','2016-04-21 12:52:01'),(7,7,'83c8c55d4d7220feb7e5ed38c352430ba4431926','2016-04-21 12:54:55');
/*!40000 ALTER TABLE `tastypie_apikey` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `thumbnail_kvstore`
--

DROP TABLE IF EXISTS `thumbnail_kvstore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `thumbnail_kvstore` (
  `key` varchar(200) NOT NULL,
  `value` longtext NOT NULL,
  PRIMARY KEY (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `thumbnail_kvstore`
--

LOCK TABLES `thumbnail_kvstore` WRITE;
/*!40000 ALTER TABLE `thumbnail_kvstore` DISABLE KEYS */;
/*!40000 ALTER TABLE `thumbnail_kvstore` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-08-25 19:15:29
