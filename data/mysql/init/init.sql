DROP TABLE IF EXISTS `available_url`;
CREATE TABLE `available_url`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `domain` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `maximum` int(10) NULL DEFAULT NULL,
  `interval` int(10) NULL DEFAULT NULL,
  `black` int(10) NULL DEFAULT 0,
  `remark` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name`) USING BTREE,
  INDEX `url`(`url`) USING BTREE,
  INDEX `domain`(`domain`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci;

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `available_count` int(10) NOT NULL,
  `send_count` int(10) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `username`(`username`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci;

INSERT INTO `message`.`available_url`(`name`, `domain`, `url`, `maximum`, `interval`, `black`, `remark`) VALUES ('chaoxing', 'passport2.chaoxing.com', 'http://passport2.chaoxing.com/register3', 3, 60, 0, NULL);
INSERT INTO `message`.`available_url`(`name`, `domain`, `url`, `maximum`, `interval`, `black`, `remark`) VALUES ('happigo', 'www.happigo.com', 'https://www.happigo.com/register/', 3, 60, 0, NULL);
INSERT INTO `message`.`available_url`(`name`, `domain`, `url`, `maximum`, `interval`, `black`, `remark`) VALUES ('pailixiang', 'heimaohui.pailixiang.com', 'http://heimaohui.pailixiang.com/register.html', 10, 60, 0, NULL);
INSERT INTO `message`.`available_url`(`name`, `domain`, `url`, `maximum`, `interval`, `black`, `remark`) VALUES ('morequick', 'itv.morequick.net', 'https://itv.morequick.net/register.html', 3, 60, 0, NULL);
INSERT INTO `message`.`available_url`(`name`, `domain`, `url`, `maximum`, `interval`, `black`, `remark`) VALUES ('asprova', 'www.asprova.cn', 'http://www.asprova.cn/register.html', 15, 30, 0, NULL);
/*
默认用户名密码为admin:admin
*/
INSERT INTO `message`.`user`(`id`, `username`, `password`, `available_count`, `send_count`) VALUES (1, 'admin', '21232f297a57a5a743894a0e4a801fc3', 1000, 0);
