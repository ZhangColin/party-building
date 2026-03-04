-- ============================================
-- 作品展示模块 - 数据库迁移脚本
-- 创建日期: 2026-01-10
-- 说明: 创建作品分类表和作品表
-- ============================================

-- 创建作品分类表
CREATE TABLE IF NOT EXISTS work_categories (
    id VARCHAR(36) PRIMARY KEY COMMENT '分类ID（UUID）',
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '分类名称',
    icon VARCHAR(50) COMMENT '分类图标（heroicons名称）',
    `order` INT NOT NULL DEFAULT 0 COMMENT '排序顺序',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_order (`order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作品分类表';

-- 创建作品表
CREATE TABLE IF NOT EXISTS works (
    id VARCHAR(36) PRIMARY KEY COMMENT '作品ID（UUID）',
    name VARCHAR(100) NOT NULL COMMENT '作品名称',
    description VARCHAR(200) NOT NULL COMMENT '作品描述',
    category_id VARCHAR(36) NOT NULL COMMENT '所属分类ID',
    icon VARCHAR(50) COMMENT '图标标识（heroicons名称）',
    html_path VARCHAR(255) NOT NULL COMMENT 'HTML文件路径（相对于static目录）',
    `order` INT NOT NULL DEFAULT 0 COMMENT '排序顺序',
    visible BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否可见',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (category_id) REFERENCES work_categories(id) ON DELETE RESTRICT,
    INDEX idx_category_order (category_id, `order`),
    INDEX idx_visible (visible)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作品表';

-- 插入初始分类数据
INSERT INTO work_categories (id, name, icon, `order`) VALUES
('creative-design', '创意设计', 'sparkles', 1),
('data-visualization', '数据可视化', 'chart-bar', 2),
('interactive-animation', '交互动画', 'cursor-arrow-rays', 3)
ON DUPLICATE KEY UPDATE name=VALUES(name), icon=VALUES(icon), `order`=VALUES(`order`);

-- 插入示例作品数据（可选，用于测试）
-- INSERT INTO works (id, name, description, category_id, icon, html_path, `order`, visible) VALUES
-- ('interactive-card', '交互式卡片', '一个精美的交互式卡片效果展示', 'creative-design', 'star', 'works/html/interactive-card/index.html', 1, TRUE),
-- ('animated-button', '动画按钮集合', '多种创意动画按钮效果', 'creative-design', 'cursor-arrow-rays', 'works/html/animated-button/index.html', 2, TRUE),
-- ('chart-demo', '图表演示', '各种图表的可视化展示', 'data-visualization', 'presentation-chart-line', 'works/html/chart-demo/index.html', 1, TRUE)
-- ON DUPLICATE KEY UPDATE name=VALUES(name), description=VALUES(description), icon=VALUES(icon);

-- 验证表创建
SELECT 
    'work_categories' AS table_name,
    COUNT(*) AS category_count
FROM work_categories
UNION ALL
SELECT 
    'works' AS table_name,
    COUNT(*) AS work_count
FROM works;
