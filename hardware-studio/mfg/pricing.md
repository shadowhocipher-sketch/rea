# 价格查询固定流程

按 `.claude/skills/research-method/SKILL.md` 执行：价格只来自 B 级来源（立创商城、JLCPCB、LCSC、DigiKey、Mouser），每条记链接、日期、所有数量档；查不到写"估算"和依据；**绝不编造价格**。

## 1. 查询顺序

1. **立创商城 / JLCPCB 元件库**（人民币或美元，贴片用料以 JLCPCB 为准）
   - 立创商城：`https://item.szlcsc.com/<数字>.html`，或在 <https://so.szlcsc.com/global.html?k=型号> 搜索；
   - JLCPCB 元件库：`https://jlcpcb.com/partdetail/<立创编号>`（例如 `https://jlcpcb.com/partdetail/C725790`），
     页面会写 Basic / Extended / Preferred，这决定贴片时有没有换料费。
2. **LCSC**（立创国际站，美元）：`https://www.lcsc.com/product-detail/<立创编号>.html`。
3. 以上都没有，再看 DigiKey / Mouser（B 级）。
4. 仍然没有 → 不写价格，或者写**估算**：给出依据和公式（例如"同尺寸裸屏 C18723026 的价格 × 1.5，系数是假设"）。
5. 淘宝、AliExpress、卖家页面、博客、搜索引擎摘要都不是价格来源。模块类（屏幕模块、传感器模块）往往只在这些地方有，只能作为**估算**的线索，并注明"不同卖家可能不同"。

## 2. 每条价格记录什么

写进 `mfg/prices/*.yaml`，字段见 `mfg/README.md` 第 3 节：

- 立创编号、厂商型号、厂商、封装；
- **全部数量档**（breaks）和币种，不只记一档；
- 链接（source_url）、查询日期（date）、来源级别（level: B）；
- 取得方式（access）：`direct` 直接打开商品页、`mirror` 经数据镜像、`search-snippet` 只有搜索摘要；
- 状态（status）：`quote` 实查 / `unverified` 待核实 / `estimate` 估算；待核实和估算必须写 basis。

状态怎么定：

| 情况 | status |
|---|---|
| 打开了商品页，或拿到带日期的完整阶梯价数据（例如 jlcparts 镜像，记下快照日期） | `quote` |
| 只看到搜索摘要，或者几个来源的数字互相矛盾 | `unverified`，basis 写清楚矛盾点和取值理由 |
| 没有 B 级价格，靠推算或假设 | `estimate`，basis 写依据和公式 |

## 3. 打不开分销商网站时

本库第一次建缓存时（2026-11-01）就遇到了：云端会话访问 `www.lcsc.com`、`jlcpcb.com`、`szlcsc.com` 全部被代理拦截（`CONNECT tunnel failed, response 403`；WebFetch 报 `getaddrinfo ENOTFOUND`）。当时的做法：

