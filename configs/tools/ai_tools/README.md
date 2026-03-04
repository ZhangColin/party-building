# 工具配置说明

## 分类顺序控制

分类的顺序通过 `categories.yaml` 配置文件控制。

### categories.yaml 格式

```yaml
categories:
  - name: "内容生成"
    order: 1          # 数字越小越靠前
    icon: "sparkles"  # 分类图标（可选）
  
  - name: "智能体"
    order: 2
    icon: "command-line"
```

**说明：**
- `name`: 分类名称（必须与工具配置中的 `category` 字段一致）
- `order`: 排序顺序，数字越小越靠前（默认 999）
- `icon`: 分类图标标识（可选，如果未配置则使用该分类下第一个工具的图标）

## 工具顺序控制

每个工具的顺序通过工具配置文件中的 `order` 字段控制。

### 工具配置文件格式

```yaml
tool_id: text_gen
name: 文生文
category: "内容生成"
order: 1              # 数字越小越靠前，默认 999
# ... 其他字段
```

**说明：**
- `order`: 工具在所属分类中的排序顺序，数字越小越靠前
- 如果不指定 `order`，默认值为 999（会排在最后）
- 同一分类内的工具按 `order` 值从小到大排序

## 示例

假设有以下配置：

**categories.yaml:**
```yaml
categories:
  - name: "内容生成"
    order: 1
  - name: "智能体"
    order: 2
```

**工具配置:**
- `text_gen.yaml`: category="内容生成", order=1
- `image_gen.yaml`: category="内容生成", order=2
- `prompt_wizard.yaml`: category="智能体", order=1

**最终显示顺序：**
1. 内容生成（分类 order=1）
   - 文生文（工具 order=1）
   - 文生图（工具 order=2）
2. 智能体（分类 order=2）
   - AI 提示词向导（工具 order=1）

## 注意事项

1. 如果分类在 `categories.yaml` 中未配置，该分类的 `order` 默认为 999
2. 如果工具未指定 `order`，默认值为 999
3. 分类图标优先使用 `categories.yaml` 中配置的图标，如果未配置则使用该分类下第一个工具的图标

