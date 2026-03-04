<template>
  <div class="icon-selector">
    <!-- 当前选中的图标 -->
    <div class="selected-icon" @click="showDialog = true">
      <component
        v-if="modelValue"
        :is="getIconComponent(modelValue)"
        class="icon-preview"
      />
      <span v-else class="placeholder">选择图标</span>
    </div>

    <!-- 图标选择对话框 -->
    <el-dialog
      v-model="showDialog"
      title="选择图标"
      width="700px"
      :close-on-click-modal="false"
    >
      <!-- 搜索框 -->
      <el-input
        v-model="searchKeyword"
        placeholder="搜索图标名称..."
        clearable
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <!-- 图标网格 -->
      <div class="icon-grid">
        <div
          v-for="icon in filteredIcons"
          :key="icon.name"
          class="icon-item"
          :class="{ active: selectedIcon === icon.name }"
          @click="selectIcon(icon.name)"
        >
          <component :is="icon.component" class="icon" />
          <span class="icon-name">{{ icon.name }}</span>
        </div>
      </div>

      <!-- 无结果提示 -->
      <el-empty
        v-if="filteredIcons.length === 0"
        description="没有找到匹配的图标"
      />

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button @click="clearIcon">清空</el-button>
        <el-button type="primary" @click="confirmSelection">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import {
  // 文档和文本
  DocumentTextIcon,
  DocumentIcon,
  FolderIcon,
  FolderOpenIcon,
  NewspaperIcon,
  BookOpenIcon,
  BookmarkIcon,
  ClipboardDocumentIcon,
  
  // 图表和数据
  ChartBarIcon,
  ChartPieIcon,
  PresentationChartBarIcon,
  TableCellsIcon,
  CalculatorIcon,
  
  // 代码和开发
  CodeBracketIcon,
  CommandLineIcon,
  CpuChipIcon,
  ServerIcon,
  CircleStackIcon,
  
  // 媒体
  PhotoIcon,
  VideoCameraIcon,
  FilmIcon,
  MusicalNoteIcon,
  SpeakerWaveIcon,
  MicrophoneIcon,
  CameraIcon,
  
  // UI和设计
  PaintBrushIcon,
  SwatchIcon,
  EyeIcon,
  EyeDropperIcon,
  CursorArrowRaysIcon,
  
  // 通信
  ChatBubbleLeftRightIcon,
  EnvelopeIcon,
  PhoneIcon,
  BellIcon,
  MegaphoneIcon,
  
  // 用户和人员
  UserIcon,
  UserGroupIcon,
  UserCircleIcon,
  UsersIcon,
  
  // 商务和金融
  BanknotesIcon,
  CreditCardIcon,
  ShoppingCartIcon,
  BuildingOfficeIcon,
  BriefcaseIcon,
  
  // 时间和日期
  ClockIcon,
  CalendarIcon,
  CalendarDaysIcon,
  
  // 位置和地图
  MapIcon,
  MapPinIcon,
  GlobeAltIcon,
  BuildingStorefrontIcon,
  HomeIcon,
  
  // 学习和教育
  AcademicCapIcon,
  BeakerIcon,
  LightBulbIcon,
  PuzzlePieceIcon,
  
  // 工具和设置
  WrenchIcon,
  Cog6ToothIcon,
  WrenchScrewdriverIcon,
  AdjustmentsHorizontalIcon,
  
  // 安全
  ShieldCheckIcon,
  LockClosedIcon,
  KeyIcon,
  FingerPrintIcon,
  
  // 导航和箭头
  ArrowRightIcon,
  ArrowLeftIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ChevronRightIcon,
  
  // 动作
  PencilSquareIcon,
  TrashIcon,
  PlusIcon,
  MinusIcon,
  XMarkIcon,
  CheckIcon,
  
  // 其他常用
  StarIcon,
  HeartIcon,
  FireIcon,
  BoltIcon,
  SparklesIcon,
  GiftIcon,
  TrophyIcon,
  RocketLaunchIcon,
  CloudIcon,
  SunIcon,
  MoonIcon,
  QrCodeIcon,
  LinkIcon,
  ShareIcon,
  PrinterIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  TagIcon,
  FlagIcon,
  InboxIcon,
  ArchiveBoxIcon,
  CubeIcon,
  CubeTransparentIcon,
  Square3Stack3DIcon,
} from '@heroicons/vue/24/outline'

