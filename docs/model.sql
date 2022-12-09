create database if not exists `recruit-system` ;
use `recruit-system`;

CREATE TABLE `bio_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `person_id` int(11) NOT NULL COMMENT '用户ID',
  `url` varchar(1024) NOT NULL COMMENT '简历pdf地址',
  `job_id` int(11) NOT NULL COMMENT '岗位ID',
  `status` int(11) DEFAULT '0' COMMENT '状态(0-未处理, 1-已处理)',
  `interview_content` text COMMENT '面试内容',
  `interview_title` varchar(256) DEFAULT NULL COMMENT '面试邮件',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8  COMMENT='投递记录表';

CREATE TABLE `hr` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `username` varchar(256) NOT NULL COMMENT '用户名',
  `password` varchar(256) DEFAULT NULL COMMENT '密码',
  `name` varchar(64) DEFAULT NULL COMMENT '姓名',
  `gender` int(11) DEFAULT NULL COMMENT '性别',
  `company` varchar(256) DEFAULT NULL COMMENT '公司',
  `telephone` varchar(24) NOT NULL COMMENT '联系电话',
  `email` varchar(45) DEFAULT 'NULL' COMMENT '邮箱',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COMMENT='求职者表';

CREATE TABLE `job` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `name` varchar(64) DEFAULT NULL COMMENT '岗位名称',
  `desc` text COMMENT '岗位描述',
  `city` varchar(64) DEFAULT NULL COMMENT '所在城市',
  `salary_low` float DEFAULT NULL COMMENT '最低工资，单位K',
  `salary_high` float DEFAULT NULL COMMENT '最高工资，单位K',
  `is_done` int(11) DEFAULT '1' COMMENT '是否在招',
  `degree` int(11) DEFAULT NULL COMMENT '学历要求',
  `experience` int(11) DEFAULT NULL COMMENT '工作经验要求',
  `hr_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=106 DEFAULT CHARSET=utf8 COMMENT='岗位表';

CREATE TABLE `person` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `username` varchar(256) NOT NULL COMMENT '用户名',
  `password` varchar(256) DEFAULT NULL COMMENT '密码',
  `name` varchar(64) DEFAULT NULL COMMENT '姓名',
  `gender` int(11) DEFAULT NULL COMMENT '性别',
  `school` varchar(256) DEFAULT NULL COMMENT '学校',
  `degree` varchar(256) DEFAULT NULL COMMENT '学历',
  `telephone` varchar(24) NOT NULL COMMENT '联系电话',
  `email` varchar(45) DEFAULT 'NULL' COMMENT '邮箱',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COMMENT='求职者表';

CREATE TABLE `star` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `person_id` int(11) NOT NULL COMMENT '用户ID',
  `job_id` int(11) NOT NULL COMMENT '岗位ID',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=104 DEFAULT CHARSET=utf8 COMMENT='岗位收藏夹表';