1. 记下被拦截的 URL 和错误；
2. 用 GitHub 上的 [yaqwsx/jlcparts](https://github.com/yaqwsx/jlcparts) 数据（每天从 JLCPCB 元件库导出，gh-pages 分支），用 `mfg/jlcparts_import.py` 按立创编号取阶梯价：

   ```bash
   git clone --depth 1 --filter=blob:none --no-checkout -b gh-pages \
       https://github.com/yaqwsx/jlcparts.git /tmp/jlcparts      # 只拉目录树，几 MB
   python mfg/jlcparts_import.py --repo /tmp/jlcparts C725790 C82942 > new.yaml
   ```

   生成的条目 `status: quote`、`access: mirror`，带镜像提交号和快照日期。镜像不全：本次 C1600000–C6299999 区间的编号（包括 ESP32-S3-WROOM-1-N16R8 C2913202、ESP32-C3-MINI-1-N4 C2838502）都不在里面。
   不要对这个仓库跑 `git ls-tree -l`，会触发几百 MB 的下载。
3. 镜像里没有的，用搜索（WebSearch）找该商品页的摘要，记为 `unverified`；
4. 都没有，写"未查到"或估算。

## 4. PCB、贴片、3D 打印、组装、包装

这些不是元件，没有阶梯价表，按计价规则记：

| 项目 | 官方页面 | 怎么记 |
|---|---|---|
| PCB 打样/批量 | <https://jlcpcb.com/quote>（计价器）、JLCPCB 博客价格表 | 按片记单价；批量价从计价器取不同数量的报价，各记一档 |
| 贴片工程费、钢网 | <https://jlcpcb.com/help/article/pcb-assembly-faqs>、<https://jlcpcb.com/help/article/pcb-assembly-price> | BOM 里 `cost_mode: batch` |
| 焊点费 | 同上 | `cost_mode: per_joint`，焊点数取价格缓存的 joints 或 BOM 的 joints 列 |
| 扩展库换料费 | 同上 | `cost_mode: per_extended_type`，自动数 jlc_class 为 Extended 的料 |
| 3D 打印 | <https://jlc3dp.com/>（计价器）、JLC3DP 调价公告 | 按克或按件；用 B 线（`cad/`）导出的模型体积/质量算用量 |
| 组装人工、包装 | 找加工厂/包装厂报价 | 拿到报价前只能 `estimate`，写明假设 |

计价规则经常改，而且不同页面会互相矛盾（例如本次贴片工程费一处写 $8、一处写 $25），一律记最新日期的那个，矛盾写进 basis，标 `unverified`，下单前用计价器复核。

## 5. 入缓存后检查

```bash
python mfg/cost.py --check-prices            # 缺链接/日期/依据、重复 key 都会报错
pytest mfg/tests                             # 包含对仓库价格缓存的检查
```

## 6. 本次（2026-11-01）建库结果

| 类别 | 条目 | 状态 |
|---|---|---|
| 无线模组 | ESP32-S3-MINI-1U-N4R2（C22356044）、ESP32-C3-MINI-1-H4X（C41349510） | 实查（镜像） |
| 无线模组 | ESP32-S3-WROOM-1-N16R8（C2913202）、ESP32-C3-MINI-1-N4（C2838502） | 待核实（搜索摘要） |
| 开发板 | LCKFB-ESP32S3R8N8（C20626143） | 实查（镜像） |
| 屏幕 | 0.96 寸 128x64 裸屏 X096-2864KSWPG01-H30（C18723026，商品描述写驱动 SSD1315） | 实查（镜像） |
| 屏幕模块 | 0.96 寸 OLED 模块（带转接板） | 估算（裸屏价 × 1.5，系数为假设） |
| 充电 | TP4056（UMW C725790；TOPPOWER TP4056-42-ESOP8 C16581） | 实查（镜像） |
| 保护 | DW01A（PUOLOP C351410；HL C18164398）、FS8205A（C908265）、8205A（UMW C351449） | 实查（镜像） |
| LDO | ME6211C33M5G-N（C82942）、XC6206P332MR-G（C5446）、AP2112K-3.3TRG1（C51118）、AMS1117-3.3（C6186） | 实查（镜像） |
| USB-C 16P | TYPE-C-31-M-12（C165948）、TYPE-C16PIN（C393939） | 实查（镜像） |
| 加速度计 | LIS3DHTR（C15134） | 实查（镜像） |
| 阻容按键 | 0402 10k/5.1k/1k、0402 100nF/1uF、0603 10uF、0805 22uF、TS-1187A 轻触开关 | 实查（镜像） |
| 加工费 | JLCPCB 贴片工程费、钢网、焊点费、扩展料换料费、2 层板打样；JLC3DP MJF PA12 每克价 | 待核实（搜索摘要，页面数字有冲突） |
| 人工、包装 | 组装人工、基础包装 | 估算（假设值） |

2026-11-01 answer-box 迁移测试补充（jlcparts 镜像里都没有，商品页打不开）：

| 类别 | 条目 | 状态 |
|---|---|---|
| 屏幕模块 | Waveshare 1.54 寸 e-Paper 模块（C5374685） | 待核实（搜索摘要，摘要显示缺货） |
| 电芯 | 402030 锂聚合物 200 mAh（`est:lipo-402030-200mah`） | 估算（只有 C 级零售价；立创/LCSC 搜索未返回电芯商品页） |
