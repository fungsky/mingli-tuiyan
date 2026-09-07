# -*- coding: utf-8 -*-
"""四视角命理推演（开源通用版）——强弱 / 调候 / 格局 / 形象。

参考陆致极《命运的求索——中国命理学简史及推演方法》多视角推演程式。
纯算法输出（可复现可验证）；解读层需分析师完成，本脚本不生成"命运结论"。

用法：
  python tuiyan.py --bazi "庚午 壬午 辛亥 癸巳" --gender 男
  python tuiyan.py --solar 1990-06-15 --time 10:30 --gender 男   # 自动排盘（示例日期为虚构占位）
"""
import sys, argparse
sys.stdout.reconfigure(encoding='utf-8')

from bazipai import wuxing, zhi_wuxing, shishen, CANG, SHENG, KE, paipan, YINYANG
from tiaohou_table import get_tiaohou

# ---------- 常量 ----------
# 十二长生（阳干顺/阴干逆，用于得地判断参考；此处用简表：禄=临官）
LU = {'甲': '寅', '乙': '卯', '丙': '巳', '丁': '午', '戊': '巳', '己': '午',
      '庚': '申', '辛': '酉', '壬': '亥', '癸': '子'}

# ---------- 视角一：强弱 ----------
# 月令状态权重（当令者旺/生我相/我生休/我克囚/克我死）
#   旺(同气)+3, 相(生我)+2, 休(当令所泄)-3, 囚(克当令)-1, 死(当令所克)-4
def month_state(day_wx, month_wx):
    if day_wx == month_wx: return 3      # 旺
    if SHENG[month_wx] == day_wx: return 2   # 相：月令生我
    if SHENG[day_wx] == month_wx: return -3  # 休：我生月令(当令泄我)
    if KE[day_wx] == month_wx: return -1     # 囚：我克月令
    return -4                                 # 死：月令克我

def cang_pos(z, target_gan):
    """返回 target_gan 在支 z 藏干中的位置（本气/中气/余气/None）"""
    c = CANG[z]
    if target_gan == c[0]: return '本气'
    if len(c) > 1 and target_gan == c[1]: return '中气'
    if len(c) > 2 and target_gan == c[2]: return '余气'
    return None

