# -*- coding: utf-8 -*-
"""六术复合排盘（开源通用版）——八字(双引擎互证)/六爻/紫微/奇门/黄历/占星 一键排盘。

纯通用：所有命盘信息通过命令行输入，不内置任何个人数据。
口径说明：
- 八字按输入时间直排（真太阳时请使用者自行换算）
- 占星按输入时间作为钟表时排（UT = 输入时间 - 8h），出生地经纬度用于上升点
- 六爻 seed=出生日期（可复现）
- 奇门：拆补法定局（节气→三元局）

用法：
  python liu_shu_paipan.py --solar 1990-06-15 --time 10:30 --gender 男 --lat 23.13 --lon 113.26
  python liu_shu_paipan.py --solar 1990-06-15 --time 10:30 --gender 男   # 不排占星（缺经纬度）

依赖：lunar-python, iching, py-iztro, qimendunjia, pyswisseph
"""
import sys, io, subprocess, contextlib, random, argparse
sys.stdout.reconfigure(encoding='utf-8')
from datetime import date
from lunar_python import Solar

GAN = '甲乙丙丁戊己庚辛壬癸'; ZHI = '子丑寅卯辰巳午未申酉戌亥'
SIGNS = ['白羊','金牛','双子','巨蟹','狮子','处女','天秤','天蝎','射手','摩羯','水瓶','双鱼']


def pai8(y, m, d, hh, mm):
    p = Solar.fromYmdHms(y, m, d, hh, mm, 0).getLunar()
    return p, p.getEightChar()


def section(title):
    print()
    print("=" * 62)
    print(title)
    print("=" * 62)


