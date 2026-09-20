# 论文写作系统交接文档

**最后更新**：2026-09-20
**一句话状态**：格式、数据、表格就绪；3.1 正文与图 2、图 3 已提交；3.2 核心命题已定、数字已核、正文未写；工作区有两张图的未提交重绘。

本文件是入口，不重复维护数字。状态看 `plan/progress.md`，论点看 `plan/claims.md`，节→数据→图表看 `plan/results-map.md`，验证看 `verification/verification-report.md`。

---

## 一、这是一个写作系统：角色、流程、边界

### 角色

- **用户 = 作者**。定论点、定每节核心命题和段落骨架、定图的设计与可读性标准、核最终文字。所有"要不要"的决定归用户。
- **AI = 执行与核查**。从 csv 现算并核对数字、出草稿、写绘图脚本、排版编译、维护 `plan/` 文档与 git。发现数据或逻辑问题要报告，不擅自改口径、不替用户做设计决定。

### 一段正文的流程

1. 用户给出该节核心命题或骨架（3.2 的核心已写在 `sections/04_results.tex` 的 % 注释里）
2. AI 从 `results/summary/` 现算全部要用的数字，连口径一起写进该节 .tex 的 % 注释
3. 出草稿（AI 写、用户核；或用户写、AI 核数）。每段：论点 → 支撑数字 → 收回论点或引出下一段
4. `latexmk -xelatex` 编译，导出页面 PNG，用户看的是**渲染页**，不是 .tex
5. 用户改或认可 → 提交（中文提交信息，写清改了什么、为什么）
6. 同步 `plan/claims.md` 状态、`plan/results-map.md` 正文状态、`plan/progress.md`

### 一张图的流程

1. 先定图要支撑的论点，再定图型；图型能否把数字放清楚**先算再画**（图 2 教训：8 cm 单栏 12 根竖柱最宽 0.59 cm，两位小数最窄 0.49 cm，必挤；改横向条形后每数一行）
2. 脚本 `scripts/plot_*.py`，`import figstyle`，从仓库根目录运行，输出 `figures/results/*.png` + `.pdf`
3. 插入 .tex（单栏 `figure` / 通栏 `figure*`，`[tbp]`），编译，导出页面给用户看
4. 用户认可后提交；更新 `figures/data-manifest.md`、`plan/claims.md` S5、`plan/results-map.md`

### 边界（不做的事）

- 正文数字只从 `results/summary/` 现算，每个数字能回溯到 csv 和脚本。不从记忆、不从旧稿、不从 `legacy/` 中转表拿数
- 不改 `results/`、`tables/` 口径；口径变动必须走脚本，并在 `plan/claims.md` 数据处理链记录
- 旧 Word 稿（`legacy/manuscript/`）只作格式与文风参考，内容不迁移
- 图的设计（图型、子图排布、配色、字号、窗口）变了要用户认可；可读性优先于工程可行，不为省事缩字号、竖排数字
- 浮动体不用 `[h]`/`[H]`；写作阶段只要求同节内图表顺序合理，定稿再调位置
- 不 push。`origin/master` 落后本地 7 个提交，push 由用户决定
- 提交前 `git status` 看清，只提交本步相关文件；用户说"先别画其它"就把其它图的改动留在工作区
- 不写空壳句和翻译腔（`plan/style-guide.md` 禁用表）；不白描数字

### 真相来源分层

1. 科学数字：`results/summary/*.csv`（可由脚本从原始输出重建，处理链见 `plan/claims.md` S1–S5）
2. 实验协议：`plan/experiment-protocol.md`
3. 论点与状态：`plan/claims.md`（C1–C8）、`plan/results-map.md`、`plan/progress.md`
4. 写作规则：`plan/style-guide.md`
5. 格式：`plan/format-spec.md`（**测绘通报模板**为准；图尺寸、配色标准也在这里）
6. 正文：`sections/*.tex`；`main.tex` 只管格式
7. 文献：`bibliography/references.bib`（Zotero 同步 71 条）

---

## 二、当前状态（2026-09-20）

### 章节

| 节 | 文件 | 状态 |
|---|---|---|
| 引言 | `01_introduction.tex` | 未写；evidence-map E1–E5 在 `plan/review/` |
| 1 数据 | `02_data.tex` | 有稿，研究区图已插入；未按 09-19/09-20 写作要求复核 |
| 2.1 三模型 | `03_methods.tex` | 待重写（模型结构图待提取） |
| 2.2 实验设计、2.3 指标、2.4 环境 | `03_methods.tex` | 已按代码核对；公式角标中文、逐条编号 |
| 3.1 站内 | `04_results.tex` | 已写（用户草稿，数字全部核对）；图 2、图 3 已插入 |
| 3.2.1 跨站 F1、3.2.2 泛化退化 | `04_results.tex` | **未写**。核心命题、全部数字及口径已在 % 注释 |
| 3.3.1 源—目标退化差异 | `04_results.tex` | 未写；热力图已有；要点见 claims C7 |
| 3.3.2 退化与空间特征 | `04_results.tex` | 数据未定位（站点级景观指标；图块级四张表） |
| 结论、摘要、题目 | `06_conclusion.tex` 等 | 未写 |

