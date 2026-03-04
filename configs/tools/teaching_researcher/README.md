# 教研员工具集配置说明

本目录包含教研员工具集的配置文件。

## 📁 目录结构

```
teaching_researcher/
├── prompts/                      # 系统提示词文件目录
│   ├── chinese_teacher.md        # 语文教研员提示词
│   ├── math_teacher.md           # 数学教研员提示词
│   └── ...                       # 其他学科提示词
├── chinese_teacher.yaml          # 语文教研员工具配置
├── math_teacher.yaml             # 数学教研员工具配置
├── categories.yaml               # 分类配置
└── README.md                     # 本说明文档
```

## 🛠️ 配置文件说明

### 工具配置文件（*.yaml）

每个教研员工具的配置文件包含：

- `tool_id`: 工具唯一标识符
- `name`: 工具显示名称
- `description`: 工具描述
- `category`: 所属分类（学科）
- `icon`: 图标标识
- `visible`: 是否在工具选择器中显示
- `type`: 工具类型（normal/placeholder）
- `order`: 排序顺序
- `toolset_id`: 所属工具集ID（必须为 `teaching_researcher`）
- `system_prompt_file`: 系统提示词文件路径（相对于本目录）
- `welcome_message`: 欢迎语

### 系统提示词文件（prompts/*.md）

- 使用 Markdown 格式编写
- 建议结构：角色定位、专业领域、工作方法、教学理念等
- 可以包含任意长度的内容（数千字、数万字都可以）

### 分类配置文件（categories.yaml）

定义工具的分类结构和显示顺序：

- `name`: 分类名称（学科名称）
- `icon`: 分类图标
- `order`: 显示顺序

## 📝 添加新的教研员工具

### 步骤 1：创建系统提示词文件

在 `prompts/` 目录下创建 Markdown 文件，例如 `english_teacher.md`：

\`\`\`markdown
# 英语教研员 - 系统提示词

你是一位经验丰富的英语教研员...
\`\`\`

### 步骤 2：创建工具配置文件

在本目录下创建配置文件，例如 `english_teacher.yaml`：

\`\`\`yaml
tool_id: english_teacher
name: "英语教研员"
description: "专业的英语教学研究员"
category: "英语"
icon: "language"
visible: true
type: "normal"
order: 1
toolset_id: teaching_researcher
system_prompt_file: "prompts/english_teacher.md"
welcome_message: "你好！我是英语教研员..."
\`\`\`

### 步骤 3：更新分类配置（可选）

如果是新学科，在 `categories.yaml` 中添加分类：

\`\`\`yaml
- name: "英语"
  icon: "language"
  order: 3
\`\`\`

### 步骤 4：重启应用

重启后端服务，新的教研员工具即可使用。

## ⚠️ 注意事项

1. **toolset_id 必须为 `teaching_researcher`**：确保工具属于教研员工具集
2. **system_prompt_file 路径**：相对于本目录的路径
3. **tool_id 唯一性**：确保 tool_id 在整个系统中唯一
4. **文件编码**：所有文件使用 UTF-8 编码
5. **YAML 格式**：注意缩进和格式正确性

## 🎯 示例配置

本目录已提供两个示例：
- 语文教研员（chinese_teacher）
- 数学教研员（math_teacher）

您可以参考这些示例，创建更多学科的教研员工具。
