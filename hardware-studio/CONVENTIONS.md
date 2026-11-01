# 能力库公共约定

所有工作线、以后所有使用这个库的会话都遵守这些约定。

## 1. 目录和归属

| 目录 | 归属工作线 | 内容 |
|---|---|---|
| `knowledge/` | A | 元器件与模块知识库 |
| `cad/` | B | build123d 参数化模块、测量/导出/切片工具、DFM 规则 |
| `firmware/`、`sim/` | C | 固件模板、屏幕模拟器 |
| `mfg/` | D | BOM 结构、成本工具、量产路线、最小系统参考设计要点 |
| `compliance/` | E | 合规地图 |
| `render/`、`diagrams/` | F | 产品渲染、接线图生成 |
| `.claude/skills/research-method/` | G | 研究方法 |
| `.claude/skills/`、`evals/` | H | 各线 skill、总流程 skill、自测 |
| `products/<产品名>/` | 使用者 | 某个具体产品的实例数据和产出（例如迁移测试）|
| `inputs/` | 用户 | 用户提供的案例材料，只读 |

一条工作线只改自己的目录和自己的 skill。需要别的线配合时，写进自己的报告，由统筹处理。

## 2. 通用，不写死

通用模块、工具和模板里不出现任何具体产品的尺寸、引脚、型号组合。
具体产品的数据放在 `products/<产品名>/` 下，以参数文件或配置文件的形式传进通用工具。

### 产品实例数据 `products/<产品名>/`

各工作线的工具都从这里读取具体产品的数据。共用格式：

- `pins.csv`（接线表，C/D/F 共用）：

  ```csv
  from_part,from_pin,to_part,to_pin,net,kind,note
  MCU,GPIO8,OLED,SDA,I2C_SDA,signal,
  MCU,3V3,OLED,VCC,+3V3,power,
  MCU,GND,OLED,GND,GND,ground,
  ```

  `kind` 取 `power` / `ground` / `signal`。每一行是一根线。
- BOM 的格式由 D 线在 `mfg/README.md` 里定义；外壳参数的格式由 B 线在 `cad/README.md` 里定义。

## 3. 事实和来源

按 `.claude/skills/research-method/SKILL.md` 执行。简单说：

- 每条参数、价格、法规都附来源链接和查询日期（YYYY-MM-DD）；
- 查不到写"未查到"；推算写"估算"并写依据；拿不准写"待核实"；
- 不凭记忆补数据。

## 4. 运行环境

```bash
cd hardware-studio
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest                      # 全部测试
python evals/run.py         # 自测打分
```

每条线把自己的依赖写进各自目录下的 `requirements.txt`，顶层 `requirements.txt` 用 `-r` 引用。
外部命令行工具（KiCad、切片软件、渲染器）在 skill 里写清安装方法；装不上时工具要给出明确提示，而不是崩溃。

## 5. 许可证

- 可复用的固件和工具里**不放任何 GPL/LGPL/AGPL 代码**，也不写依赖 GPL 库 API 的派生代码。
- 可以作为**外部命令行程序**调用 GPL 软件（例如 KiCad、PrusaSlicer），但不复制它们的代码，也不随库分发它们。
- Blender 官方认为使用 bpy API 的脚本属于派生作品，按 GPL 处理，所以可复用的渲染工具不用 bpy。
- 引入任何第三方代码或库，都把名称、版本、许可证、用途写进 `LICENSES-THIRD-PARTY.md`。

## 6. 图片

- 渲染图文件名以 `render_` 开头，图上标"渲染图 / Render"字样。
- 模拟器输出图的文件名以 `sim_` 开头，图上标"模拟 / Simulated"。
- 不把渲染图或模拟图冒充实拍。

## 7. 不写入的内容

个人信息、雇主信息、账号、密码、API 密钥。

## 8. 完成的标准

每条线都要有可以自动运行的检查（pytest 或检查脚本），而且实际运行通过。
同一个问题连续修 3 次还不通过，就停下来记录到报告里。