interface IconOption {
  name: string
  component: any
}

const props = defineProps<{
  modelValue?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | undefined): void
}>()

const showDialog = ref(false)
const searchKeyword = ref('')
const selectedIcon = ref<string | undefined>(props.modelValue)

// 可用图标列表（按分类组织，便于用户查找）
const availableIcons: IconOption[] = [
  // 文档和文本
  { name: 'document-text', component: DocumentTextIcon },
  { name: 'document', component: DocumentIcon },
  { name: 'folder', component: FolderIcon },
  { name: 'folder-open', component: FolderOpenIcon },
  { name: 'newspaper', component: NewspaperIcon },
  { name: 'book-open', component: BookOpenIcon },
  { name: 'bookmark', component: BookmarkIcon },
  { name: 'clipboard-document', component: ClipboardDocumentIcon },
  
  // 图表和数据
  { name: 'chart-bar', component: ChartBarIcon },
  { name: 'chart-pie', component: ChartPieIcon },
  { name: 'presentation-chart-bar', component: PresentationChartBarIcon },
  { name: 'table-cells', component: TableCellsIcon },
  { name: 'calculator', component: CalculatorIcon },
  
  // 代码和开发
  { name: 'code-bracket', component: CodeBracketIcon },
  { name: 'command-line', component: CommandLineIcon },
  { name: 'cpu-chip', component: CpuChipIcon },
  { name: 'server', component: ServerIcon },
  { name: 'circle-stack', component: CircleStackIcon },
  
  // 媒体
  { name: 'photo', component: PhotoIcon },
  { name: 'video-camera', component: VideoCameraIcon },
  { name: 'film', component: FilmIcon },
  { name: 'musical-note', component: MusicalNoteIcon },
  { name: 'speaker-wave', component: SpeakerWaveIcon },
  { name: 'microphone', component: MicrophoneIcon },
  { name: 'camera', component: CameraIcon },
  
  // UI和设计
  { name: 'paint-brush', component: PaintBrushIcon },
  { name: 'swatch', component: SwatchIcon },
  { name: 'eye', component: EyeIcon },
  { name: 'eye-dropper', component: EyeDropperIcon },
  { name: 'cursor-arrow-rays', component: CursorArrowRaysIcon },
  
  // 通信
  { name: 'chat-bubble-left-right', component: ChatBubbleLeftRightIcon },
  { name: 'envelope', component: EnvelopeIcon },
  { name: 'phone', component: PhoneIcon },
  { name: 'bell', component: BellIcon },
  { name: 'megaphone', component: MegaphoneIcon },
  
  // 用户和人员
  { name: 'user', component: UserIcon },
  { name: 'user-group', component: UserGroupIcon },
  { name: 'user-circle', component: UserCircleIcon },
  { name: 'users', component: UsersIcon },
  
  // 商务和金融
  { name: 'banknotes', component: BanknotesIcon },
  { name: 'credit-card', component: CreditCardIcon },
  { name: 'shopping-cart', component: ShoppingCartIcon },
  { name: 'building-office', component: BuildingOfficeIcon },
  { name: 'briefcase', component: BriefcaseIcon },
  
  // 时间和日期
  { name: 'clock', component: ClockIcon },
  { name: 'calendar', component: CalendarIcon },
  { name: 'calendar-days', component: CalendarDaysIcon },
  
  // 位置和地图
  { name: 'map', component: MapIcon },
  { name: 'map-pin', component: MapPinIcon },
  { name: 'globe-alt', component: GlobeAltIcon },
  { name: 'building-storefront', component: BuildingStorefrontIcon },
  { name: 'home', component: HomeIcon },
  
  // 学习和教育
  { name: 'academic-cap', component: AcademicCapIcon },
  { name: 'beaker', component: BeakerIcon },
  { name: 'light-bulb', component: LightBulbIcon },
  { name: 'puzzle-piece', component: PuzzlePieceIcon },
  
  // 工具和设置
  { name: 'wrench', component: WrenchIcon },
  { name: 'cog-6-tooth', component: Cog6ToothIcon },
  { name: 'wrench-screwdriver', component: WrenchScrewdriverIcon },
  { name: 'adjustments-horizontal', component: AdjustmentsHorizontalIcon },
  
  // 安全
  { name: 'shield-check', component: ShieldCheckIcon },
  { name: 'lock-closed', component: LockClosedIcon },
  { name: 'key', component: KeyIcon },
  { name: 'finger-print', component: FingerPrintIcon },
  
  // 导航和箭头
  { name: 'arrow-right', component: ArrowRightIcon },
  { name: 'arrow-left', component: ArrowLeftIcon },
  { name: 'arrow-up', component: ArrowUpIcon },
  { name: 'arrow-down', component: ArrowDownIcon },
  { name: 'chevron-right', component: ChevronRightIcon },
  
  // 动作
  { name: 'pencil-square', component: PencilSquareIcon },
  { name: 'trash', component: TrashIcon },
  { name: 'plus', component: PlusIcon },
  { name: 'minus', component: MinusIcon },
  { name: 'x-mark', component: XMarkIcon },
  { name: 'check', component: CheckIcon },
  
  // 其他常用
  { name: 'star', component: StarIcon },
  { name: 'heart', component: HeartIcon },
  { name: 'fire', component: FireIcon },
  { name: 'bolt', component: BoltIcon },
  { name: 'sparkles', component: SparklesIcon },
  { name: 'gift', component: GiftIcon },
  { name: 'trophy', component: TrophyIcon },
  { name: 'rocket-launch', component: RocketLaunchIcon },
  { name: 'cloud', component: CloudIcon },
  { name: 'sun', component: SunIcon },
  { name: 'moon', component: MoonIcon },
  { name: 'qrcode', component: QrCodeIcon },
  { name: 'link', component: LinkIcon },
  { name: 'share', component: ShareIcon },
  { name: 'printer', component: PrinterIcon },
  { name: 'magnifying-glass', component: MagnifyingGlassIcon },
  { name: 'funnel', component: FunnelIcon },
  { name: 'tag', component: TagIcon },
  { name: 'flag', component: FlagIcon },
  { name: 'inbox', component: InboxIcon },
  { name: 'archive-box', component: ArchiveBoxIcon },
  { name: 'cube', component: CubeIcon },
  { name: 'cube-transparent', component: CubeTransparentIcon },
  { name: 'square-3-stack-3d', component: Square3Stack3DIcon },
]

