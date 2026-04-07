-- 校园失物招领平台数据库初始化脚本

DROP TABLE IF EXISTS "Messages", "Notifications", "Items", "Users" CASCADE;

CREATE TABLE "Users" (
    "UserID" SERIAL PRIMARY KEY,
    "Username" VARCHAR(50) UNIQUE NOT NULL,
    "Password" VARCHAR(255) NOT NULL,
    "PasswordHash" VARCHAR(256) NOT NULL,
    "UserRole" VARCHAR(20) NOT NULL CHECK ("UserRole" IN ('普通用户', '志愿者', '管理员')),
    "RegistrationDate" TIMESTAMPTZ DEFAULT NOW(),
    "SecurityQuestion" VARCHAR(255) NULL,
    "SecurityAnswerHash" VARCHAR(256) NULL
);

CREATE TABLE "Items" (
    "ItemID" VARCHAR(10) PRIMARY KEY,
    "UserID" INT REFERENCES "Users"("UserID") ON DELETE SET NULL,
    "ItemType" VARCHAR(10) NOT NULL CHECK ("ItemType" IN ('Lost', 'Found')),
    "ItemName" VARCHAR(100) NOT NULL,
    "Description" TEXT,
    "Category" VARCHAR(50),
    "Color" VARCHAR(20),
    "Location" VARCHAR(200),
    "EventTime" TIMESTAMPTZ,
    "PostTime" TIMESTAMPTZ DEFAULT NOW(),
    "ImagePath" VARCHAR(255),
    "ItemStatus" VARCHAR(20) NOT NULL DEFAULT '未找到' CHECK ("ItemStatus" IN ('未找到', '正在联系中', '已找回', '已删除')),
    "MatchItemID" VARCHAR(10) NULL
);

CREATE TABLE "Notifications" (
    "NotificationID" SERIAL PRIMARY KEY,
    "UserID" INT REFERENCES "Users"("UserID") ON DELETE CASCADE,
    "Message" TEXT NOT NULL,
    "IsRead" BOOLEAN NOT NULL DEFAULT FALSE,
    "CreationTime" TIMESTAMPTZ DEFAULT NOW(),
    "NotificationType" VARCHAR(20) NOT NULL CHECK ("NotificationType" IN ('General', 'Match', 'Claim', 'NewMessage')),
    "RelatedItemID_1" VARCHAR(10) NULL,
    "RelatedItemID_2" VARCHAR(10) NULL
);

