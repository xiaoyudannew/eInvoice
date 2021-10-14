class point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_similar_with(self, p):
        return abs(self.x - p.x) < 10 and abs(self.y - p.y) < 10

    def __str__(self):
        return ' (x:' + str(self.x) + '\ty:' + str(self.y) + ')'


class Range:

    def __init__(self, point1, point2):
        self.p1 = point1
        self.p2 = point2

    def is_in_range(self, point1):
        if (self.p1.x <= point1.x <= self.p2.x) or (self.p2.x <= point1.x <= self.p1.x):
            if (self.p1.y <= point1.y <= self.p2.y) or (self.p2.y <= point1.y <= self.p1.y):
                return True


def merge_similar_point(point_list):
    result_list = []
    while True:
        if not point_list:
            break
        else:
            tmp_list = []
            tmp_point = None
            for i in point_list:
                if tmp_point:
                    if tmp_point.is_similar_with(i):
                        tmp_list.append(i)
                        continue
                else:
                    tmp_point = i
                    tmp_list.append(i)

            x = y = 0
            for i in tmp_list:
                point_list.remove(i)
                x = x + i.x
                y = y + i.y

            x = round(x / len(tmp_list), 2)
            y = round(y / len(tmp_list), 2)
            result_list.append(point(x, y))

    return result_list


def optimize_to_straight_line(point_list, typ):
    result_list = []
    while 1:
        if not point_list:
            break
        else:
            tmp_list = []
            tmp_point = None
            for i in point_list:
                if tmp_point:
                    n = 0
                    if typ == 'x':
                        n = tmp_point.x - i.x
                    else:
                        n = tmp_point.y - i.y
                    if abs(n) < 12:
                        tmp_list.append(i)
                        continue
                else:
                    tmp_point = i
                    tmp_list.append(i)

            n = 0
            for i in tmp_list:
                point_list.remove(i)
                if typ == 'x':
                    n = n + i.x
                else:
                    n = n + i.y

            n = round(n / len(tmp_list), 2)
            for i in tmp_list:
                if typ == 'x':
                    result_list.append(point(n, i.y))
                else:
                    result_list.append(point(i.x, n))

    return result_list


def order_point(point_list):
    p_dict = {}
    tmp_p_list = []
    for i in point_list:
        if i.y not in p_dict:
            p_dict[i.y] = []
        #else:
        p_dict[i.y].append(i)

    for k in sorted(p_dict, reverse=True):
        tmp_p_list.append(p_dict[k])

    for t in tmp_p_list:
        for i in range(len(t) - 1):
            for j in range(len(t) - i - 1):
                if t[j].x > t[(j + 1)].x:
                    #t[j], t[j + 1] = t[(j + 1)], t[j]
                    tmp = t[j]
                    t[j] = t[(j + 1)]
                    t[(j + 1)] = tmp

    return tmp_p_list


def fix_some_missing_point(point_list):
    if len(point_list) > 5:
        return point_list
    num_list = [5, 12, 8, 6, 5]
    ok_list = []
    not_ok_list = []
    for i, pl in enumerate(point_list):
        if len(pl) == num_list[i]:
            ok_list.append(i)
        else:
            not_ok_list.append(i)

    if ok_list:
        x0 = point_list[ok_list[0]][0].x
        x1 = point_list[ok_list[0]][(-1)].x
        for j in not_ok_list:
            pl = point_list[j]
            if pl[0].x != x0:
                pl.insert(0, point(x0, pl[0].y))
            if pl[(-1)].x != x1:
                pl.append(point(x1, pl[0].y))

    return point_list


