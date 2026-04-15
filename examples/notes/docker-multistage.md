# Docker 多阶段构建踩坑

今天在给训练服务做容器化的时候，用了多阶段构建来减小镜像体积，踩了几个坑。

## 问题

直接用 pytorch 官方镜像打包，镜像高达 8.5GB。部署的时候拉取太慢。

## 方案：多阶段构建

```dockerfile
# 第一阶段：安装依赖
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# 第二阶段：只复制需要的东西
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .

CMD ["python", "serve.py"]
```

## 踩坑

### 坑1：CUDA 版本不匹配

第一阶段和第二阶段用了不同的 base image，导致编译出来的 CUDA extension 运行时报错：

```
RuntimeError: CUDA error: no kernel image is available for execution on the device
```

解决：两个阶段必须用完全相同的 base image。

### 坑2：pip install --prefix 的路径问题

用 `--prefix=/install` 安装后，复制到第二阶段的时候路径对不上。

解决：需要设置 `PYTHONPATH`：

```dockerfile
ENV PYTHONPATH=/usr/local/lib/python3.10/site-packages
```

### 坑3：.dockerignore 没写好

把 `data/` 目录和 `*.pth` 文件也复制进去了，镜像又变大了。

```
# .dockerignore
data/
*.pth
*.pt
__pycache__/
.git/
wandb/
```

## 结果

优化前：8.5GB
优化后：3.2GB

减少了 62%。拉取时间从 5 分钟降到 2 分钟左右。
