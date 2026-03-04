import { describe, it, expect, vi, beforeEach } from 'vitest'
import { downloadWord } from '@/utils/documentDownloader'
import downloadPdf from '@/utils/html2pdfDownloader'

describe('downloadWord', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.restoreAllMocks()
  })

  it('should download Word document successfully', async () => {
    const mockBlob = new Blob(['test'], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    })
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => mockBlob
    } as Response))

    // Mock URL.createObjectURL and revokeObjectURL
    const mockUrl = 'blob:test-url'
    vi.spyOn(URL, 'createObjectURL').mockReturnValue(mockUrl)
    vi.spyOn(URL, 'revokeObjectURL')

    // Mock createElement to return a proper anchor element
    const mockAnchor = {
      href: '',
      download: '',
      click: vi.fn(),
      style: {}
    }
    const createElementSpy = vi.spyOn(document, 'createElement').mockReturnValue(mockAnchor as any)

    // Mock body.appendChild
    vi.spyOn(document.body, 'appendChild').mockReturnValue(mockAnchor as any)

    await downloadWord('# Test\n\nThis is a test.', 'test-document.docx')

    expect(fetch).toHaveBeenCalledWith('/api/v1/convert/markdown-to-word', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: '# Test\n\nThis is a test.' })
    })
    expect(createElementSpy).toHaveBeenCalledWith('a')
    expect(mockAnchor.href).toBe(mockUrl)
    expect(mockAnchor.download).toBe('test-document.docx')
    expect(mockAnchor.click).toHaveBeenCalled()
    expect(URL.revokeObjectURL).toHaveBeenCalledWith(mockUrl)
  })

  it('should handle API errors', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      statusText: 'Internal Server Error'
    } as Response))

    await expect(downloadWord('# Test')).rejects.toThrow('转换失败: Internal Server Error')
  })

  it('should handle network errors', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network error')))

    await expect(downloadWord('# Test')).rejects.toThrow('Network error')
  })

  it('should clean up Blob URL after download', async () => {
    const mockBlob = new Blob(['test'], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    })
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => mockBlob
    } as Response))

    // Mock URL.createObjectURL and revokeObjectURL
    const mockUrl = 'blob:test-url'
    vi.spyOn(URL, 'createObjectURL').mockReturnValue(mockUrl)
    const revokeObjectURLSpy = vi.spyOn(URL, 'revokeObjectURL')

    // Mock createElement to return a proper anchor element
    const mockAnchor = {
      href: '',
      download: '',
      click: vi.fn(),
      style: {}
    }
    vi.spyOn(document, 'createElement').mockReturnValue(mockAnchor as any)
    vi.spyOn(document.body, 'appendChild').mockReturnValue(mockAnchor as any)

    await downloadWord('# Test')

    expect(revokeObjectURLSpy).toHaveBeenCalledWith(mockUrl)
  })

  it('should use default filename if not provided', async () => {
    const mockBlob = new Blob(['test'], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    })
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => mockBlob
    } as Response))

    const mockUrl = 'blob:test-url'
    vi.spyOn(URL, 'createObjectURL').mockReturnValue(mockUrl)
    vi.spyOn(URL, 'revokeObjectURL')

    const mockAnchor = {
      href: '',
      download: '',
      click: vi.fn(),
      style: {}
    }
    vi.spyOn(document, 'createElement').mockReturnValue(mockAnchor as any)
    vi.spyOn(document.body, 'appendChild').mockReturnValue(mockAnchor as any)

    await downloadWord('# Test')

    expect(mockAnchor.download).toBe('document.docx')
  })

  it('should use custom filename if provided', async () => {
    const mockBlob = new Blob(['test'], {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    })
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => mockBlob
    } as Response))

    const mockUrl = 'blob:test-url'
    vi.spyOn(URL, 'createObjectURL').mockReturnValue(mockUrl)
    vi.spyOn(URL, 'revokeObjectURL')

    const mockAnchor = {
      href: '',
      download: '',
      click: vi.fn(),
      style: {}
    }
    vi.spyOn(document, 'createElement').mockReturnValue(mockAnchor as any)
    vi.spyOn(document.body, 'appendChild').mockReturnValue(mockAnchor as any)

    await downloadWord('# Test', 'custom-name.docx')

    expect(mockAnchor.download).toBe('custom-name.docx')
  })
})

