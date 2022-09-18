ALTER USER root IDENTIFIED WITH mysql_native_password BY 'ctfVGBUIJ67gyBUINXERCTr6vt7bHNJ';
USE xedb;

ALTER USER `root`@`localhost` IDENTIFIED BY 'ctfVctyvgBNJOK789huoijpt7bHNJ',
       `root`@`localhost` PASSWORD EXPIRE NEVER;


CREATE TABLE `homes` (
  `property_id` int(14) UNSIGNED NOT NULL,
  `property_url` varchar(300) NOT NULL,
  `bedroom` int(10) UNSIGNED DEFAULT NULL,
  `bathroom` int(10) UNSIGNED DEFAULT NULL,
  `floor` float DEFAULT NULL,
  `house_reconstruction` int(10) UNSIGNED DEFAULT NULL,
  `building_space` varchar(50) DEFAULT NULL,
  `compass` varchar(50) DEFAULT NULL,
  `title` varchar(100) NOT NULL,
  `price` int(10) UNSIGNED NOT NULL,
  `door` bit(1) DEFAULT b'0',
  `canopy` bit(1) DEFAULT b'0',
  `heating` varchar(50) DEFAULT NULL,
  `description` varchar(200) DEFAULT NULL,
  `has_oil` bit(1) DEFAULT b'0',
  `reg_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `homes`
--

-- INSERT INTO `homes` (`property_id`, `property_url`, `bedroom`, `bathroom`, `floor`, `house_reconstruction`, `building_space`, `compass`, `title`, `price`, `door`, `canopy`, `heating`, `description`, `has_oil`, `reg_date`) VALUES
-- (21695315, 'https://www.xe.gr/property/d/enoikiaseis-katoikion/21695315/athhna-ellhnorwswn-700-128?first_in_widget_ad_id=785791174&rank_in_widget=16&widget_name=search+results+list', 2, 2, -0.5, NULL, 'Καλή', 'Διαμπερές', 'Διαμέρισμα προς ενοικίαση 128 τ.μ. Αθήνα (Ελληνορώσων) (Ιδιώτης) | xe.gr', 700, b'1', b'0', 'Αυτόνομη θέρμανση με ατομική εγκατάσταση', NULL, b'0', '2022-06-12 11:45:43');

-- ALTER TABLE `homes`
--   ADD PRIMARY KEY (`property_id`);
-- COMMIT;