### 图表

| 图/表 | 文件 | 规格 | 状态 |
|---|---|---|---|
| 图 2 站内 F1 | `fig_within_site_f1` | 单栏 8×12 cm，横向条形，(a) 玉米 (b) 大豆 | 已提交 469882d；横向版**用户尚未明确反馈** |
| 图 3 D 站分类结果 | `fig_within_site_map_D` | 通栏 16×8 cm，上全站下局部，窗口 (13,8) 2×2 | 已提交；工作区有新 figstyle 重绘版未提交 |
| 热力图 | `fig_degradation_heatmap` | 通栏 16×12 cm，2×3 | 已提交旧版；脚本改六图等大+独立色标，未提交、未经用户看 |
| 研究区图 | `figures/study_area/` | — | 已插入 02_data.tex |
| 模型结构图 | `figures/models/` | — | 待提取 |
| 表 | `tables/table1,1b,2,3.csv` | — | csv 就绪；正文尚无表；3.2 是否配表待定 |

### 未提交工作区

```
M scripts/plot_degradation_heatmap.py      六图等大：cbar=False + fig.colorbar(ax=axes)；layout='constrained'；fig.supxlabel
M figures/results/fig_degradation_heatmap.{png,pdf}
M figures/results/fig_within_site_map_D.{png,pdf}   新 figstyle（刻度 6.5 pt、Arial 数字）重绘产物
```

用户指示"先别画其它"。处理顺序：图 2 定稿 → 重跑两脚本 → 编译看页 → 用户认可 → 提交，并更新 `figures/results/README_heatmap.md`、`figures/data-manifest.md` 里热力图"最右列带色标"的描述。

### 待用户决定

1. 图 2 横向条形版是否接受
2. 3.2 由 AI 按核心命题出草稿，还是用户自写 AI 核数（用户给了核心命题，尚未说明）
3. 3.2 是否配表（`table2` 内容：模型 × 作物，跨站 F1 与 ΔF1 的 12 路径 mean±std）
4. 3.2.2 "退化随迁移路径变化"讲到什么深度；与 3.3.1 热力图（逐路径）怎么分工
5. 36 路径明细是否进正文或补充材料
6. 题目、摘要；是否 push

---

## 三、下一步（按顺序）

1. 收图 2 反馈；重绘图 3、热力图；提交
2. 写 3.2.1、3.2.2。核心（用户原话）：**站内较高的作物分类精度在跨站后能否保持，以及泛化退化如何随模型、作物和迁移路径变化**。数字在 `04_results.tex` 注释，均已核对
3. 写 3.3.1（热力图 + claims C7）
4. 定位 3.3.2 数据；建立处理链后再写
5. 重写 2.1；提取模型结构图
6. 引言、结论、摘要、题目
7. 内容冻结后 LaTeX → Word

---

## 四、写作规则速查

**定位**：普通中文核心期刊（测绘通报）短文。通俗但精确。术语中文：站内、跨站、泛化退化、五次预测、汇总混淆矩阵、迁移路径、源站、目标站；保留英文的只有模型名（U-TAE、3D U-Net、ConvGRU）、HLS、CDL、F1、OA、软件名。

**严谨（用户 2026-09-20）**：
- 主语写全："三种模型的跨站玉米F1均值"，不说"精度""结果""它"
- 数字带口径：12 条路径均值 / 5 次预测标准差 / 站内汇总
- 每个数字后面跟它说明什么；不为论点服务的数字删掉或进表
- 比较说清对象与方向："U-TAE比ConvGRU高1.66个百分点"
- 结论限定：本文四站、不微调、F1 口径
- 为论点服务，不白描

**段落**：段首引图表 + 总判断 → 逐模型/逐作物数字 → 段尾解释或引出下一段。确定归因"这是由于"，推测"这可能与……有关"。

**数字格式**：百分数两位小数；差值用"个百分点"；范围用 ～；"玉米F1""大豆F1"直接写。

**公式**：角标中文、定语在前（$F1_{\text{站内玉米}}$）；一个 equation 一个公式一个编号。

