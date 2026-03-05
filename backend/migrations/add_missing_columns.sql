-- 添加党员管理缺失的字段
-- 执行方式：mysql -u root -ptruth party_building < migrations/add_missing_columns.sql

USE party_building;

-- 添加身份证号字段
ALTER TABLE party_members ADD COLUMN id_card VARCHAR(18) COMMENT '身份证号' AFTER gender;

-- 添加学历字段
ALTER TABLE party_members ADD COLUMN education VARCHAR(20) COMMENT '学历' AFTER birth_date;

-- 添加现居住地址字段
ALTER TABLE party_members ADD COLUMN address VARCHAR(500) COMMENT '现居住地址' AFTER email;

-- 添加工作单位字段
ALTER TABLE party_members ADD COLUMN work_unit VARCHAR(200) COMMENT '工作单位' AFTER address;

-- 添加职务/职称字段
ALTER TABLE party_members ADD COLUMN job_title VARCHAR(100) COMMENT '职务/职称' AFTER work_unit;

-- 添加入党申请书提交时间字段
ALTER TABLE party_members ADD COLUMN application_date DATE COMMENT '入党申请书提交时间' AFTER join_date;

-- 添加确定为积极分子时间字段
ALTER TABLE party_members ADD COLUMN activist_date DATE COMMENT '确定为积极分子时间' AFTER application_date;

-- 添加确定为发展对象时间字段
ALTER TABLE party_members ADD COLUMN candidate_date DATE COMMENT '确定为发展对象时间' AFTER activist_date;

-- 添加接收为预备党员时间字段
ALTER TABLE party_members ADD COLUMN provisional_date DATE COMMENT '接收为预备党员时间' AFTER candidate_date;

-- 添加转正时间字段
ALTER TABLE party_members ADD COLUMN full_member_date DATE COMMENT '转正时间' AFTER provisional_date;

-- 添加党内职务字段
ALTER TABLE party_members ADD COLUMN party_position VARCHAR(100) COMMENT '党内职务' AFTER full_member_date;

-- 添加介绍人1字段
ALTER TABLE party_members ADD COLUMN introducer_1 VARCHAR(50) COMMENT '介绍人1' AFTER party_position;

-- 添加介绍人2字段
ALTER TABLE party_members ADD COLUMN introducer_2 VARCHAR(50) COMMENT '介绍人2' AFTER introducer_1;

-- 添加是否流动党员字段
ALTER TABLE party_members ADD COLUMN is_mobile BOOLEAN DEFAULT FALSE COMMENT '是否流动党员' AFTER introducer_2;

-- 添加流动类型字段
ALTER TABLE party_members ADD COLUMN mobile_type VARCHAR(20) COMMENT '流动类型（流出/流入）' AFTER is_mobile;

-- 添加流动原因字段
ALTER TABLE party_members ADD COLUMN mobile_reason VARCHAR(500) COMMENT '流动原因' AFTER mobile_type;

-- 添加月收入字段
ALTER TABLE party_members ADD COLUMN monthly_income DECIMAL(10,2) COMMENT '月收入' AFTER mobile_reason;

-- 添加党费标准字段
ALTER TABLE party_members ADD COLUMN fee_standard DECIMAL(10,2) COMMENT '党费标准（月缴金额）' AFTER monthly_income;

-- 添加所属支部ID字段
ALTER TABLE party_members ADD COLUMN branch_id VARCHAR(36) COMMENT '所属支部ID' AFTER fee_standard;

-- 查看修改后的表结构
DESCRIBE party_members;
