# 远端保存范围与重建说明

2026-10-14，作者最终要求：远端仓库小于100 MB；结果应保留，归档和大文件不上传。作者拟删除旧远端后重新推送。本轮不再采用“整个results不上传”或另交ZIP的早期安排。

## 保存范围

保留正文、表体、图例拼版文本、脚本、文献元数据、规则、任务/核查记录，以及results中的小型CSV/JSON/Markdown等。单文件采用2,000,000字节门槛：小于此值可纳入，达到或超过则原位保留本地。100 MB总量按100,000,000字节严格检查，除Git对象外也核验新目录连同.git的实际大小。

归档目录、旧Word/实验资产、图片/PDF、NPZ/NPY数组、模型、压缩包、编译临时文件留本地。小型数组同样作为本地计算资产，不当成文本结果上传。results不整目录忽略；大型summary表也记录在清单中，不能据此声称summary已全部携带。2026-10-15全量文档复核后，保留`output/README.md`、`output/preview-manifest.json`和既有研究区经纬度的说明、坐标及核查元数据这5份小型文本；不因它们与资产同目录而一并排除，图片和归档仍留本地。

机器规则为 `plan/submission-policy.json`；`plan/remote-local-files.json`记录此次未上传文件的原路径、字节数、SHA-256和原因。该清单覆盖原来被Git跟踪的文件，不声称穷举数GB的本地忽略资产。新仓库的复制清单为 `plan/remote-copy-manifest.json`。

## 本地位置

- 完整科研工作区：`D:/AI/lunwen/`，数据、原Git、已有工作树都不移动。
- 新上传仓库：`D:/AI/lunwen-remote-2026-10-14/`。使用当前工作文件建立新历史，不复制旧.git，不导入旧分支或标签。
- 原历史及修改前备份：`D:/AI/lunwen_archive/2026-10-14-remote-slim/`。其中bundle保存旧refs可达历史；原.git也仍在完整科研目录。
- 原Git不用于重推；从它推送会重新带回旧数据历史。后续只从新上传仓库更新远端，不能合并旧历史。

## 准备与检查

```powershell
# 从完整工作区准备一个尚不存在的目标目录；不覆盖、不删除、不提交、不推送
python -B scripts/manage_remote_repository.py prepare --destination D:/AI/lunwen-remote-2026-10-14

# 在新上传仓库检查暂存内容或已提交历史
python -B scripts/manage_remote_repository.py check --staged
python -B scripts/manage_remote_repository.py check --history
```

新仓库安装 `.githooks/`中的提交/推送检查，拦截归档、资产、大文件和超额体积；Git忽略规则不能按文件大小自动筛选，已知大文件用明确路径排除，新文件靠检查拦截。钩子在新克隆需执行 `git config core.hooksPath .githooks`启用。

准备目录通过本地`.git/info/attributes`保留复制字节，不修改完整科研仓库的通用换行属性。2026-10-15已撤回此前引起整文件差异的通用`* -text`修改；此处的本地设置不改变科学数据内容。

作者删除旧GitHub仓库后，应新建同名空仓库（不要自动生成README），然后从新上传目录执行普通推送。原远端地址为 `https://github.com/huangyouyuan/lunwen.git`。重建和推送尚未执行时不能标为Verified，也不能用准备目录大小冒充GitHub服务器已缩小。GitHub页面/API体积可能有更新延迟，推送后另核验实际refs和新克隆。

## 继续科研与写作

新远端包含结果阅读材料，但不构成全部实验资产备份。需要大表、数组、正式图像或旧Word时，从完整科研工作区按同一相对路径取得原件；校验清单SHA-256，目标已有不同字节文件时停止，不能覆盖。不要为缺少文件重新训练、推理或造占位结果。

恢复的本地资产继续忽略，提交前核查清单。当前正文已有图像引用，因此只克隆远端不能直接编译完整PDF；先恢复图像再按授权编译。写作流程见 `plan/writing-workflow.md`。
