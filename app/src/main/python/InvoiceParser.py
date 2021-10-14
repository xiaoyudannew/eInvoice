import json
import PDFInvoiceParse

def invoice_parse(pdfs):
    inv_list = []
    for pdf in pdfs:
        print('正在解析：' + pdf)
        if pdf[-3:].lower() == 'pdf':
            inv_list.append(PDFInvoiceParse.get_dtl_from_pdf(pdf))

    return json.dumps(inv_list)
