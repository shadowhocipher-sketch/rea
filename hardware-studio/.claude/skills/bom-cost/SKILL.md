---
name: bom-cost
description: 写 BOM、查元器件和加工价格、算多数量档成本、选量产路线（开发板/模组加底板/芯片整板）时使用。Use when building a bill of materials, looking up LCSC/JLCPCB prices into the price cache, running mfg/cost.py for quantities like 10/100/1000, checking how much of a cost estimate is backed by real quotes, running KiCad ERC/DRC, or deciding a production route for a small electronic product in this library.
---

# BOM 与成本

工具和格式都在 `hardware-studio/mfg/`。先读 `mfg/README.md`（BOM 和价格缓存格式），查价按 `mfg/pricing.md`，来源规则按 `.claude/skills/research-method/SKILL.md`。

## 什么时候用

- 要回答"做 N 台要多少钱""单台成本多少""哪一项最贵"；
- 要比较开发板直接装 / 模组加底板 / 芯片整板（看 `mfg/production-routes.md`）；
- 要画 ESP32-S3 板子（看 `mfg/esp32s3-min-system.md` 的自检清单）；
- 画完 KiCad 工程要跑 ERC/DRC。

## 1. 写 BOM

- 放在 `products/<产品名>/bom.csv`，列定义见 `mfg/README.md` 第 2 节。不要把具体产品的 BOM 放进 `mfg/`。
- 五类都要写全：电子件、结构件（外壳按克或按件）、外购模块（屏幕模块、电池）、包装、加工费（PCB、贴片工程费、钢网、焊点费、换料费、组装人工）。漏掉加工费和包装是最常见的低估原因。
- 电子件填立创编号（`lcsc` 列），工具会自动用 `lcsc:<编号>` 查价；非元件填 `price_key`。
- 一次性费用用 `cost_mode: batch`；焊点费用 `per_joint`；扩展料换料费用 `per_extended_type`。
- 暂时不装的写 `dnp: y`，不要删行。
- 接线表 `products/<产品名>/pins.csv`（CONVENTIONS.md）里出现的每个零件，BOM 里都应该有对应行。

## 2. 查价并入缓存

1. 先看 `mfg/prices/` 里有没有（`grep -r C82942 mfg/prices`）。
2. 没有就按 `mfg/pricing.md` 的顺序查：立创商城 / JLCPCB → LCSC → DigiKey/Mouser。记全部数量档、链接、日期。
3. 打不开分销商网站时：用 `mfg/jlcparts_import.py` 从 jlcparts 镜像导出（`pricing.md` 第 3 节），镜像里没有的用搜索摘要记成 `unverified`。
4. 实在没有 B 级价格：写 `status: estimate`，basis 写依据和公式；或者干脆不写，让工具报"缺价格"。**不要凭记忆写价格。**
5. 写完跑 `python mfg/cost.py --check-prices`。

## 3. 跑成本

```bash
. .venv/bin/activate
python mfg/cost.py products/<产品名>/bom.csv --qty 10 100 1000 --out products/<产品名>/cost
```

- 默认损耗 2%（`--attrition`），按行可覆盖；加工费不计损耗。
- 混用人民币和美元时必须给 `--fx CNY=<汇率>`，并在报告里写汇率来源和日期。
- 要求"不能有缺价格"时加 `--strict`（缺价格退出码 3）。

## 4. 检查结果（交付前必做）

打开 `cost.md`：

- [ ] **缺价格行 = 0**，或者在报告里列出缺哪些、为什么；
- [ ] 看"实查 / 待核实 / 估算"三列。实查占比低时，在结论里写明"这是估算"，并列出金额最大的几项待核实/估算项，建议先核实它们；
- [ ] 明细里每行都有来源链接和日期（估算行有依据，在价格缓存的 basis 里）；
- [ ] 采购量明显大于需求量的行（MOQ 或多买到下一档），看一下 `leftover` 是否合理；
- [ ] 警告里的"焊点数未知"行，补 `joints` 列或接受低估；
- [ ] 一次性费用在小数量档占比很高时，说明分摊方式；
- [ ] 报价相关的结论都带日期（价格会变）。

## 5. KiCad 检查

```bash
python mfg/kicad_check.py products/<产品名>/kicad/ --out products/<产品名>/kicad-report
# 本机只有 KiCad 7 或没有 KiCad 时：
python mfg/kicad_check.py products/<产品名>/kicad/ --docker kicad/kicad:9.0
```

需要 KiCad 8+（7.x 的 `kicad-cli` 没有 erc/drc）。找不到时脚本会打印安装方法并返回 4。有错误级违规返回 1；`--fail-on warning` 让警告也算失败。KiCad 是 GPL，只当外部程序调用。

## 6. 选路线

按 `mfg/production-routes.md` 第 3 节的公式，用 `cost.py` 在同一组数量档上分别算各路线的 BOM，再结合认证（`compliance/`）、尺寸、功耗、供应链判断。路线比较的结论如果依赖待核实价格，要明说。