def check_and_fix_point(point_list):
    point_list2 = point_list.copy()
    for i in point_list2:
        if len(i) < 4:
            point_list.remove(i)

    if len(point_list) < 5:
        raise Exception('提取到的表格行数不对。')

    point_list = fix_some_missing_point(point_list)

    #print('表格行数:' + str(len(point_list)))
    #cnt = 1
    #for i in point_list:
        #print('第' + str(cnt) + '行点数量:' + str(len(i)))
        #for p in i:
            #print('('+str(p.x)+','+str(p.y)+')')
        #cnt = cnt + 1

    #if not len(point_list[0]) != 5:
        #if (len(point_list[1]) != 12 or len(point_list[2])) != 8 and not len(point_list[2]) != 9:
            #if len(point_list[3]) != 6 or (len(point_list[4]) != 5):
                #raise Exception('提取到的表格行点位点数不对。')
            #line2 = point_list[1]
            #line3 = point_list[2]
            #if len(line3) == 8:
                #new_point = point(line2[2].x, line3[0].y)
                #line3.insert(1, new_point)
        #return point_list
    if len(point_list[0]) != 5 or len(point_list[1]) != 12 or (len(point_list[2]) != 8 and len(point_list[2]) != 9) or len(point_list[3]) != 6 or len(point_list[4]) != 5 :
        raise Exception('提取到的表格行点位点数不对。')
    if len(point_list[2]) == 8 :
        line2 = point_list[1]
        line3 = point_list[2]
        new_point = point(line2[2].x, line3[0].y)
        line3.insert(1, new_point)
    return point_list


def two_edges_format_to_one(edges):
    edges_list = []
    while edges:
        tmp_edge = None
        cnt = 0
        for i in edges:
            cnt = cnt + 1
            if len(edges) == 1:
                edges.remove(i)
                edges_list.append(i)
                break
            if not tmp_edge:
                tmp_edge = i
                continue
            if i['pts'] == tmp_edge['pts']:
                if tmp_edge != i:
                    edges.remove(i)
                    edges.remove(tmp_edge)
                    if i['x0'] == i['x1']:
                        x = (i['x0'] + tmp_edge['x1']) / 2
                        i['x0'] = i['x1'] = x
                    else:
                        y = (i['y0'] + tmp_edge['y1']) / 2
                        i['y0'] = i['y1'] = y
                    edges_list.append(i)
                    break
            if len(edges) == cnt:
                edges.remove(tmp_edge)
                edges_list.append(tmp_edge)
                break

    return edges_list


def is_pts_in_xy(obj):
    xy = [
     obj['x0'], obj['y0'], obj['x1'], obj['y1']]
    pts = obj['pts']
    for pt in pts:
        for p in pt:
            if p not in xy:
                return False

    return True


def get_point_from_obj(obj):
    p_list = []
    x0 = float(str(obj['x0']))
    y0 = float(str(obj['y0']))
    x1 = float(str(obj['x1']))
    y1 = float(str(obj['y1']))
    if obj['width'] < 15:
        if obj['height'] < 15:
            return []
    if obj['width'] > 600 or (obj['height'] > 600):
        return []
    if not x0 < 0:
        if y0 < 0 or (x1 < 0 or y1 < 0):
            return []
        if obj['object_type'] == 'rect' or obj['object_type'] == 'curve':
            p_list.append(point(x0, y0))
            p_list.append(point(x0, y1))
            p_list.append(point(x1, y0))
            p_list.append(point(x1, y1))
        else:
            p_list.append(point(x0, y0))
            p_list.append(point(x1, y1))
        return p_list


def is_line_color_ok(obj):
    non_stroking_color = obj['non_stroking_color']
    stroking_color = obj['stroking_color']
    if isinstance(non_stroking_color, list):
        if non_stroking_color[0] == 1 or (non_stroking_color[1] == 1 or non_stroking_color[2] == 1):
            return False
        if isinstance(stroking_color, int):
            if stroking_color == 1:
                return False
        return True


def get_point_list(page, typ):
    p_list = []
    tmp_list = page.edges
    tmp_list2 = page.curves
    tmp_list3 = page.rects
    tmp_list4 = page.annots
    if typ == '1':
        for _ in tmp_list:
            p_list = p_list + get_point_from_obj(_)

    elif typ == '2':
        for _ in tmp_list:
            if not is_line_color_ok(_):
                continue
            else:
                p_list = p_list + get_point_from_obj(_)

    elif typ == '3':
        for _ in tmp_list2:
            if not is_line_color_ok(_):
                continue
            else:
                p_list = p_list + get_point_from_obj(_)

    elif typ == '4':
        for _ in tmp_list + tmp_list2:
            if not is_pts_in_xy(_):
                continue
            else:
                p_list = p_list + get_point_from_obj(_)

    elif typ == '5':
        t = tmp_list3 + tmp_list + tmp_list2
        for _ in t:
            if not is_pts_in_xy(_):
                t.remove(_)

        for _ in tmp_list3 + tmp_list + tmp_list2:
            if not is_line_color_ok(_):
                continue
            if not is_pts_in_xy(_):
                continue
            else:
                p_list = p_list + get_point_from_obj(_)

    elif typ == '6':
        for _ in tmp_list4:
            p_list = p_list + get_point_from_obj(_)

    else:
        return
    p_list = merge_similar_point(p_list)
    p_list = optimize_to_straight_line(p_list, 'x')
    p_list = optimize_to_straight_line(p_list, 'y')
    p_list = merge_similar_point(p_list)
    p_list = order_point(p_list)
    p_list = check_and_fix_point(p_list)
    return p_list


