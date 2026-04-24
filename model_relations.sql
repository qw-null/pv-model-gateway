/*
 Navicat Premium Dump SQL

 Source Server         : mysql-Docker-Oneapi
 Source Server Type    : MySQL
 Source Server Version : 80036 (8.0.36)
 Source Host           : 127.0.0.1:3306
 Source Schema         : pv_gateway

 Target Server Type    : MySQL
 Target Server Version : 80036 (8.0.36)
 File Encoding         : 65001

 Date: 24/04/2026 18:11:45
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for model_relations
-- ----------------------------
DROP TABLE IF EXISTS `model_relations`;
CREATE TABLE `model_relations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `from_model_id` int NOT NULL,
  `to_model_id` int NOT NULL,
  `relation_type` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_model_relations_to_model_id` (`to_model_id`),
  KEY `ix_model_relations_from_model_id` (`from_model_id`),
  CONSTRAINT `model_relations_ibfk_1` FOREIGN KEY (`from_model_id`) REFERENCES `model_records` (`id`) ON DELETE CASCADE,
  CONSTRAINT `model_relations_ibfk_2` FOREIGN KEY (`to_model_id`) REFERENCES `model_records` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=94 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of model_relations
-- ----------------------------
BEGIN;
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (1, 26, 13, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (2, 1, 3, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (3, 1, 4, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (4, 1, 17, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (5, 1, 2, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (6, 2, 1, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (7, 2, 3, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (8, 2, 4, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (9, 2, 17, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (10, 3, 1, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (11, 3, 2, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (12, 3, 4, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (13, 3, 17, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (14, 3, 1, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (15, 4, 1, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (16, 4, 3, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (17, 4, 6, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (18, 4, 17, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (19, 4, 1, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (20, 4, 3, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (21, 5, 4, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (22, 5, 7, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (23, 5, 4, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (24, 6, 1, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (25, 6, 4, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (26, 6, 7, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (27, 6, 1, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (28, 6, 4, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (29, 7, 6, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (30, 7, 5, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (31, 7, 13, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (32, 7, 8, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (33, 7, 6, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (34, 7, 5, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (35, 13, 7, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (36, 13, 8, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (37, 13, 9, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (38, 13, 10, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (39, 13, 11, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (40, 13, 12, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (41, 13, 7, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (42, 8, 13, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (43, 8, 14, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (44, 8, 13, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (45, 8, 9, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (46, 8, 10, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (47, 8, 11, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (48, 8, 12, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (49, 9, 13, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (50, 9, 14, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (51, 9, 13, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (52, 9, 8, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (53, 9, 10, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (54, 9, 11, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (55, 9, 12, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (56, 10, 13, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (57, 10, 14, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (58, 10, 13, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (59, 10, 8, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (60, 10, 9, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (61, 10, 11, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (62, 10, 12, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (63, 11, 13, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (64, 11, 14, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (65, 11, 13, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (66, 11, 8, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (67, 11, 9, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (68, 11, 10, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (69, 11, 12, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (70, 12, 13, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (71, 12, 14, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (72, 12, 13, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (73, 12, 8, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (74, 12, 9, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (75, 12, 10, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (76, 12, 11, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (77, 14, 8, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (78, 14, 15, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (79, 14, 16, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (80, 14, 8, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (81, 15, 14, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (82, 15, 14, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (83, 15, 16, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (84, 16, 14, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (85, 16, 14, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (86, 16, 15, 'conflicts_with');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (87, 17, 1, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (88, 17, 3, 'pre');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (89, 17, 5, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (90, 17, 6, 'post');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (91, 17, 1, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (92, 17, 3, 'depends_on');
INSERT INTO `model_relations` (`id`, `from_model_id`, `to_model_id`, `relation_type`) VALUES (93, 17, 4, 'conflicts_with');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
