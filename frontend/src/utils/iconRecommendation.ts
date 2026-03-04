/**
 * 图标自动推荐工具
 * 根据名称和描述中的关键词推荐合适的图标
 */

interface KeywordMapping {
  keywords: string[]
  icon: string
}

// 关键词映射表（优先级从上到下，具体关键词放前面）
const keywordMappings: KeywordMapping[] = [
  // 文档和文本
  {
    keywords: ['新闻', '报纸', '资讯', 'news', 'newspaper', 'article'],
    icon: 'newspaper',
  },
  {
    keywords: ['文档', 'markdown', 'md', '编辑', '文本', 'document', 'text', 'edit'],
    icon: 'document-text',
  },
  {
    keywords: ['文件夹', '目录', '分类', 'folder', 'directory', 'category'],
    icon: 'folder',
  },
  {
    keywords: ['书签', '收藏', 'bookmark', 'favorite'],
    icon: 'bookmark',
  },
  {
    keywords: ['剪贴板', '复制', 'clipboard', 'copy'],
    icon: 'clipboard-document',
  },
  
  // 代码和开发
  {
    keywords: ['代码编辑', '代码', '编程', '脚本', 'code', 'programming', 'script', 'developer'],
    icon: 'code-bracket',
  },
  {
    keywords: ['命令行', '终端', 'terminal', 'command', 'cli'],
    icon: 'command-line',
  },
  {
    keywords: ['数据库', '数据', 'database', 'data', 'sql'],
    icon: 'circle-stack',
  },
  {
    keywords: ['芯片', '处理器', 'ai', '智能', 'chip', 'processor', 'artificial'],
    icon: 'cpu-chip',
  },
  {
    keywords: ['服务器', '后端', 'server', 'backend'],
    icon: 'server',
  },
  
  // 媒体
  {
    keywords: ['图片编辑', '图片', '照片', '相册', '图像', 'photo', 'image', 'picture', 'gallery'],
    icon: 'photo',
  },
  {
    keywords: ['视频播放', '视频编辑', '视频', '录制', '影片', 'video', 'play', 'record', 'movie'],
    icon: 'video-camera',
  },
  {
    keywords: ['电影', '影院', 'film', 'cinema'],
    icon: 'film',
  },
  {
    keywords: ['音乐', '音频', '声音', 'music', 'audio', 'sound'],
    icon: 'musical-note',
  },
  {
    keywords: ['扬声器', '播放', '音响', 'speaker', 'play', 'audio'],
    icon: 'speaker-wave',
  },
  {
    keywords: ['麦克风', '录音', '语音', 'microphone', 'record', 'voice'],
    icon: 'microphone',
  },
  {
    keywords: ['相机', '拍照', 'camera', 'photo'],
    icon: 'camera',
  },
  
  // 图表和数据
  {
    keywords: ['图表', '统计', '柱状图', 'chart', 'statistics', 'bar', 'graph'],
    icon: 'chart-bar',
  },
  {
    keywords: ['饼图', '圆图', 'pie', 'circle'],
    icon: 'chart-pie',
  },
  {
    keywords: ['演示', '报告', 'presentation', 'report'],
    icon: 'presentation-chart-bar',
  },
  {
    keywords: ['表格', 'excel', 'csv', 'table', 'spreadsheet'],
    icon: 'table-cells',
  },
  {
    keywords: ['公式', '计算', '数学', 'calculator', 'math', 'formula'],
    icon: 'calculator',
  },
  
  // UI和设计
  {
    keywords: ['绘画', '画笔', '涂鸦', 'paint', 'brush', 'draw', 'art'],
    icon: 'paint-brush',
  },
  {
    keywords: ['色板', '颜色', '调色板', 'color', 'palette', 'swatch'],
    icon: 'swatch',
  },
  {
    keywords: ['查看', '预览', '眼睛', 'view', 'preview', 'eye'],
    icon: 'eye',
  },
  {
    keywords: ['取色', '颜色选择', 'color-picker', 'dropper'],
    icon: 'eye-dropper',
  },
  {
    keywords: ['光标', '指针', '点击', 'cursor', 'pointer', 'click'],
    icon: 'cursor-arrow-rays',
  },
  
  // 通信
  {
    keywords: ['聊天', '对话', '交流', 'chat', 'conversation', 'message'],
    icon: 'chat-bubble-left-right',
  },
  {
    keywords: ['邮件', '邮箱', 'email', 'mail', 'envelope'],
    icon: 'envelope',
  },
  {
    keywords: ['电话', '通话', '联系', 'phone', 'call', 'contact'],
    icon: 'phone',
  },
  {
    keywords: ['通知', '提醒', '消息', 'notification', 'alert', 'bell'],
    icon: 'bell',
  },
  {
    keywords: ['广播', '公告', '喇叭', 'broadcast', 'announcement', 'megaphone'],
    icon: 'megaphone',
  },
  
  // 用户和人员
  {
    keywords: ['个人', '账户', 'personal', 'account', 'profile'],
    icon: 'user',
  },
  {
    keywords: ['用户', '分组', '点名', '成员', 'user', 'group', 'member', 'team'],
    icon: 'user-group',
  },
  {
    keywords: ['头像', '用户圆形', 'avatar', 'profile-circle'],
    icon: 'user-circle',
  },
  {
    keywords: ['多人', '团队', '组织', 'users', 'team', 'organization'],
    icon: 'users',
  },
  
  // 商务和金融
  {
    keywords: ['钞票', '金钱', '费用', 'money', 'cash', 'payment'],
    icon: 'banknotes',
  },
  {
    keywords: ['信用卡', '银行卡', '支付', 'credit-card', 'payment', 'card'],
    icon: 'credit-card',
  },
  {
    keywords: ['购物车', '购物', '商城', 'shopping', 'cart', 'store'],
    icon: 'shopping-cart',
  },
  {
    keywords: ['办公楼', '公司', '企业', 'office', 'company', 'building'],
    icon: 'building-office',
  },
  {
    keywords: ['公文包', '商务', '工作', 'briefcase', 'business', 'work'],
    icon: 'briefcase',
  },
  
  // 时间和日期
  {
    keywords: ['时间', '倒计时', '计时', '定时', 'clock', 'time', 'timer', 'countdown'],
    icon: 'clock',
  },
  {
    keywords: ['日历', '日期', 'calendar', 'date'],
    icon: 'calendar',
  },
  {
    keywords: ['日程', '行程', '计划', 'schedule', 'plan', 'agenda'],
    icon: 'calendar-days',
  },
  
  // 位置和地图
  {
    keywords: ['地图', '位置', '导航', 'map', 'location', 'navigation'],
    icon: 'map',
  },
  {
    keywords: ['定位', '标记', '地标', 'pin', 'marker', 'location'],
    icon: 'map-pin',
  },
  {
    keywords: ['全球', '世界', '国际', 'global', 'world', 'international'],
    icon: 'globe-alt',
  },
  {
    keywords: ['商店', '店铺', '门店', 'store', 'shop', 'retail'],
    icon: 'building-storefront',
  },
  {
    keywords: ['家', '首页', 'home', 'homepage'],
    icon: 'home',
  },
  
  // 学习和教育
  {
    keywords: ['教育', '学习', '课程', '培训', 'education', 'learn', 'course', 'training'],
    icon: 'academic-cap',
  },
  {
    keywords: ['实验室', '实验', '试验', 'experiment', 'lab'],
    icon: 'beaker',
  },
  {
    keywords: ['灯泡', '想法', '创新', 'bulb', 'idea', 'innovation'],
    icon: 'light-bulb',
  },
  {
    keywords: ['拼图', '组件', '插件', 'puzzle', 'component', 'plugin'],
    icon: 'puzzle-piece',
  },
  {
    keywords: ['书籍', '阅读', '文库', '书本', 'book', 'read', 'library'],
    icon: 'book-open',
  },
  
  // 工具和设置
  {
    keywords: ['工具', '修理', 'tool', 'repair'],
    icon: 'wrench',
  },
  {
    keywords: ['设置', '配置', '齿轮', 'setting', 'config', 'gear'],
    icon: 'cog-6-tooth',
  },
  {
    keywords: ['维修', '工具箱', 'maintenance', 'toolbox'],
    icon: 'wrench-screwdriver',
  },
  {
    keywords: ['调整', '滑块', '参数', 'adjust', 'slider', 'parameter'],
    icon: 'adjustments-horizontal',
  },
  
  // 安全
  {
    keywords: ['安全', '防护', '保护', 'security', 'protection', 'safe'],
    icon: 'shield-check',
  },
  {
    keywords: ['锁', '加锁', 'lock', 'secure'],
    icon: 'lock-closed',
  },
  {
    keywords: ['密钥', '密码', '钥匙', 'key', 'password', 'secret'],
    icon: 'key',
  },
  {
    keywords: ['指纹', '生物识别', 'fingerprint', 'biometric'],
    icon: 'finger-print',
  },
  
  // 动作
  {
    keywords: ['编辑', '修改', '笔', 'edit', 'modify', 'pencil'],
    icon: 'pencil-square',
  },
  {
    keywords: ['删除', '垃圾桶', 'delete', 'trash', 'remove'],
    icon: 'trash',
  },
  {
    keywords: ['添加', '新增', '加号', 'add', 'new', 'plus'],
    icon: 'plus',
  },
  {
    keywords: ['减少', '移除', 'minus', 'subtract'],
    icon: 'minus',
  },
  {
    keywords: ['关闭', '取消', 'close', 'cancel'],
    icon: 'x-mark',
  },
  {
    keywords: ['完成', '确认', '勾选', 'done', 'confirm', 'check'],
    icon: 'check',
  },
  
  // 其他常用
  {
    keywords: ['星星', '收藏', '评分', 'star', 'favorite', 'rating'],
    icon: 'star',
  },
  {
    keywords: ['爱心', '喜欢', 'heart', 'like', 'love'],
    icon: 'heart',
  },
  {
    keywords: ['火', '热门', '趋势', 'fire', 'hot', 'trending'],
    icon: 'fire',
  },
  {
    keywords: ['闪电', '快速', '性能', 'bolt', 'fast', 'performance'],
    icon: 'bolt',
  },
  {
    keywords: ['创意', '灵感', '设计', '魔法', 'creative', 'inspiration', 'design', 'magic'],
    icon: 'sparkles',
  },
  {
    keywords: ['礼物', '奖励', 'gift', 'reward', 'present'],
    icon: 'gift',
  },
  {
    keywords: ['奖杯', '胜利', '成就', 'trophy', 'achievement', 'win'],
    icon: 'trophy',
  },
  {
    keywords: ['火箭', '启动', '发射', 'rocket', 'launch', 'start'],
    icon: 'rocket-launch',
  },
  {
    keywords: ['云', '云端', '存储', 'cloud', 'storage'],
    icon: 'cloud',
  },
  {
    keywords: ['太阳', '白天', '亮度', 'sun', 'day', 'brightness'],
    icon: 'sun',
  },
  {
    keywords: ['月亮', '夜晚', '暗色', 'moon', 'night', 'dark'],
    icon: 'moon',
  },
  {
    keywords: ['二维码', '扫码', 'qr', 'qrcode', 'scan'],
    icon: 'qrcode',
  },
  {
    keywords: ['链接', '超链接', 'link', 'url', 'hyperlink'],
    icon: 'link',
  },
  {
    keywords: ['分享', '共享', 'share', 'social'],
    icon: 'share',
  },
  {
    keywords: ['打印', '打印机', 'print', 'printer'],
    icon: 'printer',
  },
  {
    keywords: ['搜索', '查找', '搜索框', 'search', 'find', 'magnifier'],
    icon: 'magnifying-glass',
  },
  {
    keywords: ['筛选', '过滤', 'filter', 'funnel'],
    icon: 'funnel',
  },
  {
    keywords: ['标签', '标记', 'tag', 'label'],
    icon: 'tag',
  },
  {
    keywords: ['旗帜', '标志', 'flag', 'banner'],
    icon: 'flag',
  },
  {
    keywords: ['收件箱', '邮箱', 'inbox', 'mailbox'],
    icon: 'inbox',
  },
  {
    keywords: ['归档', '存档', 'archive', 'storage'],
    icon: 'archive-box',
  },
  {
    keywords: ['模型', '立方体', 'model', 'cube'],
    icon: 'cube',
  },
  {
    keywords: ['透明', '透视', 'transparent', 'perspective'],
    icon: 'cube-transparent',
  },
  {
    keywords: ['堆叠', '层级', '3d', 'stack', 'layer', '3d'],
    icon: 'square-3-stack-3d',
  },
]

