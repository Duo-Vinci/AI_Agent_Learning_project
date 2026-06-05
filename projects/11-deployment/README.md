# AI Agent 部署项目

完整的 AI Agent 应用部署方案，涵盖 Docker、Kubernetes、CI/CD、云平台部署等。

## 项目结构

```
11-deployment/
├── 01-docker/                    # Docker 容器化
│   └── src/
│       ├── Dockerfile            # 生产环境 Dockerfile
│       ├── Dockerfile.multistage # 多阶段构建
│       ├── .dockerignore         # Docker 忽略文件
│       ├── build.sh              # 镜像构建脚本
│       └── app/
│           └── main.py           # FastAPI 应用
│
├── 02-docker-compose/            # Docker Compose 编排
│   └── src/
│       ├── docker-compose.yml    # 生产环境配置
│       ├── docker-compose.dev.yml # 开发环境配置
│       ├── nginx.conf            # Nginx 配置
│       ├── nginx-default.conf    # Nginx 站点配置
│       ├── init-db.sql           # 数据库初始化
│       └── .env.example          # 环境变量示例
│
├── 03-secrets-management/        # 密钥管理
│   └── src/
│       ├── secrets_manager.py    # 密钥管理器
│       └── kubernetes-secrets.yaml # K8s Secrets 配置
│
├── 04-ci-cd/                     # CI/CD 流水线
│   └── src/
│       ├── .github/
│       │   └── workflows/
│       │       └── ci-cd.yml     # GitHub Actions
│       └── .gitlab-ci.yml        # GitLab CI
│
├── 05-cloud-deployment/          # 云平台部署
│   └── src/
│       ├── aws_ecs_deploy.py     # AWS ECS 部署
│       ├── gcp_cloud_run_deploy.py # GCP Cloud Run 部署
│       ├── azure_container_apps_deploy.py # Azure 部署
│       ├── aliyun-ack-deployment.yaml # 阿里云 ACK
│       └── kubernetes-deployment.yaml # K8s 完整配置
│
├── 06-serverless/                # Serverless 部署
│   └── src/
│       ├── serverless.yml        # Serverless Framework 配置
│       ├── lambda_handler.py     # AWS Lambda 处理器
│       └── worker_handler.py     # 异步任务处理器
│
├── 07-nginx-config/              # Nginx 负载均衡
│   └── src/
│       └── nginx-load-balance.conf # 负载均衡配置
│
├── requirements.txt              # Python 依赖
└── deploy.sh                     # 统一部署脚本
```

## 快速开始

### 1. Docker 本地部署

```bash
cd 01-docker/src
chmod +x build.sh
./build.sh latest

# 运行容器
docker run -d \
  --name ai-agent \
  -p 8000:8000 \
  --env-file .env \
  ai-agent:latest
```

### 2. Docker Compose 部署

```bash
cd 02-docker-compose/src

# 复制环境变量文件
cp .env.example .env
# 编辑 .env 填入实际配置

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f agent-api

# 访问服务
curl http://localhost:8000/health
```

### 3. Kubernetes 部署

```bash
cd 05-cloud-deployment/src

# 创建 Namespace 和 Secrets
kubectl create namespace ai-agent
kubectl apply -f kubernetes-secrets.yaml

# 部署应用
kubectl apply -f kubernetes-deployment.yaml

# 查看状态
kubectl get pods -n ai-agent
kubectl get svc -n ai-agent

# 查看日志
kubectl logs -f deployment/ai-agent-deployment -n ai-agent
```

### 4. 云平台部署

#### AWS ECS

```bash
cd 05-cloud-deployment/src
python aws_ecs_deploy.py --image ai-agent:latest --tag v1.0.0
```

#### GCP Cloud Run

```bash
python gcp_cloud_run_deploy.py --project-id your-project --tag v1.0.0
```

#### Azure Container Apps

```bash
python azure_container_apps_deploy.py --resource-group ai-agent-rg --tag v1.0.0
```

### 5. Serverless 部署

```bash
cd 06-serverless/src

# 安装 Serverless Framework
npm install -g serverless
npm install

# 部署到 AWS Lambda
serverless deploy --stage production

# 查看日志
serverless logs -f api --tail
```

### 6. 使用统一部署脚本

