create database if not exists `recruit-system` ;
use `recruit-system`;
-- person 表
create table if not exists `person`
(
    `id` int not null auto_increment comment 'id' primary key ,
    `username` varchar(256) not null comment '用户名',
    `password` varchar(256) null comment '密码',
    `name` varchar(64) null comment '姓名',
    `gender` int null comment '性别',
    `birth_date` datetime not null comment '出生日期',
    `school` varchar(256) null comment '学校',
    `degree` varchar(256) null comment '学历',
    `telephone` varchar(24) not null comment '联系电话',
    `email` varchar(45) default 'NULL' null comment '邮箱'
) comment '求职者表';

-- HR 表
create table if not exists `hr`
(
    `id` int not null auto_increment comment 'id' primary key ,
    `username` varchar(256) not null comment '用户名',
    `password` varchar(256) null comment '密码',
    `name` varchar(64) null comment '姓名',
    `gender` int null comment '性别(0-女, 1-男)',
    `company` varchar(256) comment '公司',
    `telephone` varchar(24) not null comment '联系电话',
    `email` varchar(45) default 'NULL' null comment '邮箱'
) comment '求职者表';

-- job 表
create table if not exists `job`
(
`id` int not null auto_increment comment 'id' primary key,
`name` varchar(64) null comment '岗位名称',
`desc` text null comment '岗位描述',
`city` varchar(64) null comment '所在城市',
`salary_low` float null comment '最低工资，单位K',
`salary_high` float null comment '最高工资，单位K',
`is_done` int null comment '是否在招' DEFAULT 1,
`degree` int null comment '学历要求',
`experience` int null comment '工作经验要求',
`hr_id` int null comment 'HR id'
) comment '工作表';

-- star表
create table if not exists `star`
(
`id` int not null auto_increment comment 'id' primary key,
`person_id` int not null comment '用户ID',
`job_id` int not null comment '岗位ID'
) comment '岗位收藏夹表';

-- bio_record 表
create table if not exists `bio_record`
(
    `id` int not null auto_increment comment 'id' primary key,
    `person_id` int not null comment '用户ID',
    `url` varchar(1024) not null comment '简历pdf地址',
    `job_id` int not null comment '岗位ID',
    `status` int null comment '状态(0-未处理, 1-已处理)' DEFAULT 0,
    `create_time` datetime not null comment '创建时间' default CURRENT_TIMESTAMP,
    `update_time` datetime not null comment '更新时间' default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
)

