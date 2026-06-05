#!/bin/bash

# AI Agent 数据恢复脚本

set -e

# ============= 配置 =============
BACKUP_DIR="/backups"

# 数据库配置
PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5432}"
PG_USER="${PG_USER:-postgres}"
PG_DB="${PG_DB:-agentdb}"

REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

# ============= 日志函数 =============
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log_success() {
    echo -e "\033[0;32m[$(date '+%Y-%m-%d %H:%M:%S')] ✓ $1\033[0m"
}

log_error() {
    echo -e "\033[0;31m[$(date '+%Y-%m-%d %H:%M:%S')] ✗ $1\033[0m"
}

log_warning() {
    echo -e "\033[0;33m[$(date '+%Y-%m-%d %H:%M:%S')] ⚠ $1\033[0m"
}

# ============= 列出可用备份 =============
list_backups() {
    local backup_type=$1

    log "可用的 $backup_type 备份:"
    echo ""

    local backups=$(ls -lt "$BACKUP_DIR"/${backup_type}_*.{sql.gz,rdb.gz,tar.gz} 2>/dev/null | head -10)

    if [ -z "$backups" ]; then
        log_warning "未找到 $backup_type 备份文件"
        return 1
    fi

    echo "$backups" | awk '{print NR". "$9" ("$6" "$7" "$8")"}'
    echo ""
}

# ============= PostgreSQL 恢复 =============
restore_postgresql() {
    local backup_file=$1

    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        return 1
    fi

    log_warning "警告: 这将覆盖数据库 $PG_DB 的所有数据！"
    read -p "是否继续? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        log "恢复已取消"
        return 1
    fi

    log "开始恢复 PostgreSQL 数据库..."

    # 终止所有连接
    psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d postgres -c \
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$PG_DB';" \
        2>/dev/null || true

    # 删除并重建数据库
    psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d postgres -c "DROP DATABASE IF EXISTS $PG_DB;"
    psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d postgres -c "CREATE DATABASE $PG_DB;"

    # 恢复数据
    if gunzip -c "$backup_file" | psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB"; then
        log_success "PostgreSQL 恢复完成"
        return 0
    else
        log_error "PostgreSQL 恢复失败"
        return 1
    fi
}

# ============= Redis 恢复 =============
restore_redis() {
    local backup_file=$1

    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        return 1
    fi

    log_warning "警告: 这将覆盖 Redis 的所有数据！"
    read -p "是否继续? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        log "恢复已取消"
        return 1
    fi

    log "开始恢复 Redis..."

    # 停止 Redis
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" SHUTDOWN NOSAVE || true
    sleep 2

    # 解压并复制 RDB 文件
    local redis_rdb="/var/lib/redis/dump.rdb"
    gunzip -c "$backup_file" > "$redis_rdb"

    # 启动 Redis
    redis-server --daemonize yes --dir /var/lib/redis
    sleep 2

    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" PING; then
        log_success "Redis 恢复完成"
        return 0
    else
        log_error "Redis 启动失败"
        return 1
    fi
}

# ============= 向量数据库恢复 =============
restore_vector_db() {
    local backup_file=$1
    local vector_db_path="/data/vector_db"

    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        return 1
    fi

    log_warning "警告: 这将覆盖向量数据库的所有数据！"
    read -p "是否继续? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        log "恢复已取消"
        return 1
    fi

    log "开始恢复向量数据库..."

    # 备份当前数据（以防万一）
    if [ -d "$vector_db_path" ]; then
        mv "$vector_db_path" "${vector_db_path}.old.$(date +%s)"
    fi

    # 解压恢复
    mkdir -p "$(dirname "$vector_db_path")"
    if tar -xzf "$backup_file" -C "$(dirname "$vector_db_path")"; then
        log_success "向量数据库恢复完成"
        return 0
    else
        log_error "向量数据库恢复失败"
        return 1
    fi
}

# ============= 交互式恢复 =============
interactive_restore() {
    echo "=========================================="
    echo "AI Agent 数据恢复工具"
    echo "=========================================="
    echo ""
    echo "请选择要恢复的组件:"
    echo "1. PostgreSQL 数据库"
    echo "2. Redis 缓存"
    echo "3. 向量数据库"
    echo "4. 全部恢复"
    echo "0. 退出"
    echo ""
    read -p "请选择 (0-4): " choice

    case $choice in
        1)
            list_backups "postgres"
            read -p "请输入备份文件路径: " backup_file
            restore_postgresql "$backup_file"
            ;;
        2)
            list_backups "redis"
            read -p "请输入备份文件路径: " backup_file
            restore_redis "$backup_file"
            ;;
        3)
            list_backups "vector_db"
            read -p "请输入备份文件路径: " backup_file
            restore_vector_db "$backup_file"
            ;;
        4)
            log "开始全量恢复..."

            # 查找最新的备份文件
            local latest_pg=$(ls -t "$BACKUP_DIR"/postgres_*.sql.gz 2>/dev/null | head -1)
            local latest_redis=$(ls -t "$BACKUP_DIR"/redis_*.rdb.gz 2>/dev/null | head -1)
            local latest_vector=$(ls -t "$BACKUP_DIR"/vector_db_*.tar.gz 2>/dev/null | head -1)

            [ -n "$latest_pg" ] && restore_postgresql "$latest_pg"
            [ -n "$latest_redis" ] && restore_redis "$latest_redis"
            [ -n "$latest_vector" ] && restore_vector_db "$latest_vector"
            ;;
        0)
            log "退出"
            exit 0
            ;;
        *)
            log_error "无效选择"
            exit 1
            ;;
    esac
}

# ============= 主函数 =============
main() {
    # 检查备份目录
    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "备份目录不存在: $BACKUP_DIR"
        exit 1
    fi

    # 如果提供了参数，直接恢复；否则进入交互模式
    if [ $# -eq 0 ]; then
        interactive_restore
    else
        # 命令行模式
        local component=$1
        local backup_file=$2

        case $component in
            postgres|postgresql)
                restore_postgresql "$backup_file"
                ;;
            redis)
                restore_redis "$backup_file"
                ;;
            vector|vector_db)
                restore_vector_db "$backup_file"
                ;;
            *)
                log_error "未知组件: $component"
                echo "用法: $0 [postgres|redis|vector] <backup_file>"
                exit 1
                ;;
        esac
    fi
}

# 执行主函数
main "$@"
