---
name: mingli-tuiyan
description: 八字命理全功能开源版（陆致极《命运的求索》方法论）——六术排盘（八字双引擎/六爻/紫微/奇门/黄历/占星）+ 四视角推演（强弱/调候/格局/形象）+ 合婚方法。纯通用算法、不含任何个人信息，任何人可输入自己的出生信息使用。
category: consultation
---

# 命理推演 · 全功能开源版（六术排盘 + 四视角推演）

结合陆致极《命运的求索——中国命理学简史及推演方法》的多视角推演框架，
把命理中可复现的部分做成算法：**六术排盘**（八字双引擎/六爻/紫微/奇门/黄历/占星）
+ **四视角推演**（强弱/调候/格局/形象）。全程不内置任何个人命盘数据，纯参数输入。

## 启用条件

用户提到：推演八字、看强弱/调候/格局、用陆致极方法、喜用神判断、四视角分析、排盘、六爻、紫微、奇门、黄历、占星、合婚。

## 使用流程

```bash
# 1) 一键六术排盘（八字双引擎互证/六爻/紫微/奇门/黄历/占星）
#    （示例日期与经纬度均为虚构占位，请替换为实际出生时间/地点；占星需出生地经纬度）
python scripts/wushu_all.py --solar 1990-06-15 --time 10:30 --gender 男 --lat 23.13 --lon 113.26

# 2) 四视角推演：从出生时间自动排盘
python scripts/tuiyan.py --solar 1990-06-15 --time 10:30 --gender 男

# 3) 四视角推演：已有四柱直接推
python scripts/tuiyan.py --bazi "庚午 壬午 辛亥 癸巳" --gender 男

# 4) 只排八字（四柱/十神/藏干/大运）
python scripts/bazipai.py --solar 1990-06-15 --time 10:30 --gender 男
```

## 安装

```bash
# 核心（四视角+八字排盘）：只装 lunar-python
pip install -r requirements.txt

# 完整（六术全功能）：见 requirements-full.txt（⚠️ py-iztro 会尝试锁定 pydantic==2.10.6，
# 实测 2.13.x 可用；若 pip 强制降级请用 pip install py-iztro --no-deps）
pip install -r requirements-full.txt
```

## 六术排盘说明（scripts/wushu_all.py）

| # | 术 | 库 | 说明 |
|---|----|----|------|
| ① | 八字 | lunar-python + bazi_skill | 双引擎独立实现互证 |
| ② | 六爻 | iching | 大衍蓍草，seed=出生日期可复现 |
| ③ | 紫微 | py-iztro | 十二宫+生年四化+大限 |
| ④ | 奇门 | qimendunjia | 拆补法定局（部分盘有库 bug，已容错跳过） |
| ⑤ | 黄历 | lunar-python | 出生日+今日宜忌 |
| ⑥ | 占星 | pyswisseph | 行星落座+上升（需经纬度，按钟表时 UT-8h） |

## 四视角推演说明（scripts/tuiyan.py）

| 视角 | 算法 | 输出 |
|------|------|------|
| ① 强弱 | 得令(旺/相/休/囚/死 ±3/2/-3/-1/-4) + 得地(禄+3、同五行藏干根 2/1/0.5) + 得生(印封顶2.0) + 得势(天干印比±、财官食伤-) | 总分 → 身强/偏强/中和/偏弱/身弱 + 喜用方向 |
| ② 调候 | 查 `tiaohou_table.py`（穷通宝鉴 10干×12月）→ 对照命局已现/未现 | 当月主用神清单 |
| ③ 格局 | 月支本气十神 → 正格八格初判 + 透干参考 | 初判格局名 |
| ④ 形象 | 干支+藏干五行计数 → 最旺/最弱/缺 | 五行分布数据 |

权重常量集中在 `tuiyan.py` 顶部，可调。

## 铁律

1. **通用性**——本技能是开源通用版，代码和数据文件**不得写入任何个人命盘/个人信息**（含分析对象真实盘）。个人数据留在别处，需要时以参数喂入。
2. **纯算模式**——脚本只输出可复现的算法初判；**综合解读（气象/性情/大运应期/六亲/合盘）不自动生成**，需分析师完成并标注依据。
3. **口径透明**——排盘按输入时间直排；真太阳时需使用者自行换算；调候表注明"通行本整理、版本有差异"；占星按钟表时排。
4. **D级红线**——命理一律作概率性倾向参考，不作决策依据（关系/投资/健康判断不进决策层）。
5. **可证伪**——涉及应期的解读要登记"预测+验证条件"，到期验证，不做无法证伪的空预测。

## 文件

```text
README.md                         项目说明（安装/用法/方法论/边界）
SKILL.md                          本技能定义
requirements.txt                  核心依赖（lunar-python）
requirements-full.txt             完整依赖（六术）
scripts/wushu_all.py              六术一键排盘（八字双引擎/六爻/紫微/奇门/黄历/占星）
scripts/tuiyan.py                 四视角推演（强弱+调候+格局+形象）
scripts/bazipai.py                八字排盘库（四柱/十神/藏干/大运）
scripts/tiaohou_table.py          穷通宝鉴调候表（独立数据文件，可校对修改）
scripts/bazi_skill_pai_pan.py     八字排盘第二引擎（零依赖纯算法）
references/hehun-method.md        合婚推演方法（干支互动视角）
references/third-party-verification.md  第三方报告核对流程
references/zhengyuan-portrait.md  正缘画像分析模板
```

> 注意：八字排盘库文件名为 bazipai.py 而非 paipan.py——避免遮蔽奇门库 `qimendunjia` 暴露的顶层模块 `paipan`（import paipan 冲突）。