describe('downloadPdf', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('should download PDF document successfully', async () => {
    // Create a mock element in the DOM
    const mockElement = document.createElement('div')
    mockElement.id = 'pdf-content'
    mockElement.innerHTML = '<h1>Test PDF Content</h1>'
    document.body.appendChild(mockElement)

    // Mock html2pdf.js
    const mockSave = vi.fn().mockResolvedValue(undefined)
    const mockFrom = vi.fn().mockReturnValue({ save: mockSave })
    const mockSet = vi.fn().mockReturnValue({ from: mockFrom })
    vi.doMock('html2pdf.js', () => {
      return {
        default: () => ({
          set: mockSet,
          from: mockFrom
        })
      }
    })

    // Import after mocking
    const downloadPdfModule = await import('@/utils/html2pdfDownloader')
    await downloadPdfModule.default('pdf-content', 'test-document.pdf')

    // Verify the PDF was generated with correct options
    expect(mockSet).toHaveBeenCalledWith({
      margin: 10,
      filename: 'test-document.pdf',
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: {
        scale: 2,
        useCORS: true,
        logging: true
      },
      jsPDF: {
        unit: 'mm',
        format: 'a4',
        orientation: 'portrait'
      }
    })
    expect(mockFrom).toHaveBeenCalledWith(mockElement)
    expect(mockSave).toHaveBeenCalled()

    // Clean up
    document.body.removeChild(mockElement)
  })

  it('should throw error if element is not found', async () => {
    await expect(downloadPdf('non-existent-element')).rejects.toThrow(
      '找不到要转换的元素: non-existent-element'
    )
  })

  it('should use default filename if not provided', async () => {
    const mockElement = document.createElement('div')
    mockElement.id = 'pdf-content-default'
    mockElement.innerHTML = '<h1>Test</h1>'
    document.body.appendChild(mockElement)

    const mockSave = vi.fn().mockResolvedValue(undefined)
    const mockFrom = vi.fn().mockReturnValue({ save: mockSave })
    const mockSet = vi.fn().mockReturnValue({ from: mockFrom })
    vi.doMock('html2pdf.js', () => {
      return {
        default: () => ({
          set: mockSet,
          from: mockFrom
        })
      }
    })

    const downloadPdfModule = await import('@/utils/html2pdfDownloader')
    await downloadPdfModule.default('pdf-content-default')

    expect(mockSet).toHaveBeenCalledWith(
      expect.objectContaining({
        filename: 'document.pdf'
      })
    )

    document.body.removeChild(mockElement)
  })

  it('should handle html2pdf errors', async () => {
    const mockElement = document.createElement('div')
    mockElement.id = 'pdf-content-error'
    mockElement.innerHTML = '<h1>Test</h1>'
    document.body.appendChild(mockElement)

    const mockError = new Error('PDF generation failed')
    const mockSave = vi.fn().mockRejectedValue(mockError)
    const mockFrom = vi.fn().mockReturnValue({ save: mockSave })
    const mockSet = vi.fn().mockReturnValue({ from: mockFrom })
    vi.doMock('html2pdf.js', () => {
      return {
        default: () => ({
          set: mockSet,
          from: mockFrom
        })
      }
    })

    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    const downloadPdfModule = await import('@/utils/html2pdfDownloader')
    await expect(downloadPdfModule.default('pdf-content-error')).rejects.toThrow('PDF generation failed')

    expect(consoleErrorSpy).toHaveBeenCalledWith('[PDF Download] PDF 下载失败:', mockError)

    consoleErrorSpy.mockRestore()
    document.body.removeChild(mockElement)
  })

  it('should configure high quality options', async () => {
    const mockElement = document.createElement('div')
    mockElement.id = 'pdf-content-quality'
    mockElement.innerHTML = '<h1>High Quality Test</h1>'
    document.body.appendChild(mockElement)

    const mockSave = vi.fn().mockResolvedValue(undefined)
    const mockFrom = vi.fn().mockReturnValue({ save: mockSave })
    const mockSet = vi.fn().mockReturnValue({ from: mockFrom })
    vi.doMock('html2pdf.js', () => {
      return {
        default: () => ({
          set: mockSet,
          from: mockFrom
        })
      }
    })

    const downloadPdfModule = await import('@/utils/html2pdfDownloader')
    await downloadPdfModule.default('pdf-content-quality')

    // Verify high quality settings
    expect(mockSet).toHaveBeenCalledWith({
      margin: 10,
      filename: 'document.pdf',
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: {
        scale: 2,
        useCORS: true,
        logging: true
      },
      jsPDF: {
        unit: 'mm',
        format: 'a4',
        orientation: 'portrait'
      }
    })

    document.body.removeChild(mockElement)
  })
})