**图**（`scripts/figstyle.py`、`plan/format-spec.md`）：
- 4 cm 模数：单栏 8 cm、通栏 16 cm；高 8 / 12 / 16 cm
- 模型色 ConvGRU 紫 `#7B3FA0`、3D U-Net 青 `#1B9E9E`、U-TAE 橘 `#E8731A`；地物色玉米黄 `#F2C14E`、大豆绿 `#4C9F70`、其它灰 `#BDBDBD`
- 图内文字 8 pt、子图题 8.5、刻度 6.5、数值 6.5；数字字母 Times New Roman，中文黑体
- 子图题"（a）……"在子图下、写全对象；图例在整幅底部；单栏多子图上下排
- 数值横排两位小数；放不下换图型，不缩字号、不竖排
- 图题只在 caption；图内不放图名、不放英文

**表**：三线表；表题在上，黑体小五；列名中文。

---

## 五、环境与操作要点

- Windows 10，PowerShell 5.1：无 heredoc、无 `&&`。多行提交信息用 Bash 工具 `git commit -F - <<'EOF'`
- 脚本相对路径以仓库根为准，在 `D:\AI\lunwen` 下 `python scripts/xxx.py`；绘图脚本自带 `sys.path` 加 `scripts/` 以 import figstyle
- 编译：`latexmk -xelatex -synctex=1 -interaction=nonstopmode -file-line-error main.tex`；页面预览用 `pymupdf` 导出 PNG 再 Read
- matplotlib 3.9.2：字体回退只认 `font.family` 列表，`font.sans-serif` 列表不回退。本机有 Arial、SimHei、Bahnschrift，无 Arial Narrow
- 原始数据：站内 `D:/20{site}/2023…results/summary/metrics_summary.csv`（未入库，iw/iw2 目录名顺序不同）；跨站 `legacy/experiment-results/cross_site_all_20260916/`（git 排除）；D 站分类图需 `D:/20il/2023{model}ilresults/summary/maps/*.tif`
- 一键重建数据与表：`scripts/run_all_updates.ps1`（calculate_crop_f1 → extract_cross_site_cm → calculate_crop_f1_degradation → generate_core_tables）
- 本机 Claude 记忆：`C:\Users\huangyouyuan\.claude\projects\d--AI-lunwen\memory\`，4 条 feedback（旧稿角色、写作定位、图表可读性、行文严谨）。仓库内等价规则在 `plan/style-guide.md`、`plan/format-spec.md`，以仓库为准

---

## 六、数据处理链与设计决策（摘要，细节见 `plan/claims.md`）

- **类别顺序**全局 corn=0, other=1, soybean=2。2026-09-18 事故：跨站曾用 corn/soybean/other，"大豆"列实为其它类，产生虚假负退化；修正后 72 个 ΔF1 全正
- **OA** = trace / 总像元（曾错为全矩阵和，全部 100%）
- **ΔF1** = 100 × (同一模型在目标站的站内汇总 F1 − 源站模型在目标站的跨站 F1 五次均值)。基准是目标站，不是源站
- **显著性**：检验对象是跨站 F1（不是 ΔF1）；配对单位 12 条路径的 5 次均值，`data_matrix.shape == (12, 3)`；Friedman → Wilcoxon → Holm step-down，报 p_holm。12 条路径共享 4 站，结论限定本文范围
- **指标**：玉米 F1、大豆 F1 分别报告；OA 只作站内辅助；不用 mIoU / Crop-mIoU（会混入其它类）
- **验证检查点**：表1 OA 89–95%；72 个 ΔF1 全正 0.44–7.39；表3 n=12
- **图 3 选窗**：只看真实玉米/大豆像元，作物像元错误率差 + 类别边界带错误率差（ConvGRU 相对另两模型均值）最大的 2×2 窗口

---

## 七、文件地图

```
main.tex                 格式：ctexart twocolumn、字号、标题样式、caption
sections/                01 引言 02 数据 03 方法 04 结果 06 结论
plan/                    paper-context（主线）claims（论点+处理链）results-map（节→数据→图表）
                         progress（状态）format-spec（格式）style-guide（文风）experiment-protocol
                         terminology  outline  review/（evidence-coverage、quality、structure）
scripts/                 数据链 4 个脚本 + run_all_updates.ps1；figstyle.py + 3 个 plot_*.py
results/summary/         科学数字唯一来源（raw/ 为标准顺序 CM）
tables/                  table1、1b、2、3 csv + table-schema.md
figures/                 data-manifest.md（每张图的输入/规格/状态）results/  study_area/  models/  workflow/
verification/            verification-report.md
bibliography/            references.bib、writing-style-report.md
legacy/                  旧稿（只作参考）、跨站原始输出（git 排除）
```
