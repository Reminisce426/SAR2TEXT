# 复现包目录契约

本目录当前只定义验收契约，不包含正式实验产物。

## 一个正式实验必须可追踪到

```text
run_id
├─ code_commit
├─ environment lock + system info
├─ data card + manifest hash + split hash
├─ model card + weight hash
├─ immutable config + config hash
├─ command + stdout/stderr log
├─ raw result
├─ summary/table/figure generation record
└─ linked claim_id + reviewer decision
```

## 建议复现顺序

1. 校验环境与依赖版本。
2. 按数据卡获取数据并核对原始清单和哈希。
3. 执行预处理/规范化，核对产物清单和哈希。
4. 运行最小推理，确认模型、权重和评价脚本可用。
5. 运行基线，再运行规范化或模型改进实验。
6. 从原始结果生成表格与图，不手工改写数字。
7. 按 `claim_id` 执行独立复核。

## 当前验收状态

- 环境复现：未开始
- 数据复现：未开始
- 基线复现：未开始
- 规范化实验复现：未开始
- 模型适配/改进复现：未开始
- 表格与图重建：未开始
- 独立复核：未开始

任何一项在完成前不得写成“已复现”。