/**
 * 根据名称和描述推荐图标
 * @param name 名称
 * @param description 描述（可选）
 * @param defaultIcon 默认图标（如果没有匹配）
 * @returns 推荐的图标名称
 */
export function recommendIcon(
  name: string,
  description?: string,
  defaultIcon: string = 'wrench'
): string {
  // 合并名称和描述
  const text = `${name} ${description || ''}`.toLowerCase()

  // 遍历关键词映射表，找到第一个匹配的图标
  for (const mapping of keywordMappings) {
    for (const keyword of mapping.keywords) {
      if (text.includes(keyword.toLowerCase())) {
        return mapping.icon
      }
    }
  }

  // 如果没有匹配，返回默认图标
  return defaultIcon
}

/**
 * 为工具推荐图标
 * @param name 工具名称
 * @param description 工具描述
 * @returns 推荐的图标名称
 */
export function recommendToolIcon(name: string, description?: string): string {
  return recommendIcon(name, description, 'wrench')
}

/**
 * 为作品推荐图标
 * @param name 作品名称
 * @param description 作品描述
 * @returns 推荐的图标名称
 */
export function recommendWorkIcon(name: string, description?: string): string {
  return recommendIcon(name, description, 'photo')
}

/**
 * 为分类推荐图标
 * @param name 分类名称
 * @returns 推荐的图标名称
 */
export function recommendCategoryIcon(name: string): string {
  return recommendIcon(name, '', 'puzzle-piece')
}