def get_point_list_from_pdf(page):
    typ_list = [
     '1', '2', '3', '4', '5', '6']
    p_list = None
    for typ in typ_list:
        try:
            p_list = get_point_list(page, typ)
        except Exception as e:
            try:
                p_list = None
            finally:
                e = None
                del e

        if p_list:
            break

    return p_list


def show_points_in_image(point_list):
    x_list = []
    y_list = []
    for p1 in point_list:
        for p in p1:
            x_list.append(p.x)
            y_list.append(p.y)


def get_char_list_from_range(page, r):
    char_list = []
    for c in page.chars:
        #if c['text'] == '餐' :
            #print(c['text'] + ':('+str(c['x0'])+','+str(c['y0'])+')')
        p = point(float(str(c['x0'])), float(str(c['y0'])))
        if r.is_in_range(p):
            char_list.append(c)

    return char_list


def order_chars(chars):
    #print('符合的字符数量:' + str(len(chars)))
    y_dict = {}
    for c in chars:
        find_flg = False
        y0 = float(str(c['y0']))
        for key in y_dict:
            if abs(key - y0) < 3:
                y_dict[key].append(c)
                find_flg = True
                break

        if not find_flg:
            y_dict[y0] = [c]

    for y_line in y_dict:
        line = y_dict[y_line]
        for i in range(len(line) - 1):
            for j in range(len(line) - i - 1):
                if float(str(line[j]['x0'])) > float(str(line[(j + 1)]['x0'])):
                    line[j], line[j + 1] = line[(j + 1)], line[j]

        y_dict[y_line] = line

    s_dict = {}
    for key in sorted(y_dict, reverse=True):
        s = ''
        for c in y_dict[key]:
            s = s + c['text']

        s_dict[key] = s

    return s_dict


def is_num_in_list(num, num_list):
    for num2 in num_list:
        if abs(num - num2) < 4:
            return num2


def format_goods_info(item_dict):
    line_list = []
    for key in item_dict:
        new_chars_dict = {}
        chars_dict = item_dict[key]
        for key2 in chars_dict:
            num2 = is_num_in_list(key2, line_list)
            if num2:
                new_chars_dict[num2] = chars_dict[key2]
            else:
                line_list.append(key2)
                new_chars_dict[key2] = chars_dict[key2]

        item_dict[key] = new_chars_dict

    tmp_line_list = line_list.copy()
    for key in tmp_line_list:
        if key in item_dict['Amount']:
            if '金' in item_dict['Amount'][key]:
                line_list.remove(key)
        if key in item_dict['Item']:
            if '合计' == item_dict['Item'][key].replace(' ', ''):
                line_list.remove(key)
        if key not in item_dict['Item']:
            if key in item_dict['Amount']:
                line_list.remove(key)

    tmp_line_list = line_list.copy()
    last_key = None
    for key in tmp_line_list:
        if key not in item_dict['Amount']:
            if key in item_dict['Item']:
                if last_key:
                    item_dict['Item'][last_key] = item_dict['Item'][last_key] + item_dict['Item'][key]
            line_list.remove(key)
            last_key = None
        else:
            last_key = key

    goods_list = []
    for i, key in enumerate(line_list):
        goods_d = {'orderNo': i + 1}
        for key2 in item_dict:
            if key in item_dict[key2]:
                goods_d[key2] = item_dict[key2][key]

        goods_list.append(goods_d)

    return goods_list