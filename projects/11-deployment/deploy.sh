#!/bin/bash
# 完整的部署脚本 - 支持多种环境和平台

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
PROJECT_NAME="ai-agent"
DOCKER_IMAGE="${PROJECT_NAME}"
DEFAULT_TAG="latest"

# 函数：打印标题
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# 函数：打印信息
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# 函数：打印警告
warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 函数：打印错误
error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# 函数：检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        error "$1 未安装，请先安装"
    fi
}

# 函数：Docker 本地部署
deploy_docker_local() {
    print_header "Docker 本地部署"

    info "构建 Docker 镜像..."
    docker build -t ${DOCKER_IMAGE}:${TAG} .

    info "停止旧容器..."
    docker stop ${PROJECT_NAME} 2>/dev/null || true
    docker rm ${PROJECT_NAME} 2>/dev/null || true

    info "启动新容器..."
    docker run -d \
        --name ${PROJECT_NAME} \
        -p 8000:8000 \
        --env-file .env \
        --restart unless-stopped \
        ${DOCKER_IMAGE}:${TAG}

    info "等待服务启动..."
    sleep 5

    if curl -f http://localhost:8000/health &> /dev/null; then
        info "✅ 部署成功！访问地址: http://localhost:8000"
    else
        error "健康检查失败"
    fi
}

# 函数：Docker Compose 部署
deploy_docker_compose() {
    print_header "Docker Compose 部署"

    check_command "docker-compose"

    info "停止现有服务..."
    docker-compose down

    info "构建并启动服务..."
    docker-compose up -d --build

    info "等待服务就绪..."
    sleep 10

    info "查看服务状态..."
    docker-compose ps

    if curl -f http://localhost:8000/health &> /dev/null; then
        info "✅ 部署成功！访问地址: http://localhost:8000"
    else
        error "健康检查失败"
    fi
}

# 函数：AWS ECS 部署
deploy_aws_ecs() {
    print_header "AWS ECS 部署"

    check_command "aws"

    info "执行 AWS ECS 部署脚本..."
    python3 deploy/aws_ecs_deploy.py --tag ${TAG}
}

# 函数：GCP Cloud Run 部署
deploy_gcp_cloudrun() {
    print_header "GCP Cloud Run 部署"

    check_command "gcloud"

    info "执行 GCP Cloud Run 部署脚本..."
    python3 deploy/gcp_cloud_run_deploy.py --tag ${TAG}
}

# 函数：Azure Container Apps 部署
deploy_azure_containerapp() {
    print_header "Azure Container Apps 部署"

    check_command "az"

    info "执行 Azure 部署脚本..."
    python3 deploy/azure_container_apps_deploy.py --tag ${TAG}
}

# 函数：Kubernetes 部署
deploy_kubernetes() {
    print_header "Kubernetes 部署"

    check_command "kubectl"

    local NAMESPACE="${NAMESPACE:-default}"

    info "应用 Kubernetes 配置..."
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/secrets.yaml
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
    kubectl apply -f k8s/ingress.yaml
    kubectl apply -f k8s/hpa.yaml

    info "等待部署完成..."
    kubectl rollout status deployment/${PROJECT_NAME} -n ${NAMESPACE} --timeout=5m

    info "查看服务状态..."
    kubectl get pods -n ${NAMESPACE} -l app=${PROJECT_NAME}

    info "✅ Kubernetes 部署成功！"
}

# 函数：Serverless 部署
deploy_serverless() {
    print_header "Serverless 部署"

    check_command "serverless"

    local STAGE="${STAGE:-dev}"

    info "部署到 Serverless 平台..."
    cd serverless/
    serverless deploy --stage ${STAGE}
    cd ..

    info "✅ Serverless 部署成功！"
}

# 函数：健康检查
health_check() {
    local URL=$1
    local MAX_RETRIES=10
    local RETRY_INTERVAL=5

    info "执行健康检查: ${URL}"

    for i in $(seq 1 ${MAX_RETRIES}); do
        if curl -f ${URL}/health &> /dev/null; then
            info "✅ 健康检查通过"
            return 0
        else
            warn "健康检查失败，等待 ${RETRY_INTERVAL} 秒后重试... (${i}/${MAX_RETRIES})"
            sleep ${RETRY_INTERVAL}
        fi
    done

    error "健康检查失败，已达最大重试次数"
}

