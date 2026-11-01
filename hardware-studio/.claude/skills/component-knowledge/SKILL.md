---
name: component-knowledge
description: 查询和维护 hardware-studio/knowledge/ 元器件知识库（ESP32-S3/C3/C6、SSD1306/ST7789/SSD1680-SSD1681 屏、电容触摸/按键/LIS3DH、蜂鸣器/MAX98357A、USB-C 受电/TP4056/DW01/LDO、Wi-Fi/BLE 功耗与天线）。Use when choosing components for a small electronic product, looking up a pin/voltage/current/timing/pitfall for one of these parts, comparing options in a category's selection.md, adding a new component page, or checking that every fact row in knowledge/ carries a source link, level and date (check_sources.py).
---

# 元器件知识库

知识库在 `hardware-studio/knowledge/`，每类一个目录（mcu、display、input、audio、power、wireless），
每个器件一页，每类一张 `selection.md`。所有事实行都带"链接 · 来源级别 · 查询日期"或"未查到/估算/待核实"标记。
写入任何事实前必须先读并遵守 `.claude/skills/research-method/SKILL.md`。

## 什么时候用

- 给新产品选型：先看对应类别的 `selection.md`（场景 → 推荐器件 → 价格区间 → 取舍），再点进器件页。
- 画原理图 / 写驱动：查器件页的"引脚要点""电压、电流""接口时序要点""易踩的坑"。
- 需要的器件不在库里：按下面"新增一个器件页"补，补完跑检查。

## 怎么查

1. 打开 `knowledge/README.md` 找类别和页面（README 也解释了级别 S / S（镜像）/ A / B / C 和三个标记的含义）。
2. 用 grep 定位具体参数（在 `hardware-studio/` 下运行），例如：
   ```bash
   cd hardware-studio
   grep -rn "strapping\|Strapping" knowledge/mcu/
   grep -rn "深睡" knowledge/
   grep -rln "MCP73831\|电量计" knowledge/ || echo "库里没有，按下面'新增一个器件页'补"
   ```
3. 读数时看最后一列：
   - 带"待核实"的行（大多数非乐鑫器件，因为数据手册是从第三方镜像读的；以及全部价格）在定稿 BOM、量产前要按链接回原厂核对；
   - "未查到"的行不能当成"没有这个参数"，要自己去原厂资料补；
   - 模组/模块参数和芯片参数分开写，不要混用（例如 ST7789 芯片电流不含背光）。
4. 价格只当量级参考：全部来自搜索摘要快照，下单前打开商品页看实时阶梯价。

## 怎么新增一个器件页

1. 放到对应类别目录，文件名用小写型号，如 `knowledge/input/bmi270.md`。
2. 按统一模板写（复制任意现有页面改）：
   一句话概述 → 关键参数表 → 引脚要点 → 电压、电流 → 接口时序要点 →（模组/模块参数，单独一节）→ 易踩的坑 → 来源列表。
3. 每个事实写成表格行，最后一列格式：
   `[文档名 版本 章节/表号](链接) · S · 2026-11-01`
   - 原厂文件但从非官方地址读到：级别写 `S（镜像）`，并加 `· 待核实`；在来源列表里写官方地址、镜像地址（固定到 commit）和 PDF 的 sha256 前缀。
   - 只有社区资料：`· C · 日期 · 待核实`。
   - 查不到：写"未查到（查过哪里、什么错误）"，仍附上尝试过的官方 URL。
   - 推算：写"估算"和公式/依据。
   - 易踩的坑也写成表格行，同样要有来源。
4. 价格写进该类 `selection.md`，只能用 B 级来源（立创/LCSC/JLCPCB 商品页）；查不到写"估算"并给依据。
5. 在 `knowledge/README.md` 的目录里加一行链接（README 用列表，不用表格）。
6. 不要凭记忆补数据；拿不准就"待核实"。

## 怎么检查结果

```bash
cd hardware-studio && . .venv/bin/activate
python knowledge/check_sources.py           # 全库；也可传文件或目录：python knowledge/check_sources.py knowledge/power/
python -m pytest knowledge/tests -q
```

- `check_sources.py` 扫描每个 Markdown 表格的数据行（跳过表头、分隔行、``` 代码块）。合格条件：同时有 http 链接、合法的 YYYY-MM-DD 日期、来源级别（`· S/A/B/C`），或者含"未查到/估算/待核实"之一。输出不合格行的 `文件:行号: 原因`，退出码 0 合格、1 有不合格行、2 路径不存在。
- pytest 包含一个故意缺来源的反例，并要求六类各有 ≥2 个器件页和 1 张 selection.md、全库检查通过。
- `check_sources.py` 是给**事实页**用的：拿它扫 `mfg/README.md`、许可证表这类说明性表格会报大量"不合格"，那是正常的，不要据此改说明表。
- 脚本只检查"有没有来源"，不检查"来源对不对"。新增内容后，随机抽几条打开链接核对数值，把核对结果写进你的报告。
