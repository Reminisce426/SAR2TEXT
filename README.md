# SAR2text：SAR 与自然语言研究

当前项目以 SAR 图像描述和自然语言生成 SAR 为主体，双向图文检索是基线；本 README 下文说明的是已实现的阶段 3 检索代码，不代表描述或生成模型已经完成。整体计划见 [六周总计划](docs/项目总计划_两周汇报制.md)，跨设备工作与当前状态见 [Mac 交接说明](docs/reports/2026-09-23/Mac跨设备工作交接.md)。

本仓库提供一个**数据集无关、离线权重友好**的 OpenCLIP 零样本检索基线。它用于建立可复现对照，不把 OpenCLIP、SARCLIP 或 SAR-TEXT 作为本课题创新。

当前状态：代码结构、配置协议、双向 Recall@1/5/10、案例导出和无模型最小测试已完成；由于正式数据集和实际 SAR 图像尚未确定，**尚未产生任何实验数值**。

## 任务边界

- 已实现：文字找图（text-to-image）、图找文（image-to-text）。
- 未实现：SAR 图像描述、文字生成 SAR。它们不是检索任务，不能用本仓库的 Recall@K 代替各自评价。
- 输入图像：当前通用基线通过 Pillow 读取并转为 RGB。单通道 SAR 会复制为三通道；这是一项明确的基线处理，不代表最优 SAR 预处理。

## 数据清单

UTF-8 CSV 必须包含以下列：

```csv
image_id,image_path,caption_id,caption,split
S1_0001,relative/path/0001.png,S1_0001_c0,"a SAR image of a harbor",test
S1_0001,relative/path/0001.png,S1_0001_c1,"ships are visible near the quay",test
```

约束：

- `image_id` 标识图像实体；同一图像可对应多条描述。
- `caption_id` 在清单中必须唯一。
- 同一 `image_id` 的 `image_path` 必须一致。
- 相对路径以配置中的 `image_root` 为基准。
- 候选库按清单首次出现顺序固定；不要在不同方法间改变清单或测试划分。

配置中的相对路径统一以配置文件所在目录为基准，因此从不同工作目录启动时仍会解析到同一批输入。先验证清单：

```powershell
$env:PYTHONPATH = "src"
python -m sar_baseline.validate_manifest --config configs/openclip_vit_b32.json
```

## DBCloud 运行

在已具备 PyTorch 2.4.1、OpenCLIP 3.3.0 和 Pillow 的环境中，不需要联网安装权重：

1. 复制 `configs/openclip_vit_b32.json` 为一次实验专用配置。
2. 填写 `data.manifest`, `data.image_root` 和本地 `model.pretrained_path`。
3. 记录权重的预期 SHA256 到 `model.expected_sha256`；首次不知道时可暂留空，程序仍会在产物中计算并记录实际值。
4. 在加载模型前执行离线输入预检；它会核对配置、清单、图像文件、权重、可选权重哈希和输出位置，不会初始化 OpenCLIP 或 CUDA：

```bash
export PYTHONPATH=src
python -m sar_baseline.preflight --config configs/openclip_vit_b32.json
```

5. 预检通过后执行：

```bash
export PYTHONPATH=src
python -m sar_baseline.run --config configs/openclip_vit_b32.json
```

程序不会下载模型。结果写入配置指定的 `output_dir`：

- `resolved_config.json`：本次实际配置；
- `preflight.json`：模型初始化前的配置、清单、图像、权重和输出位置检查记录；
- `environment.json`：Python、平台、PyTorch、OpenCLIP、CUDA、GPU、Git 提交号和工作树状态；
- `fingerprints.json`：清单与权重 SHA256；
- `metrics.json`：双向 Recall@1/5/10、均值和有效查询数；
- `cases.jsonl`：固定数量的最佳/最差查询及 Top-K 候选，用于案例分析。

`evaluation.case_top_k` 只控制 `cases.jsonl` 中每条案例保留的候选数量；Recall@K 仍按 `evaluation.recall_ks` 独立计算。

## 最小测试

最小测试不需要 PyTorch、OpenCLIP、GPU 或真实图像：

```powershell
python -m unittest discover -s tests -v
```

它覆盖多描述正例、双向检索、稳定并列排序和清单约束。真实数据确定后，还需增加 8–32 个样本的模型冒烟测试，确认图像读取、离线权重和 GPU 推理链路。

## 公平对照最低要求

所有模型必须使用同一测试清单、同一候选库、同一正例定义、同一 Recall@K 实现和同一案例抽取规则。输入分辨率或预处理若因模型原生要求不同，必须单独报告，不能写成“完全相同预处理”。SAR 专用基线的采用前审计见 [docs/sar_baseline_audit.md](docs/sar_baseline_audit.md)。
