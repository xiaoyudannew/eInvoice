import re, pdfplumber
from PDFInvoiceUtils import get_point_list_from_pdf, point, Range, get_char_list_from_range, order_chars, format_goods_info

def get_txt_from_pdf(pdf_path):
    pdf = pdfplumber.open(pdf_path, password='')
    txt = pdf.pages[0].extract_text(x_tolerance=3, y_tolerance=3)
    pdf.close()
    if txt is None:
        return 'pdf中提取字符失败，估计是pdf中是一张图片'
    txt = txt.replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ')
    txt = txt.replace('：', ':').replace('（', '(').replace('）', ')').replace('¥', '￥').replace('\u3000', ' ').replace('＊', '*').replace('* *', '**').replace('* *', '**').replace('  ', ' ').replace('  ', ' ')
    txt = txt.replace(': ', ':').replace(': ', ':').replace(' :', ':').replace(' :', ':')
    return txt


def get_dtl_from_pdf(pdf_path):
    txt = get_txt_from_pdf(pdf_path)
    page = pdfplumber.open(pdf_path, password='').pages[0]
    p_list = get_point_list_from_pdf(page)
    dict1 = {'fileName':pdf_path, 
     'fileType':'PDF'}
    if txt is None or (txt.replace(' ', '').find('电子普通发票') == -1):
        dict1['headline'] = '解析失败:1、可能此文件不是正规电子发票(如，PDF中是图片发票)；2、此文件存在页面提取保护；3、pdfminer的camp未安装或未打包成功。'
        return dict1
    TaxControlCode = re.findall('[0-9/+*<>-]{21,28}', txt)
    TaxControlCode2 = re.findall('[ 0-9/+*<>-]{21,60}', txt)
    if TaxControlCode and len(TaxControlCode) > 3:
        TaxControlCode = TaxControlCode[0:4]
        txt = txt.replace(TaxControlCode[0], '').replace(TaxControlCode[1], '').replace(TaxControlCode[2], '').replace(TaxControlCode[3], '')
    elif TaxControlCode2 and len(TaxControlCode2) > 3:
        must_str = [
         '/', '+', '*', '<', '>', '-']
        TaxControlCode2_temp = []
        ok_flag = False
        for i in TaxControlCode2:
            for s in must_str:
                if i == s:
                    ok_flag = True
                    break

            if ok_flag:
                TaxControlCode2_temp.append(i)
                break

        if TaxControlCode2_temp and len(TaxControlCode2_temp) > 3:
            TaxControlCode = TaxControlCode2_temp
            txt = txt.replace(TaxControlCode[0], '').replace(TaxControlCode[1], '').replace(TaxControlCode[2], '').replace(TaxControlCode[3], '')
        else:
            TaxControlCode = '密码区提取失败，这将导致购买方的信息提取也出现错误。'
    else:
        TaxControlCode = re.findall('[0-9a-f ]{21,60}', txt)[0:3]
        if len(TaxControlCode) > 2:
            txt = txt.replace(TaxControlCode[0], '').replace(TaxControlCode[1], '').replace(TaxControlCode[2], '')
        else:
            TaxControlCode = '密码区提取失败，这将导致购买方的信息提取也出现错误。'
    dict1['TaxControlCode'] = TaxControlCode
    txt_h = txt.split('价税合计')[0]
    txt_t = txt.split('价税合计')[1]
    if re.search('机器编号(.*)', txt_h):
        MachineNo = re.search('机器编号(.*)', txt_h).group().split(':')[1].lstrip().split(' ')[0]
    else:
        MachineNo = ''
    dict1['MachineNo'] = MachineNo
    headline = re.search('(.*)电子普通发票', txt_h)
    if headline:
        headline = headline.group()
    else:
        headline = re.search('(.*)电(\\s*)子(\\s*)普(\\s*)通(\\s*)发(\\s*)票', txt_h).group().replace(' ', '')
    if len(headline) > 11:
        if headline.count(' ') >= 1:
            tmp_strs = headline.split()
            for s in tmp_strs:
                if s.count('增值税电子普通发票') == 1:
                    if len(s) >= 11:
                        headline = s

    headline = headline.replace(' ', '')
    dict1['headline'] = headline
    dict1['InvoiceCode'] = re.search('发票代码(.*)', txt_h).group().split(':')[1].replace(' ', '')
    dict1['InvoiceNo'] = re.search('发票号码(.*)', txt_h).group().split(':')[1].replace(' ', '')
    dict1['IssueDate'] = re.search('开票日期(.*)', txt_h).group().split(':')[1].replace(' ', '')
    dict1['InvoiceCheckCode'] = re.search('校(.*)验(.*)码(.*)', txt_h).group().split(':')[1]
    BuyerName = re.search('名(.*)称(.*):(.*)', txt_h).group().split(':')[1].lstrip().split(' ')[0].replace(' ', '')
    BuyerTaxID = re.search('纳税人识别号(.*)', txt_h).group().split(':')[1].replace(' ', '')
    if len(BuyerTaxID) < 10:
        BuyerTaxID = re.search('[A-Za-z0-9]{15,}.{1,10}纳税人识别号', txt_h.replace('\n', ' '))
        if BuyerTaxID:
            BuyerTaxID = re.search('[A-Za-z0-9]{15,}', BuyerTaxID.group().replace(' ', '')).group()
        else:
            BuyerTaxID = ''.join(re.findall('[A-Za-z0-9]', BuyerName))
            if len(BuyerTaxID) >= 15:
                BuyerTaxID = BuyerTaxID
                BuyerName = ''.join(re.findall('[一-龥()]', BuyerName))
            else:
                BuyerTaxID = ''
    else:
        BuyerTaxID = re.search('[A-Za-z0-9]{15,}', BuyerTaxID)
        if BuyerTaxID:
            BuyerTaxID = BuyerTaxID.group()
        else:
            BuyerTaxID = ''
    dict1['BuyerName'] = BuyerName
    dict1['BuyerTaxID'] = BuyerTaxID
    BuyerAddrTel = re.search('地(.*)址(.*)、(.*)电(.*)话(.*)', txt_h).group()
    info_txt = re.search(':(.+)[\\u4E00-\\u9FA5 ]+(.*)([0-9]|-|#{6,})', BuyerAddrTel)
    if info_txt:
        info_txt = info_txt.group().replace(':', '')
        if len(info_txt) >= 1:
            BuyerAddrTel = info_txt
    else:
        BuyerAddrTel = ''
    dict1['BuyerAddrTel'] = BuyerAddrTel
    if re.search('开户行及账号(.*)', txt_h):
        BuyerFinancialAccount = re.search('开户行及账号(.*)', txt_h).group().split(':')[1]
    else:
        BuyerFinancialAccount = re.search('电子支付标识(.*)', txt_h).group().split(':')[1]
    info_txt = re.findall('[\\u4E00-\\u9FA5 ]+[A-Za-z0-9]{10,}', BuyerFinancialAccount)
    if len(info_txt) >= 1:
        BuyerFinancialAccount = info_txt[0]
    else:
        BuyerFinancialAccount = ''
    dict1['BuyerFinancialAccount'] = BuyerFinancialAccount
    priceBig = re.search('价税合计(.*?)大(.*?)写(.*)', txt).group().split(')')[1].split('(')[0].replace(' ', '')
    dict1['priceBig'] = priceBig
    if re.findall('￥[-0-9 .]{3,}', txt.replace(' ', '')):
        price_info = re.findall('￥[-0-9 .]{3,}', txt.replace(' ', ''))
        TaxInclusiveTotalAmount = float(price_info[(len(price_info) - 1)][1:])
    else:
        TaxInclusiveTotalAmount = float(re.search('(小写)(.*)', txt_t).group().split(')')[1])
    dict1['TaxInclusiveTotalAmount'] = TaxInclusiveTotalAmount
    TaxTotalAmount = re.search('合(.*)计(.*)[0-9 .*]{3,}', txt_h)
    if TaxTotalAmount:
        TaxTotalAmount = TaxTotalAmount.group().replace('￥', '').replace('  ', ' ').replace('  ', ' ')
        if '小写' in TaxTotalAmount:
            TaxTotalAmount = TaxTotalAmount.split('小写)')[1].split(' ')[1]
        else:
            TaxTotalAmount = TaxTotalAmount.split('计')[1].split(' ')[2]
    else:
        TaxTotalAmount = txt_h.replace('\n', ' ')[-40:-1]
        if '*合计' in TaxTotalAmount.replace(' ', ''):
            TaxTotalAmount = '***'
        else:
            TaxTotalAmount = re.findall('[-0-9.]{3,}', TaxTotalAmount)[(-1)]
    if '*' not in TaxTotalAmount:
        TaxTotalAmount = float(TaxTotalAmount)
    dict1['TaxTotalAmount'] = TaxTotalAmount
    if TaxInclusiveTotalAmount:
        if '*' not in str(TaxTotalAmount):
            dict1['TaxExclusiveTotalAmount'] = float(TaxInclusiveTotalAmount) - float(TaxTotalAmount)
        else:
            dict1['TaxExclusiveTotalAmount'] = float(TaxInclusiveTotalAmount)
    SellerName = re.search('名(.*)称(.*):(.*)', txt_t).group().split(':')[1].lstrip().split(' ')[0].replace(' ', '')
    SellerTaxID = re.search('纳税人识别号(.*)', txt_t).group().split(':')[1].replace(' ', '')
    if len(SellerTaxID) < 10:
        SellerTaxID = re.search('[A-Za-z0-9]{15,}(.*)\n(.*)纳税人识别号', txt_t.replace(' ', ''))
        if SellerTaxID:
            SellerTaxID = re.search('[A-Za-z0-9]{15,}', SellerTaxID.group().replace(' ', '')).group()
        else:
            SellerTaxID = ''.join(re.findall('[A-Za-z0-9]', SellerName))
            if len(SellerTaxID) >= 15:
                SellerTaxID = SellerTaxID
                SellerName = ''.join(re.findall('[一-龥()]', SellerName))
            else:
                SellerTaxID = ' '
    else:
        SellerTaxID = re.search('[A-Za-z0-9]{15,}', SellerTaxID).group()
    dict1['SellerName'] = SellerName
    dict1['SellerTaxID'] = SellerTaxID
    SellerAddrTel = re.search('地(.*)址(.*)、(.*)电(.*)话(.*)', txt_t).group()
    try:
        info_txt = re.search(':(.*?)[\\u4E00-\\u9FA5 ]+(.*)([0-9#-]{5,})', SellerAddrTel).group().replace(':', '')
    except Exception as e:
        try:
            SellerAddrTel = re.search('地(.*)址(.*)、(.*)电(.*)话(.*)', txt_t.replace('\n', ''), re.M).group()
            if re.search(':(.*?)[\\u4E00-\\u9FA5 ]+(.*?)([0-9#-]{5,})', SellerAddrTel):
                info_txt = re.search(':(.*?)[\\u4E00-\\u9FA5 ]+(.*?)([0-9#-]{5,})', SellerAddrTel).group().replace(':', '')
            else:
                SellerAddrTel = '未找到'
        finally:
            e = None
            del e

    if len(info_txt) >= 1:
        SellerAddrTel = info_txt.replace(' ', '')
    else:
        SellerAddrTel = ''
    dict1['SellerAddrTel'] = SellerAddrTel
    SellerFinancialAccount = re.search('开户行及账号(.*)', txt_t).group().split(':')[1]
    info_txt = re.findall('[\\u4E00-\\u9FA5 ()]+[A-Za-z0-9-]{10,}', SellerFinancialAccount)
    if len(info_txt) >= 1:
        SellerFinancialAccount = info_txt[0]
    else:
        SellerFinancialAccount = ''
    dict1['SellerFinancialAccount'] = SellerFinancialAccount
    if p_list:
        #note_range = Range(p_list[4][3], p_list[3][5])
        note_range = Range(p_list[3][4], p_list[4][3])
        note_chars = get_char_list_from_range(page, note_range)
        note_chars_dict = order_chars(note_chars)
        note_string = ''
        for key in sorted(note_chars_dict, reverse=True):
            note_string = note_string + note_chars_dict[key]

        dict1['Note'] = note_string
    else:
        dict1['Note'] = '程序未能正确解析文件中的表格，提取备注失败。'
    InvoiceClerk = re.search('开(.*)票(.*):(.*)', txt_t).group().split(':')[1].split(' ')[0]
    if InvoiceClerk[0] == '销':
        InvoiceClerk = re.search('开(.*)票(.*):(.*)', txt_t).group().split(':')[1].split('销')
        if InvoiceClerk:
            InvoiceClerk = InvoiceClerk[0]
        else:
            InvoiceClerk = None
    dict1['InvoiceClerk'] = InvoiceClerk
    Payee = re.search('收(.*)款(.*):(.*)', txt_t).group().split(':')[1].split(' ')[0]
    if Payee[0] == '复':
        Payee = re.search('收(.*)款(.*):(.*)', txt_t).group().split(':')[1].split('复')
        if Payee:
            Payee = Payee[0]
        else:
            Payee = None
    dict1['Payee'] = Payee
    Checker = re.search('复(.*)核(.*):(.*)', txt_t).group().split(':')[1].split(' ')[0]
    if Checker[0] == '开':
        Checker = re.search('复(.*)核(.*):(.*)', txt_t).group().split(':')[1].split('开')
        if Checker:
            Checker = Checker[0]
        else:
            Checker = None
    dict1['Checker'] = Checker
    if p_list:
        #print('\n最终行数:' + str(len(p_list)))
        #Item_range = Range(p_list[2][0], p_list[1][2])
        Item_range = Range(p_list[1][0], p_list[2][1])
        #Specification_range = Range(p_list[2][1], p_list[1][3])
        Specification_range = Range(p_list[1][2], p_list[2][2])
        #MeasurementDimension_range = Range(p_list[2][2], p_list[1][4])
        MeasurementDimension_range = Range(p_list[1][3], p_list[2][3])
        #Quantity_range = Range(p_list[2][3], p_list[1][5])
        Quantity_range = Range(p_list[1][4], p_list[2][4])
        #Price_range = Range(p_list[2][4], p_list[1][8])
        Price_range = Range(p_list[1][5], p_list[2][5])
        #Amount_range = Range(p_list[2][5], p_list[1][9])
        Amount_range = Range(p_list[1][8], p_list[2][6])
        #TaxScheme_range = Range(p_list[2][6], p_list[1][10])
        TaxScheme_range = Range(p_list[1][9], p_list[2][7])
        #TaxAmount_range = Range(p_list[2][7], p_list[1][11])
        TaxAmount_range = Range(p_list[1][10], p_list[2][8])
        Item_chars = order_chars(get_char_list_from_range(page, Item_range))
        Specification_chars = order_chars(get_char_list_from_range(page, Specification_range))
        MeasurementDimension_chars = order_chars(get_char_list_from_range(page, MeasurementDimension_range))
        Quantity_chars = order_chars(get_char_list_from_range(page, Quantity_range))
        Price_chars = order_chars(get_char_list_from_range(page, Price_range))
        Amount_chars = order_chars(get_char_list_from_range(page, Amount_range))
        TaxScheme_chars = order_chars(get_char_list_from_range(page, TaxScheme_range))
        TaxAmount_chars = order_chars(get_char_list_from_range(page, TaxAmount_range))
        item_dict = {'Item':Item_chars, 
         'Specification':Specification_chars,  'MeasurementDimension':MeasurementDimension_chars, 
         'Quantity':Quantity_chars,  'Price':Price_chars, 
         'Amount':Amount_chars,  'TaxScheme':TaxScheme_chars,  'TaxAmount':TaxAmount_chars}
        goods_list = format_goods_info(item_dict)
        dict1['GoodsInfos'] = goods_list
    else:
        dict1['GoodsInfos'] = None
    return dict1