# 函数：回滚
rollback() {
    print_header "回滚部署"

    case ${PLATFORM} in
        docker)
            warn "Docker 本地部署不支持自动回滚"
            ;;
        kubernetes)
            info "回滚 Kubernetes Deployment..."
            kubectl rollout undo deployment/${PROJECT_NAME} -n ${NAMESPACE:-default}
            ;;
        serverless)
            info "回滚 Serverless 部署..."
            cd serverless/
            serverless rollback --stage ${STAGE:-dev}
            cd ..
            ;;
        *)
            error "不支持的平台: ${PLATFORM}"
            ;;
    esac

    info "✅ 回滚完成"
}

# 函数：查看日志
show_logs() {
    print_header "查看日志"

    case ${PLATFORM} in
        docker)
            docker logs -f ${PROJECT_NAME}
            ;;
        docker-compose)
            docker-compose logs -f
            ;;
        kubernetes)
            kubectl logs -f deployment/${PROJECT_NAME} -n ${NAMESPACE:-default}
            ;;
        *)
            error "不支持的平台: ${PLATFORM}"
            ;;
    esac
}

# 函数：显示帮助
show_help() {
    cat << EOF
AI Agent 部署脚本

用法: $0 [选项]

选项:
    -p, --platform PLATFORM    部署平台 (docker|docker-compose|kubernetes|aws|gcp|azure|serverless)
    -t, --tag TAG             Docker 镜像标签 (默认: latest)
    -e, --env ENV             环境 (dev|staging|production)
    -r, --rollback            回滚部署
    -l, --logs                查看日志
    -h, --help                显示帮助信息

示例:
    # Docker 本地部署
    $0 --platform docker

    # Docker Compose 部署
    $0 --platform docker-compose

    # Kubernetes 部署
    $0 --platform kubernetes --tag v1.0.0

    # AWS ECS 部署
    $0 --platform aws --env production

    # 回滚 Kubernetes 部署
    $0 --platform kubernetes --rollback

    # 查看 Docker 日志
    $0 --platform docker --logs

EOF
}

# 主函数
main() {
    # 默认值
    PLATFORM=""
    TAG=${DEFAULT_TAG}
    ENV="production"
    ACTION="deploy"

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--platform)
                PLATFORM="$2"
                shift 2
                ;;
            -t|--tag)
                TAG="$2"
                shift 2
                ;;
            -e|--env)
                ENV="$2"
                shift 2
                ;;
            -r|--rollback)
                ACTION="rollback"
                shift
                ;;
            -l|--logs)
                ACTION="logs"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error "未知选项: $1"
                ;;
        esac
    done

    # 检查必需参数
    if [ -z "${PLATFORM}" ]; then
        error "请指定部署平台 (-p|--platform)"
    fi

    # 显示配置
    print_header "部署配置"
    echo "平台: ${PLATFORM}"
    echo "标签: ${TAG}"
    echo "环境: ${ENV}"
    echo "操作: ${ACTION}"
    echo ""

    # 执行操作
    case ${ACTION} in
        deploy)
            case ${PLATFORM} in
                docker)
                    deploy_docker_local
                    ;;
                docker-compose)
                    deploy_docker_compose
                    ;;
                kubernetes|k8s)
                    deploy_kubernetes
                    ;;
                aws|ecs)
                    deploy_aws_ecs
                    ;;
                gcp|cloudrun)
                    deploy_gcp_cloudrun
                    ;;
                azure)
                    deploy_azure_containerapp
                    ;;
                serverless|lambda)
                    deploy_serverless
                    ;;
                *)
                    error "不支持的平台: ${PLATFORM}"
                    ;;
            esac
            ;;
        rollback)
            rollback
            ;;
        logs)
            show_logs
            ;;
        *)
            error "未知操作: ${ACTION}"
            ;;
    esac
}

# 执行主函数
main "$@"