/**
 * 过滤后的图标列表
 */
const filteredIcons = computed(() => {
  if (!searchKeyword.value) {
    return availableIcons
  }

  const keyword = searchKeyword.value.toLowerCase()
  return availableIcons.filter((icon) =>
    icon.name.toLowerCase().includes(keyword)
  )
})

/**
 * 根据图标名称获取图标组件
 */
const getIconComponent = (iconName: string) => {
  const icon = availableIcons.find((i) => i.name === iconName)
  return icon?.component
}

/**
 * 选择图标
 */
const selectIcon = (iconName: string) => {
  selectedIcon.value = iconName
}

/**
 * 清空图标
 */
const clearIcon = () => {
  selectedIcon.value = undefined
  emit('update:modelValue', undefined)
  showDialog.value = false
}

/**
 * 确认选择
 */
const confirmSelection = () => {
  emit('update:modelValue', selectedIcon.value)
  showDialog.value = false
}

/**
 * 监听props变化
 */
watch(
  () => props.modelValue,
  (newValue) => {
    selectedIcon.value = newValue
  }
)
</script>

<style scoped>
.icon-selector {
  display: inline-block;
}

.selected-icon {
  width: 80px;
  height: 80px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.selected-icon:hover {
  border-color: #1890ff;
}

.icon-preview {
  width: 48px;
  height: 48px;
  color: #1890ff;
}

.placeholder {
  color: #999;
  font-size: 14px;
}

.search-input {
  margin-bottom: 16px;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px;
  border: 2px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.icon-item:hover {
  border-color: #1890ff;
  background-color: #f0f7ff;
}

.icon-item.active {
  border-color: #1890ff;
  background-color: #e6f4ff;
}

.icon-item .icon {
  width: 32px;
  height: 32px;
  color: #666;
  margin-bottom: 8px;
}

.icon-item.active .icon {
  color: #1890ff;
}

.icon-name {
  font-size: 12px;
  color: #999;
  text-align: center;
  word-break: break-all;
}

.icon-item.active .icon-name {
  color: #1890ff;
  font-weight: 500;
}
</style>