def analyze_qiangruo(pillars, day_gan):
    """日主强弱：得令 + 得地 + 得生 + 得势
    得地=日主同五行通根；得生=印星生扶(封顶2.0)；得势=天干印比帮扶/财官食伤耗泄。
    """
    day_wx = wuxing(day_gan)
    month_zhi = pillars[1][1]
    month_wx = zhi_wuxing(month_zhi)
    score = month_state(day_wx, month_wx)
    st_map = {3: '旺', 2: '相', -3: '休', -1: '囚', -4: '死'}
    detail = [f'月令[{month_zhi}{month_wx}]: {st_map.get(score,"?")}({score:+d})']

    # 得地：四支中找日主同五行的藏干根（禄刃最重）
    lu = LU[day_gan]
    di_score, di_note = 0.0, []
    for p in pillars:
        z = p[1]
        if z == lu:                      # 禄位：日主同气本气
            di_score += 3.0
            di_note.append(f'{z}=禄(+3)')
            continue
        best = None
        for pos, c in enumerate(CANG[z]):
            if wuxing(c) == day_wx:      # 同五行根
                w = (2.0, 1.0, 0.5)[pos]
                if best is None or w > best[1]:
                    best = (c, w, ('本气', '中气', '余气')[pos])
        if best:
            di_score += best[1]
            di_note.append(f'{z}藏{best[0]}={best[2]}(+{best[1]:g})')
    detail.append(f'得地: {di_score:+.1f}  [{" ".join(di_note) if di_note else "无根"}]')
    score += di_score

    # 得生：印星（生我五行）藏干生扶，封顶 2.0
    sheng_score, sheng_note = 0.0, []
    for p in pillars:
        z = p[1]
        for pos, c in enumerate(CANG[z]):
            if SHENG[wuxing(c)] == day_wx:
                w = (0.8, 0.5, 0.3)[pos]
                if sheng_score >= 2.0:
                    break
                room = min(w, 2.0 - sheng_score)
                if room <= 0:
                    break
                sheng_score += room
                sheng_note.append(f'{z}藏{c}=印(+{room:g})')
                break
    detail.append(f'得生(印): {sheng_score:+.1f}  [{" ".join(sheng_note) if sheng_note else "无印"}]')
    score += sheng_score

    # 得势：天干印比帮扶、财官食伤耗泄
    shi_score = 0.0
    shi_note = []
    for i, p in enumerate(pillars):
        if i == 2: continue
        g = p[0]
        ss = shishen(day_gan, g)
        if ss in ('正印', '偏印'):
            shi_score += 1.5; shi_note.append(f'{g}{ss}(+1.5)')
        elif ss in ('比肩', '劫财'):
            shi_score += 1.0; shi_note.append(f'{g}{ss}(+1)')
        elif ss in ('食神', '伤官'):
            shi_score -= 0.8; shi_note.append(f'{g}{ss}(-0.8)')
        elif ss in ('正财', '偏财'):
            shi_score -= 1.0; shi_note.append(f'{g}{ss}(-1)')
        elif ss in ('正官', '七杀'):
            shi_score -= 1.2; shi_note.append(f'{g}{ss}(-1.2)')
    detail.append(f'得势: {shi_score:+.1f}  [{" ".join(shi_note) if shi_note else "无"}]')
    score += shi_score

    if score >= 6: verdict = '身强'
    elif score >= 2: verdict = '偏强'
    elif score > -2: verdict = '中和'
    elif score > -6: verdict = '偏弱'
    else: verdict = '身弱'
    return {'score': round(score, 1), 'verdict': verdict, 'detail': detail,
            '喜': '印(生扶)、比劫(帮身)' if verdict in ('身弱', '偏弱') else ('财官食伤(克泄耗)' if verdict in ('身强', '偏强') else '中和看局')}

def label_of(pos):
    return ('本气', '中气', '余气')[pos]

# ---------- 视角二：调候 ----------
def analyze_tiaohou(pillars, day_gan):
    month_zhi = pillars[1][1]
    yongshen, m = get_tiaohou(day_gan, month_zhi)
    present = []
    missing = []
    all_chars = ''.join(p[0] + p[1] for p in pillars) + ''.join(''.join(c) for z in (p[1] for p in pillars) for c in CANG[z])
    for ys in yongshen:
        # 用神天干明现或地支藏干有
        hit = any(ys == c for p in pillars for c in p) or any(ys == c for z in (p[1] for p in pillars) for c in CANG[z])
        (present if hit else missing).append(ys)
    return {'月序': m, '月支': month_zhi, '调候用神': yongshen,
            '已现': present, '未现': missing}

# ---------- 视角三：格局 ----------
def analyze_geju(pillars, day_gan):
    """月令取格（正格八格初判）+ 透干参考"""
    month_zhi = pillars[1][1]
    cang = CANG[month_zhi]
    benqi = cang[0]                      # 本气
    benqi_ss = shishen(day_gan, benqi)
    ge_map = {'食神': '食神格', '伤官': '伤官格', '正财': '正财格', '偏财': '偏财格',
              '正官': '正官格', '七杀': '七杀格', '正印': '正印格', '偏印': '偏印格'}
    geju = ge_map.get(benqi_ss)
    # 透干（月支藏干透到天干）
    tous = []
    for p in pillars[:1] + pillars[2:]:
        g = p[0]
        if g in cang and g != day_gan:
            tous.append(f'{g}({shishen(day_gan, g)})')
    return {'月支': month_zhi, '本气': benqi, '本气十神': benqi_ss,
            '初判格局': geju or '（月令为比劫，需看透干/会合取格）',
            '透干参考': tous or '无'}

