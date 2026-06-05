#!/bin/bash
# Docker 镜像构建脚本

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
IMAGE_NAME="ai-agent"
IMAGE_TAG="${1:-latest}"
REGISTRY="${REGISTRY:-docker.io}"
DOCKERFILE="${2:-Dockerfile}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}开始构建 Docker 镜像${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "镜像名称: ${YELLOW}${IMAGE_NAME}${NC}"
echo -e "镜像标签: ${YELLOW}${IMAGE_TAG}${NC}"
echo -e "Dockerfile: ${YELLOW}${DOCKERFILE}${NC}"
echo ""

# 检查 Dockerfile 是否存在
if [ ! -f "$DOCKERFILE" ]; then
    echo -e "${RED}错误: 找不到 Dockerfile: $DOCKERFILE${NC}"
    exit 1
fi

# 构建镜像
echo -e "${GREEN}[1/4] 构建 Docker 镜像...${NC}"
docker build \
    -t ${IMAGE_NAME}:${IMAGE_TAG} \
    -t ${IMAGE_NAME}:latest \
    -f ${DOCKERFILE} \
    --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
    --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown") \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 镜像构建成功${NC}"
else
    echo -e "${RED}✗ 镜像构建失败${NC}"
    exit 1
fi

# 查看镜像信息
echo -e "\n${GREEN}[2/4] 镜像信息:${NC}"
docker images ${IMAGE_NAME}:${IMAGE_TAG}

# 检查镜像大小
IMAGE_SIZE=$(docker images ${IMAGE_NAME}:${IMAGE_TAG} --format "{{.Size}}")
echo -e "镜像大小: ${YELLOW}${IMAGE_SIZE}${NC}"

# 运行安全扫描（如果安装了 trivy）
if command -v trivy &> /dev/null; then
    echo -e "\n${GREEN}[3/4] 运行安全扫描...${NC}"
    trivy image --severity HIGH,CRITICAL ${IMAGE_NAME}:${IMAGE_TAG}
else
    echo -e "\n${YELLOW}[3/4] 跳过安全扫描 (未安装 trivy)${NC}"
fi

# 可选：推送到镜像仓库
read -p "是否推送镜像到仓库? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${GREEN}[4/4] 推送镜像到仓库...${NC}"

    # 标记镜像
    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

    # 推送镜像
    docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

    echo -e "${GREEN}✓ 镜像推送成功${NC}"
else
    echo -e "${YELLOW}跳过镜像推送${NC}"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}构建完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "运行命令: ${YELLOW}docker run -p 8000:8000 ${IMAGE_NAME}:${IMAGE_TAG}${NC}"
