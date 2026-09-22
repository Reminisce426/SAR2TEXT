# 阶段 6：成果整理与贡献核验

本目录只建立交付与验收模板，不包含实验结果，也不宣称任何规范或模型有效。

## 文档

- [`01_周期汇报与里程碑.md`](01_周期汇报与里程碑.md)：每 1–2 周汇报规则、状态定义与主流程回传格式。
- [`02_开源引用与许可清单.md`](02_开源引用与许可清单.md)：代码、模型、权重、数据、论文和工具的引用及许可核验。
- [`03_贡献分类与声明规则.md`](03_贡献分类与声明规则.md)：区分开源基线、工程实现、规范提案、模型改进和实验支持。
- [`04_最终交付与复现目录.md`](04_最终交付与复现目录.md)：Demo、报告、代码包与复现目录设计。
- [`05_结论证据验收表.md`](05_结论证据验收表.md)：结论进入报告、摘要、答辩和 Demo 前的证据门槛。

## 可直接复制的模板

- [`weekly_report.md`](../../templates/weekly_report.md)
- [`data_card.md`](../../templates/data_card.md)
- [`model_card.md`](../../templates/model_card.md)
- [`experiment_config.yaml`](../../templates/experiment_config.yaml)
- [`result_record.csv`](../../templates/result_record.csv)
- [`conclusion_evidence.csv`](../../templates/conclusion_evidence.csv)
- [`opensource_inventory.csv`](../../templates/opensource_inventory.csv)

复现包目录契约见 [`../../repro/README.md`](../../repro/README.md)。

## 最短使用流程

1. 复制周期汇报模板记录事实、假设、建议和证据位置。
2. 任何第三方资产先登记许可与引用，再进入代码包。
3. 每个正式实验用同一个 `run_id` 关联配置、日志、原始结果和复核记录。
4. 每条论文主张分配 `claim_id`，通过证据验收后才能用于最终结论。
