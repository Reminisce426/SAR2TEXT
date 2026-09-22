# SAR 专用图文基线采用前审计

审计日期：2026-09-22。这里只记录官方论文/官方仓库可核验的信息；网盘文件尚未下载，因此权重内容、哈希、实际可加载性和数值均未验证。

## 结论摘要

| 候选 | 身份与数据域 | 许可 | 权重/代码 | 当前判断 |
|---|---|---|---|---|
| CAESAR-Radi SARCLIP | SAR 专用 CLIP；配套 SARCAP，官方论文称数据覆盖多分辨率、多传感器、多类别，仓库列出 Capella、WorldCover、OGSOD、RSDD、SADD、SIVED、SEN12MS 等来源 | 代码 MIT；SARCAP **仅限非商业研究和教育**，且须遵守原始数据提供方条款 | 官方仓库提供代码及百度网盘权重/数据入口；权重说明为研究和非商业用途 | 可列为候选；下载后必须核验 SHA256、模型结构和 Sentinel-1 GRD 域匹配，不能直接视为可复现实验 |
| SAR-TEXT / SAR-RS-CLIP | SAR-TEXT 超过 13 万图文对；论文在 OSdataset_512、HRSID 上做检索。仓库提供基于 OpenCLIP 的 SAR-RS-CLIP | 仓库代码为 Apache-2.0；**未发现数据集和权重的独立许可文本**，不能把代码许可外推到数据/权重 | 数据和模型通过百度网盘发布；检索脚本依赖 `open_clip`、`clip_benchmark`、PyTorch、Pillow、NumPy、Pandas、tqdm | 技术上接近现有环境，但许可澄清前只作参考/内部可行性核查，不纳入可发布成果 |

## 关键风险

1. **名称冲突**：公开资料中有多个名为 SARCLIP/SAR-CLIP 的工作。引用时必须写作者、论文题名、年份和仓库地址，不能只写模型简称。
2. **数据域不等价**：SARCAP、SAR-TEXT、HRSID 等混合或目标检测衍生数据，不等于本课题最终的 Sentinel-1 GRD 场景数据。需要记录传感器、极化、产品级别、空间分辨率、裁块方式和描述来源。
3. **描述可能是合成/半自动生成**：SARCAP 许可文件明确提示 SARTEX 半自动/模板转换可能产生错误；SAR-TEXT 论文也以 SAR-Narrator 构造描述。评价时必须区分人工文本、模板文本和模型生成文本。
4. **权重许可与代码许可分离**：能下载不代表能再分发或用于商业场景。每个权重都应保存来源 URL、下载日期、许可快照和 SHA256。
5. **依赖与接口差异**：CAESAR-Radi SARCLIP 自带 `sar_clip` 实现并列出 GDAL、Transformers、safetensors 等依赖；SAR-TEXT 的检索实现使用 OpenCLIP 和 `clip_benchmark`。不要把权重强行加载到名称相同但结构不一致的编码器。
6. **公平性**：若 SAR 专用模型原生输入大小/归一化不同，可保留其官方预处理，但候选库、测试划分、正例映射和指标实现必须一致，并报告预处理差异。

## 采用前检查表

- [ ] 明确唯一论文与官方仓库，记录 commit/tag。
- [ ] 保存代码、数据、权重各自许可；不以 README 一句话代替完整条款。
- [ ] 下载权重并记录文件名、字节数、SHA256。
- [ ] 在隔离环境中安装依赖并导出 `pip freeze`。
- [ ] 确认权重与架构、输入尺寸、tokenizer 一一匹配。
- [ ] 用 8–32 个非正式样本完成离线加载和双向检索冒烟测试。
- [ ] 检查训练数据与最终测试集是否重叠，尤其是 HRSID、SEN12MS 等来源。
- [ ] 用本仓库同一 manifest 和指标模块复算，而非直接引用论文数值。
- [ ] 对人工/模板/模型生成描述分别统计；记录语言和规范化版本。

## 一手来源

- CAESAR-Radi SARCLIP 官方仓库：https://github.com/CAESAR-Radi/SARCLIP
- SARCLIP 论文 DOI：https://doi.org/10.1016/j.isprsjprs.2025.10.017
- SAR-TEXT 官方仓库：https://github.com/YiguoHe/SAR-TEXT
- SAR-TEXT 论文：https://arxiv.org/abs/2507.18743