```bash
# 给脚本执行权限
chmod +x deploy.sh

# Docker 本地部署
./deploy.sh --platform docker --tag latest

# Docker Compose 部署
./deploy.sh --platform docker-compose

# Kubernetes 部署
./deploy.sh --platform kubernetes --tag v1.0.0 --env production

# AWS ECS 部署
./deploy.sh --platform aws --tag v1.0.0

# 查看日志
./deploy.sh --platform docker --logs

# 回滚部署
./deploy.sh --platform kubernetes --rollback
```

## 配置说明

### 环境变量

创建 `.env` 文件：

```bash
# 应用配置
ENV=production
LOG_LEVEL=INFO

# API Keys
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key

# 数据库
DATABASE_URL=postgresql://user:pass@host:5432/db

# Redis
REDIS_URL=redis://host:6379/0

# 安全
SECRET_KEY=your-secret-key
```

### 密钥管理

- **环境变量**: 开发环境
- **Docker Secrets**: Docker Swarm
- **Kubernetes Secrets**: K8s 集群
- **AWS Secrets Manager**: AWS 环境
- **GCP Secret Manager**: GCP 环境

参考 `03-secrets-management/src/secrets_manager.py`

## CI/CD 流程

### GitHub Actions

1. 代码检查 (lint, format)
2. 单元测试 (pytest)
3. 安全扫描 (bandit, safety)
4. 构建镜像
5. 推送到镜像仓库
6. 部署到环境

配置文件: `04-ci-cd/src/.github/workflows/ci-cd.yml`

### GitLab CI

配置文件: `04-ci-cd/src/.gitlab-ci.yml`

## 负载均衡

### Nginx 配置

- **负载均衡算法**: least_conn, ip_hash, round_robin
- **限流**: 基于 IP 和路径
- **缓存**: 静态资源缓存
- **SSL/TLS**: HTTPS 配置
- **健康检查**: 自动故障转移

配置文件: `07-nginx-config/src/nginx-load-balance.conf`

## 监控和日志

### 健康检查

所有部署都包含健康检查端点: `/health`

```bash
curl http://your-domain/health
```

### 日志查看

```bash
# Docker
docker logs -f ai-agent

# Docker Compose
docker-compose logs -f agent-api

# Kubernetes
kubectl logs -f deployment/ai-agent -n ai-agent

# Serverless
serverless logs -f api --tail
```

## 性能优化

1. **Docker 镜像优化**
   - 多阶段构建减小镜像体积
   - 使用 Alpine 基础镜像
   - 合理使用缓存层

2. **资源限制**
   - CPU 和内存限制
   - 请求和限制比例

3. **水平扩展**
   - HPA (Horizontal Pod Autoscaler)
   - 负载均衡

4. **缓存策略**
   - Redis 缓存
   - Nginx 静态资源缓存

## 安全最佳实践

1. **镜像安全**
   - 使用非 root 用户运行
   - 定期扫描漏洞 (Trivy)
   - 最小化基础镜像

2. **密钥管理**
   - 不在代码中硬编码密钥
   - 使用密钥管理服务
   - 定期轮换密钥

3. **网络安全**
   - HTTPS/TLS 加密
   - 网络策略隔离
   - 限流和防护

4. **访问控制**
   - RBAC 权限管理
   - 服务账号隔离

## 故障排查

### 容器无法启动

```bash
# 查看日志
docker logs ai-agent

# 检查配置
docker inspect ai-agent

# 进入容器调试
docker exec -it ai-agent /bin/bash
```

### 服务不可访问

```bash
# 检查端口映射
docker ps
netstat -tlnp | grep 8000

# 检查防火墙
sudo ufw status

# 测试连接
curl -v http://localhost:8000/health
```

### K8s Pod 异常

```bash
# 查看 Pod 状态
kubectl get pods -n ai-agent
kubectl describe pod <pod-name> -n ai-agent

# 查看日志
kubectl logs <pod-name> -n ai-agent

# 进入 Pod 调试
kubectl exec -it <pod-name> -n ai-agent -- /bin/bash
```

## 参考文档

- [Docker 官方文档](https://docs.docker.com/)
- [Kubernetes 官方文档](https://kubernetes.io/docs/)
- [AWS ECS 文档](https://docs.aws.amazon.com/ecs/)
- [GCP Cloud Run 文档](https://cloud.google.com/run/docs)
- [Azure Container Apps 文档](https://docs.microsoft.com/azure/container-apps/)
- [Serverless Framework 文档](https://www.serverless.com/framework/docs/)

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
