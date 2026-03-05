/** @type {import('tailwindcss').Config} */
import typography from '@tailwindcss/typography'; 

export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // 颜色系统（待从官网提取品牌色后更新）
      colors: {
        // 品牌主色（待从官网提取后更新，当前使用通用蓝色系）
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6', // 主色
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        // 中性色系统
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        },
        // 语义色系统
        success: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981', // 成功色
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b', // 警告色
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444', // 错误色
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
        info: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6', // 信息色（与主色相同）
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        // 党建色彩系统
        party: {
          red: {
            DEFAULT: '#C8102E',  // 中国红
            light: '#E84D56',    // 浅红
            dark: '#8B0000',     // 深红
            50: '#FEF2F2',
            100: '#FEE2E2',
            200: '#FECACA',
            300: '#FCA5A5',
            400: '#F87171',
            500: '#C8102E',
            600: '#A80D27',
            700: '#8B0000',
            800: '#6B0000',
            900: '#4B0000',
          },
          gold: {
            DEFAULT: '#FFD700',  // 五星金
            light: '#FFE55C',    // 浅金
            dark: '#CCB800',     // 深金
            50: '#FFFEF5',
            100: '#FFFECC',
            200: '#FFFDA6',
            300: '#FFF966',
            400: '#FFEF00',
            500: '#FFD700',
            600: '#CCB800',
            700: '#A69400',
            800: '#807000',
            900: '#594C00',
          },
          deepRed: '#8B0000',  // 党建深红
        },
      },
      // 阴影系统
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'md': '0 2px 4px 0 rgba(0, 0, 0, 0.1)',
        'lg': '0 4px 8px 0 rgba(0, 0, 0, 0.1)',
        'xl': '0 8px 16px 0 rgba(0, 0, 0, 0.1)',
        'focus': '0 0 0 3px rgba(59, 130, 246, 0.1)',
        'focus-primary': '0 0 0 3px rgba(59, 130, 246, 0.1)',
        'focus-success': '0 0 0 3px rgba(16, 185, 129, 0.1)',
        'focus-warning': '0 0 0 3px rgba(245, 158, 11, 0.1)',
        'focus-error': '0 0 0 3px rgba(239, 68, 68, 0.1)',
      },
      // 圆角系统
      borderRadius: {
        'xs': '4px',
        'sm': '6px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
      },
      // 间距系统（基于4px）
      spacing: {
        '18': '4.5rem', // 72px
        '22': '5.5rem', // 88px
      },
    },
  },
  plugins: [
    typography(),
  ],
}