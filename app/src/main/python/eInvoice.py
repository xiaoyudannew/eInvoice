invoice_col_info = {'fileName':'文件名', 
 'fileType':'文件类型', 
 'headline':'发票标题', 
 'DocID':'文件ID', 
 'InvoiceCode':'发票代码', 
 'InvoiceNo':'发票号码', 
 'TypeCode':'发票类型代码', 
 'IssueDate':'开票日期', 
 'InvoiceCheckCode':'校验码', 
 'MachineNo':'机器编号', 
 'TaxControlCode':'密码区', 
 'BuyerName':'购买方名称', 
 'BuyerTaxID':'购买方纳税人识别号', 
 'BuyerAddrTel':'购买方地址、电话', 
 'BuyerFinancialAccount':'购买方开户行及账号', 
 'Tpvn':'？暂时未知Tpvn', 
 'SellerName':'销售方名称', 
 'SellerTaxID':'销售方纳税人识别号', 
 'SellerAddrTel':'销售方地址、电话', 
 'SellerFinancialAccount':'销售方开户行及账号', 
 'Issuea1':'？暂时未知Issuea1', 
 'Issuea2':'？暂时未知Issuea2', 
 'TaxInclusiveTotalAmount':'价税合计', 
 'Note':'备注', 
 'InvoiceClerk':'开票人', 
 'Payee':'收款人', 
 'Checker':'复核人', 
 'TaxTotalAmount':'税额合计', 
 'TaxExclusiveTotalAmount':'不含税金额', 
 'GraphCode':'二维码中的值', 
 'InvoiceSIA1':'？暂时未知InvoiceSIA1', 
 'InvoiceSIA2':'？暂时未知InvoiceSIA2', 
 'Signature':'签名', 
 'GoodsInfos':'货物清单'}

def get_key_by_val(d, val):
    for key in d.keys():
        if val == d[key]:
            return key


invoice_col_order = ('fileName', 'fileType', 'headline', 'DocID', 'InvoiceCode', 'InvoiceNo',
                     'TypeCode', 'IssueDate', 'InvoiceCheckCode', 'MachineNo', 'TaxControlCode',
                     'BuyerName', 'BuyerTaxID', 'BuyerAddrTel', 'BuyerFinancialAccount',
                     'Tpvn', 'SellerName', 'SellerTaxID', 'SellerAddrTel', 'SellerFinancialAccount',
                     'Issuea1', 'Issuea2', 'TaxInclusiveTotalAmount', 'Note', 'InvoiceClerk',
                     'Payee', 'Checker', 'TaxTotalAmount', 'TaxExclusiveTotalAmount',
                     'GraphCode', 'InvoiceSIA1', 'InvoiceSIA2', 'Signature', 'GoodsInfos')
goods_col_info = {'orderNo':'序号', 
 'Item':'项目名称', 
 'Specification':'规格型号', 
 'MeasurementDimension':'单位', 
 'Quantity':'数量', 
 'Price':'单价', 
 'Amount':'金额', 
 'TaxScheme':'税率', 
 'TaxAmount':'税额'}
goods_col_order = ('orderNo', 'Item', 'Specification', 'MeasurementDimension', 'Quantity',
                   'Price', 'Amount', 'TaxScheme', 'TaxAmount')

class eInvoice:

    def __init__(self, col_dict):
        self.col_dict = col_dict
        for item in invoice_col_order:
            if item not in self.col_dict:
                self.col_dict[item] = ''
            if item in ('TaxInclusiveTotalAmount', 'TaxTotalAmount', 'TaxExclusiveTotalAmount'):
                try:
                    self.col_dict[item] = float(self.col_dict[item])
                except Exception as e:
                    try:
                        pass
                    finally:
                        e = None
                        del e

    def __str__(self):
        return self.col_dict.__str__()

    def print_with_col_name(self):
        for item in invoice_col_order:
            if item == 'GoodsInfos':
                print(invoice_col_info[item] + ': ' + GoodsInfo(self.col_dict[item]).__str__())
            else:
                print(invoice_col_info[item] + ': ' + self.col_dict[item])


class GoodsInfo:

    def __init__(self, goods):
        self.goods = goods
        if not goods:
            self.goods = [
             {'X': 1}]
        for col_dict in self.goods:
            for item in goods_col_order:
                if item not in col_dict:
                    col_dict[item] = ''

    def __str__(self):
        s = ''
        for col_dict in self.goods:
            for item in goods_col_order:
                #s = s + 'ψ' + str(col_dict[item])
                s = s + '|' + str(col_dict[item])

            s = s + '\n'

        return s