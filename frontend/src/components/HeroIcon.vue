<template>
  <component v-if="iconComponent" :is="iconComponent" :class="iconClass" />
  <WrenchIcon v-else :class="iconClass" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  DocumentTextIcon,
  ChartBarIcon,
  CodeBracketIcon,
  TableCellsIcon,
  CalculatorIcon,
  PhotoIcon,
  VideoCameraIcon,
  ClockIcon,
  UserGroupIcon,
  QrCodeIcon,
  WrenchIcon,
  PuzzlePieceIcon,
  BeakerIcon,
  AcademicCapIcon,
  BookOpenIcon,
  SparklesIcon,
  PencilSquareIcon,
  MusicalNoteIcon,
  PaintBrushIcon,
  CubeIcon,
  CpuChipIcon,
  GlobeAltIcon,
  MapIcon,
  CloudIcon,
  ServerIcon,
  ShieldCheckIcon,
  KeyIcon,
  BellIcon,
  ChatBubbleLeftRightIcon,
  EnvelopeIcon,
  PhoneIcon,
} from '@heroicons/vue/24/outline'

interface Props {
  name?: string
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  name: 'wrench',
  class: '',
})

// 图标组件映射表
const iconComponents: Record<string, any> = {
  'document-text': DocumentTextIcon,
  'chart-bar': ChartBarIcon,
  'code-bracket': CodeBracketIcon,
  'table-cells': TableCellsIcon,
  calculator: CalculatorIcon,
  photo: PhotoIcon,
  'video-camera': VideoCameraIcon,
  clock: ClockIcon,
  'user-group': UserGroupIcon,
  qrcode: QrCodeIcon,
  wrench: WrenchIcon,
  'puzzle-piece': PuzzlePieceIcon,
  beaker: BeakerIcon,
  'academic-cap': AcademicCapIcon,
  'book-open': BookOpenIcon,
  sparkles: SparklesIcon,
  'pencil-square': PencilSquareIcon,
  'musical-note': MusicalNoteIcon,
  'paint-brush': PaintBrushIcon,
  cube: CubeIcon,
  'cpu-chip': CpuChipIcon,
  'globe-alt': GlobeAltIcon,
  map: MapIcon,
  cloud: CloudIcon,
  server: ServerIcon,
  'shield-check': ShieldCheckIcon,
  key: KeyIcon,
  bell: BellIcon,
  'chat-bubble-left-right': ChatBubbleLeftRightIcon,
  envelope: EnvelopeIcon,
  phone: PhoneIcon,
}

/**
 * 获取图标组件
 */
const iconComponent = computed(() => {
  if (!props.name) {
    return WrenchIcon
  }
  return iconComponents[props.name] || WrenchIcon
})

/**
 * 图标类名
 */
const iconClass = computed(() => props.class || 'w-6 h-6')
</script>