def main():
    ap = argparse.ArgumentParser(description='六术复合排盘（开源通用版，无内置个人信息）')
    ap.add_argument('--solar', required=True, help='公历日期 YYYY-MM-DD')
    ap.add_argument('--time', default='12:00', help='时间 HH:MM（示例为虚构占位，请替换为实际出生时间）')
    ap.add_argument('--gender', choices=['男', '女'], default='男')
    ap.add_argument('--lat', type=float, default=None, help='出生地纬度（排占星上升需要）')
    ap.add_argument('--lon', type=float, default=None, help='出生地经度（排占星上升需要）')
    a = ap.parse_args()

    y, m, d = (int(x) for x in a.solar.split('-'))
    hh, mm = (int(x) for x in a.time.split(':'))
    g = a.gender

    # ---------- ① 八字四柱 · 双引擎互证 ----------
    section('【① 八字四柱 · 双引擎互证】（lunar-python + bazi_skill 独立实现）')
    p, ba = pai8(y, m, d, hh, mm)
    calc = f"{ba.getYear()} {ba.getMonth()} {ba.getDay()} {ba.getTime()}"
    print(f"公历 {a.solar} {a.time} {g}")
    print(f"  四柱：{calc}")
    print(f"  日主：{ba.getDayGan()}({ba.getDayWuXing()[:1]}) 生肖{p.getYearShengXiao()}  十神：年{ba.getYearShiShenGan()} 月{ba.getMonthShiShenGan()} 日{ba.getDayShiShenGan()} 时{ba.getTimeShiShenGan()}")
    try:
        r = subprocess.run([sys.executable, "bazi_paipan_duli.py",
                            "--solar", f"{y}-{m:02d}-{d:02d}",
                            "--hour", f"{hh}:{mm:02d}", "--sex", g],
                           capture_output=True, text=True, timeout=60,
                           cwd=str(__import__('pathlib').Path(__file__).parent))
        gan2 = zhi2 = []
        for line in r.stdout.splitlines():
            if line.strip().startswith("| 天干 |"):
                gan2 = [c.strip() for c in line.split("|")[2:6]]
            if line.strip().startswith("| 地支 |"):
                zhi2 = [c.strip() for c in line.split("|")[2:6]]
        gz2 = "".join(gc + zc for gc, zc in zip(gan2, zhi2))
        gz1 = calc.replace(" ", "")
        cross = "双引擎互证 ✅（bazi_skill 同盘）" if gz2 == gz1 else f"⚠️ bazi_skill 出 {gz2}"
        print(f"  互证：{cross}")
    except Exception as e:
        print(f"  互证：bazi_skill 未跑（{str(e)[:60]}）")

    # ---------- ② 六爻 ----------
    section('【② 六爻·大衍蓍草】（iching，seed=出生日期可复现）')
    import iching.iching as ic
    random.seed(date(y, m, d).toordinal())
    yao = ic.sixYao()
    dong = [i + 1 for i, v in enumerate(yao) if v in (6, 9)]
    print(f"  终身卦爻值（自下而上）：{yao}  {'静卦' if not dong else '动爻第' + '、'.join(map(str, dong)) + '爻'}")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ic.predict(date(y, m, d), date.today())
    out = buf.getvalue().splitlines()
    print(f"  流年卦：{out[0][:80] if out else ''}")

    # ---------- ③ 紫微斗数 ----------
    section('【③ 紫微斗数 · 含生年四化/大限】（py-iztro）')
    from py_iztro import Astro
    # 时辰 → time_index（0早子/1丑/2寅/3卯/4辰/5巳/6午/7未/8申/9酉/10戌/11亥/12晚子）
    hour2idx = lambda h: {0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 5,
                          11: 6, 12: 6, 13: 7, 14: 7, 15: 8, 16: 8, 17: 9, 18: 9, 19: 10,
                          20: 10, 21: 11, 22: 11, 23: 12}[h]
    ti = hour2idx(hh)
    r = Astro().by_solar(f"{y}-{m}-{d}", ti, g)
    print(f"  命主{r.soul} 身主{r.body}（命宫在{r.earthly_branch_of_soul_palace}宫，五行局:{r.five_elements_class}）")
    s4 = [(pl.name, s.name, s.mutagen) for pl in r.palaces for s in pl.major_stars + pl.minor_stars if s.mutagen]
    print(f"  生年四化：{'、'.join(f'{n}化{mut}（{pl}宫）' for pl, n, mut in s4) or '无'}")
    for pl in r.palaces:
        stars = "、".join(s.name + (s.brightness or "") for s in pl.major_stars) or "—"
        dl = pl.decadal
        print(f"  {pl.name}（{pl.earthly_branch}）：{stars}  [大限{dl.heavenly_stem}{dl.earthly_branch} {dl.range[0]}-{dl.range[1]}岁]" if dl else f"  {pl.name}（{pl.earthly_branch}）：{stars}")

    # ---------- ④ 奇门遁甲 ----------
    section('【④ 奇门遁甲·时家奇门】（qimendunjia/paipan，拆补法定局）')
    import paipan as qm
    YANG = {'冬至': (1, 7, 4), '小寒': (2, 8, 5), '大寒': (3, 9, 6), '立春': (8, 5, 2), '雨水': (9, 6, 3), '惊蛰': (1, 7, 4),
            '春分': (3, 9, 6), '清明': (4, 1, 7), '谷雨': (5, 2, 8), '立夏': (4, 1, 7), '小满': (5, 2, 8), '芒种': (6, 3, 9)}
    YIN = {'夏至': (9, 3, 6), '小暑': (8, 2, 5), '大暑': (7, 1, 4), '立秋': (2, 5, 8), '处暑': (1, 4, 7), '白露': (9, 3, 6),
           '秋分': (7, 1, 3), '寒露': (6, 9, 3), '霜降': (5, 8, 2), '立冬': (6, 9, 3), '小雪': (5, 8, 2), '大雪': (4, 7, 1)}
    ORDER = {g2 + z2: i for i, (g2, z2) in enumerate((GAN[i % 10] + ZHI[i % 12]) for i in range(60))}

    def dingju(rgz, jieqi):
        if jieqi in YANG:
            table, yang = YANG[jieqi], True
        elif jieqi in YIN:
            table, yang = YIN[jieqi], False
        else:
            return None, False
        n = ORDER[rgz]
        while n >= 0:
            if GAN[n % 10] in '甲己':
                break
            n -= 1
        yuan = {'子': 0, '午': 0, '卯': 0, '酉': 0, '寅': 1, '申': 1, '巳': 1, '亥': 1, '辰': 2, '戌': 2, '丑': 2, '未': 2}[ZHI[n % 12]]
        return table[yuan], yang

    gz = [ba.getYear(), ba.getMonth(), ba.getDay(), ba.getTime()]
    try:
        jieqi_name = p.getPrevJieQi().getName()
        if jieqi_name not in YANG and jieqi_name not in YIN:
            jieqi_name = '春分'
    except Exception:
        jieqi_name = '春分'
    jushu, yang = dingju(gz[2], jieqi_name)
    if jushu is None:
        print("  （无法定局）")
    else:
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                pan = qm.PaiPan(tuple(gz), yang, jushu)
            print(f"  （{gz[2]}日，{jieqi_name}，{'阳' if yang else '阴'}遁{jushu}局）")
            for gg in pan.pan:
                print(f"  {gg.name}: 地盘{'、'.join(x.name for x in gg.dipan)} | 天盘{'、'.join(x.name for x in gg.tianpan)} | 星{'、'.join(x.name for x in gg.jiuxing)} | 门{gg.renpan.name if gg.renpan else '-'} | 神{gg.shenpan.name if gg.shenpan else '-'}")
        except Exception as e:
            print(f"  （奇门排盘失败：{str(e)[:80]}——qimendunjia 库对部分盘有已知 bug，跳过）")

    # ---------- ⑤ 黄历 ----------
    section('【⑤ 黄历宜忌】（出生当日 + 今日）')
    lunar_day = Solar.fromYmdHms(y, m, d, 12, 0, 0).getLunar()
    print(f"  出生日（{a.solar} 农历{lunar_day.toString()}）")
    print(f"  宜：{'、'.join(lunar_day.getDayYi()[:10])}")
    print(f"  忌：{'、'.join(lunar_day.getDayJi()[:10])}")
    print(f"  冲煞：{lunar_day.getDayChongShengXiao()}  吉神：{'、'.join(lunar_day.getDayJiShen()[:6])}")
    today = Solar.fromYmdHms(date.today().year, date.today().month, date.today().day, 12, 0, 0).getLunar()
    print(f"  今日（{date.today()} 农历{today.toString()}）宜：{'、'.join(today.getDayYi()[:10])} | 忌：{'、'.join(today.getDayJi()[:10])} | 冲：{today.getDayChongShengXiao()}")

    # ---------- ⑥ 占星（可选） ----------
    if a.lat is not None and a.lon is not None:
        section('【⑥ 占星 · swisseph】（按输入时间作钟表时，UT=时间-8h）')
        import swisseph as swe
        FLAG = swe.FLG_SWIEPH | swe.FLG_SPEED
        PLANETS = [(swe.SUN, '太阳'), (swe.MOON, '月亮'), (swe.MERCURY, '水星'), (swe.VENUS, '金星'),
                   (swe.MARS, '火星'), (swe.JUPITER, '木星'), (swe.SATURN, '土星'),
                   (swe.URANUS, '天王'), (swe.NEPTUNE, '海王'), (swe.PLUTO, '冥王')]
        jd = swe.julday(y, m, d, hh + mm / 60.0 - 8.0)

        def sign(lon):
            return SIGNS[int(lon // 30) % 12]

        for pid, pname in PLANETS:
            pos, _ = swe.calc_ut(jd, pid, FLAG)
            deg = pos[0] % 360
            print(f"  {pname}{sign(deg)}{int(deg % 30)}°")
        cusps, ascmc = swe.houses_ex(jd, a.lat, a.lon, b'P')
        asc = ascmc[0] % 360
        print(f"  上升{sign(asc)}{int(asc % 30)}°{int((asc % 1) * 60)}′")
    else:
        print()
        print("（占星未排：请加 --lat 出生地纬度 --lon 出生地经度）")

    print()
    print("-" * 62)
    print("提示：以上为六术排盘数据；综合解读（强弱/调候/格局/形象四视角见 tuiyan.py；")
    print("气象、性情、应期解读需分析师完成）。命理属传统文化研究，不作决策依据。")


if __name__ == '__main__':
    main()
