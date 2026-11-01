# cad/ 第三方依赖与许可证

按 CONVENTIONS 第 5 条记录。顶层 `LICENSES-THIRD-PARTY.md` 由统筹汇总（本线只改自己的目录）。
版本是 2026-11-01 在 `hardware-studio/.venv` 里 `pip show` 的结果。

| 名称 | 版本 | 许可证 | 用途 | 引入方式 |
|---|---|---|---|---|
| build123d | 0.13.0 | Apache-2.0 | 参数化 B-rep 建模、布尔运算、STEP/STL 导出 | 公共依赖（顶层 requirements.txt） |
| cadquery-ocp-novtk（OCP） | 8.0.1.1.0 | Apache-2.0（绑定本身）；内含 OpenCASCADE 技术库，许可证为 LGPL-2.1 附例外（**待核实**：按 OCCT 官方许可说明核对） | build123d 的几何内核 | build123d 的传递依赖，以动态库形式使用，本线未复制、未修改其代码 |
| numpy | 2.5.4 | BSD-3-Clause 等 | 数值计算 | 公共依赖 |
| matplotlib | 3.11.2 | Matplotlib License（PSF 风格） | 预览 PNG | 公共依赖 |
| trimesh | 5.2.0 | MIT | 网格、表面采样、射线求交（壁厚抽样） | 公共依赖 |
| rtree | 1.4.1 | MIT | trimesh 射线求交需要的空间索引 | **本线新增**（`cad/requirements.txt`） |
| scipy | 1.18.1 | BSD-3-Clause | trimesh 细分 / 采样的传递依赖 | 传递依赖 |
| PyYAML | 6.0.3 | MIT | 读外壳参数文件 | 公共依赖 |
| pillow | 13.0.0 | MIT-CMU | 测试中读取 PNG | 公共依赖 |
| pytest | 9.2.0 | MIT | 测试 | 公共依赖 |
| PrusaSlicer（命令行） | 2.7.2+dfsg-1build2（Ubuntu noble universe） | AGPL-3.0 | 切片检查 | **外部程序**，通过 `subprocess` 调用，不复制、不链接、不随库分发 |
