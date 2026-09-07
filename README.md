# mingli-tuiyan · 命理推演（六术排盘 + 四视角法）

结合陆致极《命运的求索——中国命理学简史及推演方法》的多视角推演框架，
把八字命理的推演方法做成**可复现、可验证**的开源算法工具：
**六术排盘**（八字双引擎/六爻/紫微/奇门/黄历/占星）+ **四视角推演**（强弱/调候/格局/形象）。

> ⚠️ 声明：本工具基于传统命理文献整理，属文化研究与算法演示用途。
> 命理不是科学，输出为概率性倾向描述，不构成任何决策依据（医疗/投资/婚恋等请咨询专业人士）。

## 功能总览

| 功能 | 脚本 | 说明 |
|------|------|------|
| 六术一键排盘 | `scripts/wushu_all.py` | 八字(双引擎互证)/六爻/紫微/奇门/黄历/占星 |
| 四视角推演 | `scripts/tuiyan.py` | 强弱评分/调候表/格局初判/五行形象 |
| 八字排盘库 | `scripts/bazipai.py` | 四柱/十神/藏干/大运 |
| 合婚/正缘方法 | `references/` | 方法论文档 |

## 安装

```bash
# 核心（四视角 + 八字排盘）
pip install -r requirements.txt

# 完整（六术全功能）
pip install -r requirements-full.txt
```

> ⚠️ `py-iztro`（紫微）声明 `pydantic==2.10.6`，`pip install py-iztro` 可能尝试降级你环境的 pydantic。
> 实测 pydantic 2.13.x 下 py-iztro 正常运行（仅 deprecation warning）。
> 若需避免降级：`pip install py-iztro --no-deps`（确保环境已有 pydantic>=2.0）。

## 用法

```bash
# ① 一键六术排盘（示例日期与经纬度均为虚构占位，请替换为实际出生时间/地点）
python scripts/wushu_all.py --solar 1990-06-15 --time 10:30 --gender 男 --lat 23.13 --lon 113.26

# ② 四视角推演（从出生时间自动排盘）
python scripts/tuiyan.py --solar 1990-06-15 --time 10:30 --gender 男

# ③ 四视角推演（已有四柱）
python scripts/tuiyan.py --bazi "庚午 壬午 辛亥 癸巳" --gender 男

# ④ 只排八字
python scripts/bazipai.py --solar 1990-06-15 --time 10:30 --gender 男
```

## 方法论

参考陆致极《命运的求索》第十一章「多视角的推演程式」：

1. **强弱分析**（扶抑）：日主得令/得地/得生/得势加权评分 → 身强/偏强/中和/偏弱/身弱
2. **调候分析**：按《穷通宝鉴》十干 × 十二月调候表，查当月最需要的五行/天干
3. **格局分析**：月令取格（正格八格初判 + 透干参考）
4. **形象分析**：五行分布、流通方向、缺失/偏枯（脚本输出数据，解读由分析师完成）

叠加**大运流年**形成完整推演。算法层输出可复现分数与查表结果，解读层（分析师）负责综合与人生对照。

## 目录

```text
mingli-tuiyan/
├── README.md
├── SKILL.md                      # Agent 技能说明（方法论+纪律）
├── requirements.txt              # 核心依赖
├── requirements-full.txt         # 完整依赖（六术）
├── scripts/
│   ├── wushu_all.py              # 六术一键排盘
│   ├── tuiyan.py                 # 四视角推演
│   ├── bazipai.py                # 八字排盘库
│   ├── tiaohou_table.py          # 穷通宝鉴调候表
│   └── bazi_skill_pai_pan.py     # 八字排盘第二引擎（零依赖）
└── references/
    ├── hehun-method.md           # 合婚推演方法
    ├── third-party-verification.md # 第三方报告核对流程
    └── zhengyuan-portrait.md     # 正缘画像模板
```

## 方法论来源与边界

- 排盘口径：真太阳时建议自行换算；节气以天文历为准（lunar-python）
- 占星口径：按输入时间作钟表时排（UT=时间-8h），需出生地经纬度
- 强弱评分：扶抑派主流权重，阈值可调（见 tuiyan.py 常量）
- 调候表：以《穷通宝鉴》通行本整理，各版本口诀存在差异，仅供参考
- 格局初判：月令本气取格 + 透干辅助；变格（专旺/从格等）需人工判断
- 奇门：qimendunjia 库对部分盘存在已知 bug，脚本已容错跳过
- 形象/综合/合婚解读：超出纯算法范围，需分析师结合理论库完成

## License

MIT
