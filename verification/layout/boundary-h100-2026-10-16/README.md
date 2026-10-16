# 边界定义与硬件更正编译核查

2026-10-16，Verified，仅限本次内容同步、编译与受影响页面排版。按作者提供信息将显卡改为NVIDIA H100（40 GB显存），同步`sections/03_methods.tex`与`plan/experiment-protocol.md`；未现场检测训练硬件，未重新计算科学结果。

当前整稿为`output/main.pdf`，8页，SHA-256：`82ad810eac3422808bfebe9286879e3bfdef423ec47f3a589c97534b67442522`。执行默认`latexmk -xelatex -synctex=1 -interaction=nonstopmode -halt-on-error main.tex`，退出码0。最终控制台记录在`output/build/main/build-boundary-h100-2026-10-16-final.txt`。

逐字核对PDF提取文字：作者提供的2.3边界段完整出现在第4页，接在“OA作为总体参考”之后；第5页含NVIDIA H100及40 GB显存，旧4090文字已不存在。用该段局部`\looseness=-1`消除首次编译时末字“异。”单独跨到第5页的问题，不改段落文字。

Poppler以130 dpi渲染并查看最终第4、5页：`final-page-4.png`、`final-page-5.png`。正文、表1、联合分布图及本站F1图无裁切或重叠。第5页右栏仍有图表分页产生的留白，本次没有重排Results图表。用PyMuPDF以72 dpi逐页比较编译前PDF，只有第4、5页改变，其余6页像素一致。

日志无LaTeX错误、Overfull、缺字、未定义引用或文献引用；保留xeCJK字体族重定义、SimSun/SimHei粗体替代及1.3段落一处Underfull提示（badness 2376，第55—56行）。对应1.3页面与编译前稿像素一致。

保护文件哈希保持不变：`sections/02_data.tex`为`4939398686bd18c320b5a63bf207a7e509a22c212c6981afd526214b66627b93`；`sections/04_results.tex`为`a1bfd5dcea3283af7757d66c7a8f11dadbb54519032c4fdd616c9b015b5d23fc`。

编译前稿及原路径、归档路径、原因和SHA-256见[原稿快照](../../../archive/manuscript/2026-10-16/boundary-h100-before/manifest.json)。本目录`page-4.png`、`page-5.png`对应[首次编译稿](../../../archive/manuscript/2026-10-16/boundary-h100-first-build/manifest.json)，仅保留检查过程，以`final-page-*.png`为本次最终页面。
