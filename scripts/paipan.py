# -*- coding: utf-8 -*-
"""通用八字排盘（开源版）：输入出生公历时间+性别 → 输出四柱/十神/藏干/大运。
无任何内置个人信息。口径：默认按输入时间直接排（真太阳时请自行换算）。
依赖：lunar-python
"""
import sys, argparse
sys.stdout.reconfigure(encoding='utf-8')
from lunar_python import Solar

GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'
# 五行: 甲乙木 丙丁火 戊己土 庚辛金 壬癸水
WX = {'甲乙': '木', '丙丁': '火', '戊己': '土', '庚辛': '金', '壬癸': '水'}
YINYANG = {'甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴', '戊': '阳', '己': '阴',
           '庚': '阳', '辛': '阴', '壬': '阳', '癸': '阴'}
# 地支藏干（本气/中气/余气）
CANG = {
    '子': ['癸'], '丑': ['己', '癸', '辛'], '寅': ['甲', '丙', '戊'],
    '卯': ['乙'], '辰': ['戊', '乙', '癸'], '巳': ['丙', '戊', '庚'],
    '午': ['丁', '己'], '未': ['己', '丁', '乙'], '申': ['庚', '壬', '戊'],
    '酉': ['辛'], '戌': ['戊', '辛', '丁'], '亥': ['壬', '甲'],
}
SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}  # 我生
KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}      # 我克

def wuxing(g):
    for k, v in WX.items():
        if g in k:
            return v
    return ''

# 地支五行（本气）
ZHI_WX = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
          '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'}

def zhi_wuxing(z):
    return ZHI_WX.get(z, '')

def shishen(day_gan, other_gan):
    """十神：以日干为我"""
    dg, og = day_gan, other_gan
    dw, ow = wuxing(dg), wuxing(og)
    if dw == ow:
        return '比肩' if YINYANG[dg] == YINYANG[og] else '劫财'
    if SHENG[ow] == dw:   # 生我者 印
        return '正印' if YINYANG[dg] != YINYANG[og] else '偏印'
    if SHENG[dw] == ow:   # 我生者 食伤
        return '伤官' if YINYANG[dg] != YINYANG[og] else '食神'
    if KE[dw] == ow:      # 我克者 财
        return '正财' if YINYANG[dg] != YINYANG[og] else '偏财'
    if KE[ow] == dw:      # 克我者 官杀
        return '正官' if YINYANG[dg] != YINYANG[og] else '七杀'
    return ''

def paipan(y, m, d, hh, mm, gender):
    solar = Solar.fromYmdHms(y, m, d, hh, mm, 0)
    lunar = solar.getLunar()
    ec = lunar.getEightChar()
    pillars = [ec.getYear(), ec.getMonth(), ec.getDay(), ec.getTime()]
    day_gan = pillars[2][0]
    result = {'四柱': [], '十神_天干': [], '藏干': [], '五行统计': {}}
    wx_count = {}
    for i, p in enumerate(pillars):
        g, z = p[0], p[1]
        ss = shishen(day_gan, g)
        cang = CANG[z]
        cang_ss = [(c, shishen(day_gan, c), wuxing(c)) for c in cang]
        result['四柱'].append(p)
        result['十神_天干'].append(ss if i != 2 else '日主')
        result['藏干'].append(cang_ss)
        for c in [g] + cang:
            w = wuxing(c)
            wx_count[w] = wx_count.get(w, 0) + 1
    result['五行统计'] = wx_count
    result['日主'] = day_gan
    result['日主五行'] = wuxing(day_gan)
    # 大运
    yun = ec.getYun(1 if gender == '男' else 0)
    dayuns = []
    for dy in yun.getDaYun():
        dayuns.append({'起运岁': dy.getStartAge(), '干支': dy.getGanZhi()})
    result['大运'] = dayuns
    result['性别'] = gender
    result['公历'] = f'{y}-{m:02d}-{d:02d} {hh:02d}:{mm:02d}'
    return result

def main():
    ap = argparse.ArgumentParser(description='通用八字排盘（开源版，无内置个人信息）')
    ap.add_argument('--solar', help='公历日期 YYYY-MM-DD')
    ap.add_argument('--time', help='时间 HH:MM')
    ap.add_argument('--gender', choices=['男', '女'], default='男')
    a = ap.parse_args()
    if not a.solar:
        ap.error('需要 --solar YYYY-MM-DD')
    y, m, d = [int(x) for x in a.solar.split('-')]
    hh, mm = (int(x) for x in (a.time or '12:00').split(':'))
    r = paipan(y, m, d, hh, mm, a.gender)
    print('公历：', r['公历'], '性别：', r['性别'])
    print('四柱：', ' '.join(r['四柱']))
    print('日主：', r['日主'], f"({r['日主五行']})", '十神(年/月/日/时)：', ' '.join(r['十神_天干']))
    print('藏干十神：')
    for p, cang in zip(r['四柱'], r['藏干']):
        s = ', '.join(f'{c}({ss},{w})' for c, ss, w in cang)
        print(f'  {p}: {s}')
    print('五行统计：', r['五行统计'])
    print('大运：', ' '.join(f"{x['起运岁']}岁起 {x['干支']}" for x in r['大运'][:8]))

if __name__ == '__main__':
    main()