CREATE TABLE "Messages" (
    "MessageID" SERIAL PRIMARY KEY,
    "SenderID" INT NOT NULL,
    "ReceiverID" INT,
    "LostItemID" VARCHAR(10) NOT NULL,
    "FoundItemID" VARCHAR(10) NOT NULL,
    "Content" TEXT NOT NULL,
    "SentTime" TIMESTAMPTZ DEFAULT NOW(),
    "IsRead" BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX "idx_items_type_status_post_time"
ON "Items" ("ItemType", "ItemStatus", "PostTime" DESC);

CREATE INDEX "idx_items_user_status"
ON "Items" ("UserID", "ItemStatus");

CREATE INDEX "idx_notifications_user_created"
ON "Notifications" ("UserID", "CreationTime" DESC);

CREATE INDEX "idx_messages_pair_time"
ON "Messages" ("LostItemID", "FoundItemID", "SentTime" ASC);

INSERT INTO "Users" ("Username", "Password", "PasswordHash", "UserRole", "SecurityQuestion", "SecurityAnswerHash") VALUES
('admin', '', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', '管理员', '这个程序什么时候第一次完整运行？', '6292df4465e7b3e221a66eb83bcda2fb81301db91d0fedf18fbcf05029c99674'),
('volunteer1', '', '25a21eab5feca60534fc732ff65e27984b61e43d0c7a4614b9710cd01456c37a', '志愿者', '我最喜欢的桌游是什么？', '72730d7516fb6c51503936e978181e2c0c1a5b996032ef69ad0d728eaa6ad206'),
('user1', '', 'ee79976c9380d5e337fc1c095ece8c8f22f91f306ceeb161fa51fecede2c4ba1', '普通用户', '我最喜欢的运动是什么？', '217a257fb363ed862f2eadc88261372a8d8aee79124b334828619f5d910af982'),
('user2', '', '33a7d3da476a32ac237b3f603a1be62fad00299e0d4b5a8db8d913104edec629', '普通用户', '我最喜欢的颜色是什么？', 'ed7d2c54184be5f5b81cbcae880942acec9635014aad20bab6cca1d68dbe3f75'),
('user3', '', 'afb47e00531153e93808589e43d02c11f6398c5bc877f7924cebca8211c8dd18', '普通用户', '我的宠物的名字是？', '291b0888f1c619c377d6bea46669ec27ef8a4ffd7ed68bd21b351fa4a65cdf9d'),
('volunteer2', '', '66276e7280fc7c734d9afc08ac94b646f042d50af0ee4c83cd3a8d2b733b2a75', '志愿者', '我最喜欢的课程是什么？', 'fc93dcab1fd417be0b069226551beba46b257c663c53a1f4ee18ad67fe509041');

INSERT INTO "Items" ("UserID", "ItemID", "ItemType", "ItemName", "Category", "Color", "Location", "Description", "EventTime", "ImagePath") VALUES
-- 失物
(3, 'L100000001', 'Lost', '一个球', '其他', '多色', '西土城校区：体育场', '在体育场丢了一个球，失主请联系。', NOW() - INTERVAL '1 day', NULL),
(4, 'L100000002', 'Lost', '一把吉他', '其他', '木色', '沙河校区：学活', '在学生活动中心丢了一把吉他。', NOW() - INTERVAL '2 day', NULL),
(5, 'L100000003', 'Lost', '一袋水果', '其他', '多色', '沙河校区：南区食堂', '在食堂餐桌上丢的，还很新鲜。', NOW() - INTERVAL '3 day', NULL),
(3, 'L100000004', 'Lost', '一条裤子', '衣物', '蓝色', '西土城校区：学十一公寓', '在公寓楼下丢的。', NOW() - INTERVAL '4 day', NULL),
(4, 'L100000005', 'Lost', '一顶帽子', '衣物', '黑色', '沙河校区：运动场', '在操场看台丢的。', NOW() - INTERVAL '5 day', NULL),
(5, 'L100000006', 'Lost', '一个哑铃', '其他', '银色', '沙河校区：教学实验综合楼', '在健身房角落丢的。', NOW() - INTERVAL '6 day', NULL),
(3, 'L100000007', 'Lost', '一个充电器', '电子产品', '白色', '西土城校区：图书馆', '在图书馆座位上丢的。', NOW() - INTERVAL '7 day', NULL),
(4, 'L100000008', 'Lost', '一个吹风机', '电子产品', '粉色', '沙河校区：雁北园A B C D1宿舍楼', '在公共卫生间丢的。', NOW() - INTERVAL '8 day', NULL),
(5, 'L100000009', 'Lost', '一支笔', '书籍', '黑色', '西土城校区：教一楼', '在教室地上丢的。', NOW() - INTERVAL '9 day', NULL),
(3, 'L100000010', 'Lost', '一根数据线', '电子产品', '白色', '沙河校区：智工楼', '在实验室丢的。', NOW() - INTERVAL '10 day', NULL),
(4, 'L100000011', 'Lost', '一双鞋子', '衣物', '白色', '西土城校区：体育馆', '在体育馆更衣室丢的。', NOW() - INTERVAL '11 day', NULL),
(5, 'L100000012', 'Lost', '一个行李箱', '其他', '蓝色', '沙河校区：西门', '在校门口丢的，无人看管。', NOW() - INTERVAL '12 day', NULL),
(3, 'L100000013', 'Lost', '一块手表', '电子产品', '黑色', '西土城校区：科研楼', '在楼道丢的。', NOW() - INTERVAL '13 day', NULL),
(4, 'L100000014', 'Lost', '一个玩具', '其他', '黄色', '沙河校区：理学院', '在学院草坪上丢的。', NOW() - INTERVAL '14 day', NULL),
(5, 'L100000015', 'Lost', '一个台灯', '电子产品', '白色', '西土城校区：学九公寓', '在公寓自习室丢的。', NOW() - INTERVAL '15 day', NULL),
(3, 'L100000016', 'Lost', '一个手办', '其他', '多色', '沙河校区：S6宿舍楼', '在宿舍楼下丢的。', NOW() - INTERVAL '1 day', NULL),
(4, 'L100000017', 'Lost', '沐浴露和洗发水', '其他', '透明', '西土城校区：学八公寓', '在公共浴室丢的。', NOW() - INTERVAL '2 day', NULL),
(5, 'L100000018', 'Lost', '一个平板电脑', '电子产品', '深空灰', '沙河校区：公共教学楼', '在教室丢的。', NOW() - INTERVAL '3 day', NULL),
(3, 'L100000019', 'Lost', '一套餐具', '其他', '银色', '西土城校区：综合食堂', '在食堂丢的。', NOW() - INTERVAL '4 day', NULL),
(4, 'L100000020', 'Lost', '一件衣服', '衣物', '白色', '沙河校区：运动场', '在操场上丢的。', NOW() - INTERVAL '5 day', NULL),
(5, 'L100000021', 'Lost', '一本书', '书籍', '多色', '西土城校区：图书馆', '在图书馆丢的。', NOW() - INTERVAL '6 day', NULL),
(3, 'L100000022', 'Lost', '一个书包', '其他', '黑色', '沙河校区：S3工程实验楼', '在实验室丢的。', NOW() - INTERVAL '7 day', NULL),
(4, 'L100000023', 'Lost', '一部手机', '电子产品', '蓝色', '西土城校区：科学会堂', '在会堂丢的。', NOW() - INTERVAL '8 day', NULL),
(5, 'L100000024', 'Lost', '一份早餐', '其他', '多色', '沙河校区：学生食堂', '在食堂丢的。', NOW() - INTERVAL '9 day', NULL),
(3, 'L100000025', 'Lost', '一个水瓶', '其他', '透明', '西土城校区：教四楼', '在教室丢的。', NOW() - INTERVAL '10 day', NULL),
(4, 'L100000026', 'Lost', '一台笔记本电脑', '电子产品', '银色', '沙河校区：图书馆', '在图书馆丢的。', NOW() - INTERVAL '11 day', NULL),
(5, 'L100000027', 'Lost', '一个篮球', '其他', '橙色', '西土城校区：篮球场', '在篮球场丢的。', NOW() - INTERVAL '12 day', NULL),
(3, 'L100000028', 'Lost', '一把雨伞', '其他', '黑色', '沙河校区：数媒楼', '在教学楼门口丢的。', NOW() - INTERVAL '13 day', NULL),
(4, 'L100000029', 'Lost', '一条项链', '其他', '金色', '西土城校区：学生活动中心', '在活动中心丢的。', NOW() - INTERVAL '14 day', NULL),
(5, 'L100000030', 'Lost', '一条围巾', '衣物', '格子', '沙河校区：综合办公楼', '在办公楼丢的。', NOW() - INTERVAL '15 day', NULL),
(3, 'L100000031', 'Lost', '一副眼镜', '其他', '黑色', '西土城校区：教三楼', '在教室丢的。', NOW() - INTERVAL '1 day', NULL),
(4, 'L100000032', 'Lost', '一本护照', '证件', '蓝色', '沙河校区：东配楼', '在教学楼丢的。', NOW() - INTERVAL '2 day', NULL),
(5, 'L100000033', 'Lost', '一本结婚证', '证件', '红色', '沙河校区：网安楼', '在网安楼丢的。', NOW() - INTERVAL '3 day', NULL),
(3, 'L100000034', 'Lost', '一个充电宝', '电子产品', '黑色', '西土城校区：学五公寓', '在公寓楼下丢的。', NOW() - INTERVAL '4 day', NULL),
(4, 'L100000035', 'Lost', '一个钱包', '证件', '棕色', '沙河校区：快递驿站', '在快递站丢的。', NOW() - INTERVAL '5 day', NULL),
(5, 'L100000036', 'Lost', '一串钥匙', '钥匙', '银色', '西土城校区：学三公寓', '在公寓楼道丢的。', NOW() - INTERVAL '6 day', NULL),
(3, 'L100000037', 'Lost', '一台相机', '电子产品', '黑色', '沙河校区：医务室', '在医务室丢的。', NOW() - INTERVAL '7 day', NULL),
(4, 'L100000038', 'Lost', '一个快递', '其他', '多色', '西土城校区：快递站', '在快递站丢的。', NOW() - INTERVAL '8 day', NULL),
(4, 'L100000039', 'Lost', '一副耳塞', '电子产品', '白色', '沙河校区：S5宿舍楼', '在宿舍楼丢的。', NOW() - INTERVAL '9 day', NULL),

-- 拾物
(5, 'F200000001', 'Found', '一个球', '其他', '多色', '西土城校区：体育场', '在体育场捡到了一个球，失主请联系。', NOW() - INTERVAL '1 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475862/sample1_jwy8nm.jpg'),
(3, 'F200000002', 'Found', '一把吉他', '其他', '木色', '沙河校区：学活', '在学生活动中心捡到一把吉他。', NOW() - INTERVAL '2 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475862/sample2_ep3rwm.jpg'),
(4, 'F200000003', 'Found', '一袋水果', '其他', '多色', '沙河校区：南区食堂', '在食堂餐桌上发现的，还很新鲜。', NOW() - INTERVAL '3 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475862/sample3_augtpf.jpg'),
(5, 'F200000004', 'Found', '一条裤子', '衣物', '蓝色', '西土城校区：学十一公寓', '在公寓楼下发现的。', NOW() - INTERVAL '4 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475863/sample4_xdiweb.jpg'),
(3, 'F200000005', 'Found', '一顶帽子', '衣物', '黑色', '沙河校区：运动场', '在操场看台捡到的。', NOW() - INTERVAL '5 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475863/sample5_pllpxt.jpg'),
(4, 'F200000006', 'Found', '一个哑铃', '其他', '银色', '沙河校区：教学实验综合楼', '在健身房角落发现的。', NOW() - INTERVAL '6 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475863/sample6_i031tn.jpg'),
(5, 'F200000007', 'Found', '一个充电器', '电子产品', '白色', '西土城校区：图书馆', '在图书馆座位上捡到的。', NOW() - INTERVAL '7 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475863/sample7_o2etgl.jpg'),
(3, 'F200000008', 'Found', '一个吹风机', '电子产品', '粉色', '沙河校区：雁北园A B C D1宿舍楼', '在公共卫生间捡到的。', NOW() - INTERVAL '8 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475863/sample8_feevsa.jpg'),
(4, 'F200000009', 'Found', '一支笔', '书籍', '黑色', '西土城校区：教一楼', '在教室地上捡到的。', NOW() - INTERVAL '9 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475863/sample9_ha6iqn.jpg'),
(5, 'F200000010', 'Found', '一根数据线', '电子产品', '白色', '沙河校区：智工楼', '在实验室捡到的。', NOW() - INTERVAL '10 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475865/sample10_o18pm9.jpg'),
(3, 'F200000011', 'Found', '一双鞋子', '衣物', '白色', '西土城校区：体育馆', '在体育馆更衣室发现的。', NOW() - INTERVAL '11 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475885/sample11_xdpw2b.jpg'),
(4, 'F200000012', 'Found', '一个行李箱', '其他', '蓝色', '沙河校区：西门', '在校门口发现的，无人看管。', NOW() - INTERVAL '12 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475885/sample12_kqsxu1.jpg'),
(5, 'F200000013', 'Found', '一块手表', '电子产品', '黑色', '西土城校区：科研楼', '在楼道捡到的。', NOW() - INTERVAL '13 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475886/sample13_kyrb17.jpg'),
(3, 'F200000014', 'Found', '一个玩具', '其他', '黄色', '沙河校区：理学院', '在学院草坪上发现的。', NOW() - INTERVAL '14 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475886/sample14_wdtuo2.jpg'),
(4, 'F200000015', 'Found', '一个台灯', '电子产品', '白色', '西土城校区：学九公寓', '在公寓自习室捡到的。', NOW() - INTERVAL '15 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475886/sample15_gjqskb.jpg'),
(5, 'F200000016', 'Found', '一个手办', '其他', '多色', '沙河校区：S6宿舍楼', '在宿舍楼下捡到的。', NOW() - INTERVAL '1 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475886/sample16_fufhlh.jpg'),
(3, 'F200000017', 'Found', '沐浴露和洗发水', '其他', '透明', '西土城校区：学八公寓', '在公共浴室捡到的。', NOW() - INTERVAL '2 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475886/sample17_ftlnck.jpg'),
(4, 'F200000018', 'Found', '一个平板电脑', '电子产品', '深空灰', '沙河校区：公共教学楼', '在教室捡到的。', NOW() - INTERVAL '3 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475886/sample18_wschyg.jpg'),
(5, 'F200000019', 'Found', '一套餐具', '其他', '银色', '西土城校区：综合食堂', '在食堂捡到的。', NOW() - INTERVAL '4 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475886/sample19_mqmgvb.jpg'),
(3, 'F200000020', 'Found', '一件衣服', '衣物', '白色', '沙河校区：运动场', '在操场上捡到的。', NOW() - INTERVAL '5 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475887/sample20_aoojpx.jpg'),
(4, 'F200000021', 'Found', '一本书', '书籍', '多色', '西土城校区：图书馆', '在图书馆捡到的。', NOW() - INTERVAL '6 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475887/sample21_xsthzf.jpg'),
(5, 'F200000022', 'Found', '一个书包', '其他', '黑色', '沙河校区：S3工程实验楼', '在实验室捡到的。', NOW() - INTERVAL '7 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475887/sample22_kubwv3.jpg'),
(3, 'F200000023', 'Found', '一部手机', '电子产品', '蓝色', '西土城校区：科学会堂', '在会堂捡到的。', NOW() - INTERVAL '8 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475897/sample23_t7xowd.jpg'),
(4, 'F200000024', 'Found', '一份早餐', '其他', '多色', '沙河校区：学生食堂', '在食堂捡到的。', NOW() - INTERVAL '9 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475897/sample24_fja7xw.jpg'),
(5, 'F200000025', 'Found', '一个水瓶', '其他', '透明', '西土城校区：教四楼', '在教室捡到的。', NOW() - INTERVAL '10 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475897/sample25_igrno3.jpg'),
(3, 'F200000026', 'Found', '一台笔记本电脑', '电子产品', '银色', '沙河校区：图书馆', '在图书馆捡到的。', NOW() - INTERVAL '11 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475897/sample26_shnhhg.jpg'),
(4, 'F200000027', 'Found', '一个篮球', '其他', '橙色', '西土城校区：篮球场', '在篮球场捡到的。', NOW() - INTERVAL '12 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475897/sample27_bb08d6.jpg'),
(5, 'F200000028', 'Found', '一把雨伞', '其他', '黑色', '沙河校区：数媒楼', '在教学楼门口捡到的。', NOW() - INTERVAL '13 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475897/sample28_jcrelf.jpg'),
(3, 'F200000029', 'Found', '一条项链', '其他', '金色', '西土城校区：学生活动中心', '在活动中心捡到的。', NOW() - INTERVAL '14 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475898/sample29_ocjrkt.jpg'),
(4, 'F200000030', 'Found', '一条围巾', '衣物', '格子', '沙河校区：综合办公楼', '在办公楼捡到的。', NOW() - INTERVAL '15 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475898/sample30_gumvxh.jpg'),
(5, 'F200000031', 'Found', '一副眼镜', '其他', '黑色', '西土城校区：教三楼', '在教室捡到的。', NOW() - INTERVAL '1 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475898/sample31_mquvn9.jpg'),
(3, 'F200000032', 'Found', '一本护照', '证件', '蓝色', '沙河校区：东配楼', '在教学楼捡到的。', NOW() - INTERVAL '2 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475898/sample32_kbv5hj.jpg'),
(4, 'F200000033', 'Found', '一本结婚证', '证件', '红色', '沙河校区：网安楼', '在网安楼捡到的。', NOW() - INTERVAL '3 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475899/sample33_fgynay.jpg'),
(5, 'F200000034', 'Found', '一个充电宝', '电子产品', '黑色', '西土城校区：学五公寓', '在公寓楼下捡到的。', NOW() - INTERVAL '4 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475898/sample34_jay2zq.jpg'),
(3, 'F200000035', 'Found', '一个钱包', '证件', '棕色', '沙河校区：快递驿站', '在快递站捡到的。', NOW() - INTERVAL '5 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475899/sample35_ib6lak.jpg'),
(4, 'F200000036', 'Found', '一串钥匙', '钥匙', '银色', '西土城校区：学三公寓', '在公寓楼道捡到的。', NOW() - INTERVAL '6 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475907/sample36_zac1le.jpg'),
(5, 'F200000037', 'Found', '一台相机', '电子产品', '黑色', '沙河校区：医务室', '在医务室捡到的。', NOW() - INTERVAL '7 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475907/sample37_sj57sz.jpg'),
(3, 'F200000038', 'Found', '一个快递', '其他', '多色', '西土城校区：快递站', '在快递站捡到的。', NOW() - INTERVAL '8 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475907/sample38_j7zgen.jpg'),
(4, 'F200000039', 'Found', '一副耳塞', '电子产品', '白色', '沙河校区：S5宿舍楼', '在宿舍楼捡到的。', NOW() - INTERVAL '9 day', 'https://res.cloudinary.com/dypmjysm4/image/upload/v1759475907/sample39_xstmo9.jpg');
