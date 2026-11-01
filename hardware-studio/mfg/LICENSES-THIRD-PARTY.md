# mfg/ 第三方依赖与许可证

按 CONVENTIONS 第 5 条记录。顶层 `LICENSES-THIRD-PARTY.md` 由统筹汇总（本线只改自己的目录）。日期 2026-11-01。

| 名称 | 版本 | 许可证 | 用途 | 引入方式 |
|---|---|---|---|---|
| PyYAML | 6.0.3 | MIT | 读写价格缓存 | 公共依赖（顶层 requirements.txt） |
| pytest | 9.2.0 | MIT | 测试 | 公共依赖 |
| git | 系统自带 | GPL-2.0 | `jlcparts_import.py` 读取数据镜像 | **外部程序**，subprocess 调用 |
| KiCad `kicad-cli` | 9.0.9（Docker 镜像 `kicad/kicad:9.0`，sha256:e638b79b…）；系统里另装了 Ubuntu 源的 7.0.11（没有 erc/drc，不可用） | GPL-3.0-or-later | `kicad_check.py` 跑 ERC/DRC | **外部程序**，subprocess / docker 调用，不复制、不链接、不随库分发 |
| jlcparts 数据（yaqwsx/jlcparts gh-pages） | 提交 028c436，快照 2026-10-31 | 项目代码为 MIT（[LICENSE](https://github.com/yaqwsx/jlcparts/blob/master/LICENSE)）；数据本身来自 JLCPCB 元件库，数据的使用条款**待核实** | 读取 JLCPCB 阶梯价写进 `prices/jlcpcb-parts.yaml` | 只读数据文件，不包含其代码；本库只存 25 条价格 |
| 乐鑫 ESP Hardware Design Guidelines | 源码仓库提交 a727293（2026-10-26） | 文档 CC BY-SA 4.0，代码 Apache-2.0 | `esp32s3-min-system.md` 的内容来源 | 摘要和翻译（改编），该页按 CC BY-SA 4.0 发布并署名 |