# ---------- 视角四：形象（数据层） ----------
def analyze_xingxiang(pillars, day_gan):
    wx_count = {}
    for p in pillars:
        g, z = p[0], p[1]
        wg, wz = wuxing(g), zhi_wuxing(z)
        wx_count[wg] = wx_count.get(wg, 0) + 1
        wx_count[wz] = wx_count.get(wz, 0) + 1
    # 补齐藏干
    for p in pillars:
        for c in CANG[p[1]]:
            w = wuxing(c)
            wx_count[w] = wx_count.get(w, 0) + 1
    order = ['木', '火', '土', '金', '水']
    missing = [w for w in order if w not in wx_count]
    strongest = max(wx_count, key=wx_count.get) if wx_count else ''
    weakest = min(wx_count, key=wx_count.get) if wx_count else ''
    return {'五行统计': {w: wx_count.get(w, 0) for w in order},
            '最旺': strongest, '最弱': weakest, '缺': missing or '无'}

def main():
    ap = argparse.ArgumentParser(description='四视角命理推演（开源通用版）')
    ap.add_argument('--bazi', help='四柱，如 "庚午 壬午 辛亥 癸巳"')
    ap.add_argument('--solar', help='或提供公历 YYYY-MM-DD + --time + --gender 自动排盘')
    ap.add_argument('--time', default='12:00')
    ap.add_argument('--gender', choices=['男', '女'], default='男')
    a = ap.parse_args()

    if a.bazi:
        pillars = a.bazi.split()
    elif a.solar:
        y, m, d = [int(x) for x in a.solar.split('-')]
        hh, mm = (int(x) for x in a.time.split(':'))
        r = paipan(y, m, d, hh, mm, a.gender)
        pillars = r['四柱']
    else:
        ap.error('需要 --bazi 或 --solar')
    if len(pillars) != 4:
        ap.error('四柱格式应为 4 组干支')

    day_gan = pillars[2][0]
    print('=' * 58)
    print(f'四柱：{" ".join(pillars)}    日主：{day_gan}({wuxing(day_gan)})')
    print('=' * 58)

    print('\n【视角一 · 强弱分析（扶抑）】')
    q = analyze_qiangruo(pillars, day_gan)
    for d in q['detail']:
        print('  ', d)
    print(f"  → 总分 {q['score']:+.1f}：{q['verdict']}")
    print(f"  → 喜用方向参考：{q['喜']}")

    print('\n【视角二 · 调候分析（穷通宝鉴）】')
    t = analyze_tiaohou(pillars, day_gan)
    print(f"  {day_gan}日主生于{t['月支']}月 → 调候主用神：{'、'.join(t['调候用神'])}")
    print(f"  命局已现：{'、'.join(t['已现']) if t['已现'] else '无'}   未现：{'、'.join(t['未现']) if t['未现'] else '无'}")

    print('\n【视角三 · 格局分析（月令取格）】')
    g = analyze_geju(pillars, day_gan)
    print(f"  月令 {g['月支']}，本气 {g['本气']}({g['本气十神']}) → 初判：{g['初判格局']}")
    print(f"  透干参考：{g['透干参考']}")

    print('\n【视角四 · 形象分析（五行分布·数据层）】')
    x = analyze_xingxiang(pillars, day_gan)
    print(f"  五行统计：{' '.join(f'{w}{n}' for w, n in x['五行统计'].items())}")
    print(f"  最旺：{x['最旺']}   最弱：{x['最弱']}   缺：{x['缺']}")

    print('\n' + '-' * 58)
    print('提示：以上为可复现的算法初判（强弱/调候/格局/五行），')
    print('综合解读（形象气象、性情、大运流年应期、六亲）需分析师结合理论库完成。')
    print('命理属传统文化研究，输出为概率性倾向，不作决策依据。')

if __name__ == '__main__':
    main()
