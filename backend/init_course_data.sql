-- 初始化课程文档数据
-- 注意：运行此脚本前请确保数据库表已创建

-- 插入示例目录
INSERT INTO course_categories (id, name, parent_id, `order`, created_at, updated_at) VALUES
('cat-001', 'AI基础知识', NULL, 0, NOW(), NOW()),
('cat-002', 'AI工具应用', NULL, 1, NOW(), NOW()),
('cat-003', '什么是AI', 'cat-001', 0, NOW(), NOW()),
('cat-004', 'AI的历史', 'cat-001', 1, NOW(), NOW()),
('cat-005', 'ChatGPT使用指南', 'cat-002', 0, NOW(), NOW());

-- 插入示例文档
-- 注意：这里的file_path应该对应实际创建的Markdown文件
INSERT INTO course_documents (id, title, summary, file_path, category_id, `order`, created_at, updated_at) VALUES
('doc-001', 'AI是什么？', '理解人工智能的基本概念和定义', 'course_docs/doc-001/content.md', 'cat-003', 0, NOW(), NOW()),
('doc-002', 'AI的发展历程', '从图灵测试到ChatGPT：AI技术的演进之路', 'course_docs/doc-002/content.md', 'cat-004', 0, NOW(), NOW()),
('doc-003', 'ChatGPT入门', '快速上手ChatGPT，开启AI对话之旅', 'course_docs/doc-003/content.md', 'cat-005', 0, NOW(), NOW());

