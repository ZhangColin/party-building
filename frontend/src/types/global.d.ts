/**
 * Global type declarations for AI Teacher Platform
 */

/**
 * Global toast notification function
 * Can be called from anywhere in the application using: window.__showToast(message)
 *
 * @example
 * window.__showToast('File uploaded successfully')
 */
declare global {
  interface Window {
    __showToast?: (message: string) => void
  }
}

export {}
