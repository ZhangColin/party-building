declare module 'html2pdf.js' {
  interface Html2PdfOptions {
    margin?: number | [number, number, number, number];
    filename?: string;
    image?: { type: string; quality: number };
    html2canvas?: { scale: number; useCORS?: boolean; letterRendering?: boolean };
    jsPDF?: { unit: string; format: string; orientation: 'portrait' | 'landscape' };
    pagebreak?: { mode: string };
  }

  interface Html2Pdf {
    set(opt: Html2PdfOptions): Html2Pdf;
    from(element: HTMLElement): Html2Pdf;
    save(): Promise<void>;
  }

  const html2pdf: (opt?: Html2PdfOptions) => Html2Pdf;

  export default html2pdf;
}
