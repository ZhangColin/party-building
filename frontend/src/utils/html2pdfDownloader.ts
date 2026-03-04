/**
 * Downloads a PDF document by converting an HTML element using html2pdf.js
 *
 * @param elementId - The ID of the HTML element to convert to PDF
 * @param filename - The filename for the downloaded PDF (default: 'document.pdf')
 * @throws Error if the element is not found or conversion fails
 */
export default async function downloadPdf(
  elementId: string,
  filename = 'document.pdf'
): Promise<void> {
  try {
    console.log('[PDF Download] 开始 PDF 下载流程')

    const element = document.getElementById(elementId)
    if (!element) {
      console.error(`[PDF Download] 找不到要转换的元素: ${elementId}`)
      throw new Error(`找不到要转换的元素: ${elementId}`)
    }

    console.log('[PDF Download] 找到元素，开始生成 PDF')

    // Configure html2pdf options for high-quality output
    const opt = {
      margin: 10, // margin in mm
      filename,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: {
        scale: 2, // Higher scale for better quality
        useCORS: true, // Enable CORS for images
        logging: true // Enable logging to help debug
      },
      jsPDF: {
        unit: 'mm',
        format: 'a4',
        orientation: 'portrait' as const
      }
    }

    // Generate and save PDF
    const html2pdf = (await import('html2pdf.js')).default()
    console.log('[PDF Download] html2pdf.js 已加载')

    await html2pdf.set(opt).from(element).save()
    console.log('[PDF Download] PDF 生成成功')
  } catch (error) {
    console.error('[PDF Download] PDF 下载失败:', error)
    throw error
  }
}
