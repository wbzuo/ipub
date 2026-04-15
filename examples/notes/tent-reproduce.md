# Tent 复现记录

## 背景

Tent 是一篇经典的 Test-Time Adaptation (TTA) 论文，核心思想是在测试阶段通过最小化预测的熵来更新 BN 层的参数。

论文地址：https://arxiv.org/abs/2006.10726
代码仓库：https://github.com/DequanWang/tent

## 环境配置

```bash
conda create -n tent python=3.8
conda activate tent
pip install torch==1.12.0 torchvision==0.13.0
pip install robustbench
```

注意：robustbench 的版本要和 torch 版本匹配，不然会报 CUDA 错误。

## 核心代码解读

Tent 的核心就两步：

1. 冻结所有参数，只开放 BN 层的 affine 参数
2. 用预测的熵作为 loss 来更新

```python
def configure_model(model):
    model.train()
    model.requires_grad_(False)
    for m in model.modules():
        if isinstance(m, nn.BatchNorm2d):
            m.requires_grad_(True)
            m.track_running_stats = False
            m.running_mean = None
            m.running_var = None
    return model

def forward_and_adapt(x, model, optimizer):
    outputs = model(x)
    loss = softmax_entropy(outputs).mean(0)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
    return outputs
```

关键点：`track_running_stats = False` 这一行很重要，不然 BN 会继续用训练时的统计量。

## 实验结果

在 CIFAR-100-C 上的结果：

| Corruption | Source | Tent |
|-----------|--------|------|
| Gaussian Noise | 26.3 | 38.7 |
| Shot Noise | 29.1 | 40.2 |
| Impulse Noise | 24.8 | 36.5 |
| Fog | 46.2 | 55.8 |
| Snow | 41.3 | 51.2 |

平均提升约 10 个点，和论文报告的一致。

## 踩坑记录

1. **batch size 太小会崩** - batch size < 16 的时候 BN 统计量不稳定，效果反而变差
2. **学习率很敏感** - 默认 0.001 在大部分 corruption 上 ok，但在某些类型上不稳定
3. **单次 vs 持续适应** - Tent 是 episodic 的，每个 batch 适应完要 reset 模型，不然会 error accumulation

## 总结

Tent 的方法非常简洁优雅，但局限性也很明显：
- 只更新 BN 层，能力有限
- 对 batch size 敏感
- 持续适应场景下不稳定

后续可以看 CoTTA、SAR 等改进方法。
