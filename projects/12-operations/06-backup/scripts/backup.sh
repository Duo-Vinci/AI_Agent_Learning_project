#!/bin/bash

# AI Agent 数据库备份脚本
# 支持 PostgreSQL、Redis、向量数据库等

set -e  # 遇到错误立即退出

# ============= 配置 =============
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7  # 保留天数

# AWS S3 配置（可选）
S3_BUCKET="s3://my-agent-backups"
ENABLE_S3_UPLOAD=false

# 数据库配置
PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5432}"
PG_USER="${PG_USER:-postgres}"
PG_DB="${PG_DB:-agentdb}"

REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

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

# ============= PostgreSQL 备份 =============
backup_postgresql() {
    log "开始备份 PostgreSQL 数据库..."

    local backup_file="$BACKUP_DIR/postgres_${PG_DB}_${TIMESTAMP}.sql.gz"

    if pg_dump -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" "$PG_DB" | gzip > "$backup_file"; then
        local size=$(du -h "$backup_file" | cut -f1)
        log_success "PostgreSQL 备份完成: $backup_file ($size)"
        echo "$backup_file"
    else
        log_error "PostgreSQL 备份失败"
        return 1
    fi
}

# ============= Redis 备份 =============
backup_redis() {
    log "开始备份 Redis..."

    local backup_file="$BACKUP_DIR/redis_${TIMESTAMP}.rdb"

    # 触发 Redis BGSAVE
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" BGSAVE; then
        # 等待备份完成
        sleep 2

        # 复制 RDB 文件
        local redis_rdb="/var/lib/redis/dump.rdb"
        if [ -f "$redis_rdb" ]; then
            cp "$redis_rdb" "$backup_file"
            gzip "$backup_file"
            log_success "Redis 备份完成: ${backup_file}.gz"
            echo "${backup_file}.gz"
        else
            log_error "找不到 Redis RDB 文件"
            return 1
        fi
    else
        log_error "Redis 备份失败"
        return 1
    fi
}

# ============= 向量数据库备份 =============
backup_vector_db() {
    log "开始备份向量数据库（FAISS/Chroma）..."

    local vector_db_path="/data/vector_db"
    local backup_file="$BACKUP_DIR/vector_db_${TIMESTAMP}.tar.gz"

    if [ -d "$vector_db_path" ]; then
        if tar -czf "$backup_file" -C "$(dirname "$vector_db_path")" "$(basename "$vector_db_path")"; then
            local size=$(du -h "$backup_file" | cut -f1)
            log_success "向量数据库备份完成: $backup_file ($size)"
            echo "$backup_file"
        else
            log_error "向量数据库备份失败"
            return 1
        fi
    else
        log "跳过向量数据库备份（路径不存在）"
    fi
}

# ============= 应用配置备份 =============
backup_configs() {
    log "开始备份应用配置..."

    local config_dirs="/app/config /etc/agent"
    local backup_file="$BACKUP_DIR/configs_${TIMESTAMP}.tar.gz"

    # 查找存在的配置目录
    local existing_dirs=""
    for dir in $config_dirs; do
        if [ -d "$dir" ]; then
            existing_dirs="$existing_dirs $dir"
        fi
    done

    if [ -n "$existing_dirs" ]; then
        if tar -czf "$backup_file" $existing_dirs 2>/dev/null; then
            log_success "配置文件备份完成: $backup_file"
            echo "$backup_file"
        else
            log_error "配置文件备份失败"
            return 1
        fi
    else
        log "跳过配置备份（未找到配置目录）"
    fi
}

# ============= 上传到 S3 =============
upload_to_s3() {
    local file=$1

    if [ "$ENABLE_S3_UPLOAD" = true ]; then
        log "上传备份到 S3: $file"

        if aws s3 cp "$file" "$S3_BUCKET/$(basename "$file")"; then
            log_success "上传成功: $S3_BUCKET/$(basename "$file")"
        else
            log_error "S3 上传失败: $file"
            return 1
        fi
    fi
}

# ============= 清理旧备份 =============
cleanup_old_backups() {
    log "清理 $RETENTION_DAYS 天前的旧备份..."

    local deleted_count=$(find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete -print | wc -l)

    if [ "$deleted_count" -gt 0 ]; then
        log_success "已删除 $deleted_count 个旧备份文件"
    else
        log "没有需要清理的旧备份"
    fi
}

# ============= 备份验证 =============
verify_backup() {
    local file=$1

    log "验证备份文件: $(basename "$file")"

    if [ ! -f "$file" ]; then
        log_error "备份文件不存在: $file"
        return 1
    fi

    # 检查文件大小
    local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    if [ "$size" -lt 1024 ]; then
        log_error "备份文件太小，可能损坏: $size bytes"
        return 1
    fi

    # 测试压缩文件完整性
    if [[ "$file" == *.gz ]]; then
        if ! gzip -t "$file" 2>/dev/null; then
            log_error "备份文件损坏（gzip 测试失败）"
            return 1
        fi
    fi

    log_success "备份文件验证通过"
    return 0
}

# ============= 生成备份报告 =============
generate_report() {
    local report_file="$BACKUP_DIR/backup_report_${TIMESTAMP}.txt"

    cat > "$report_file" << EOF
=====================================
AI Agent 备份报告
=====================================
备份时间: $(date)
备份目录: $BACKUP_DIR

备份文件:
$(ls -lh "$BACKUP_DIR" | grep "$TIMESTAMP")

磁盘使用情况:
$(df -h "$BACKUP_DIR")

总备份大小: $(du -sh "$BACKUP_DIR" | cut -f1)
=====================================
EOF

    cat "$report_file"
}

# ============= 主函数 =============
main() {
    log "==============================================="
    log "开始 AI Agent 数据备份"
    log "==============================================="

    local backup_files=()
    local failed=false

    # 执行各项备份
    if file=$(backup_postgresql); then
        backup_files+=("$file")
    else
        failed=true
    fi

    if file=$(backup_redis); then
        backup_files+=("$file")
    else
        failed=true
    fi

    if file=$(backup_vector_db); then
        backup_files+=("$file")
    fi

    if file=$(backup_configs); then
        backup_files+=("$file")
    fi

    # 验证备份
    log ""
    log "验证备份文件..."
    for file in "${backup_files[@]}"; do
        verify_backup "$file" || failed=true
    done

    # 上传到 S3
    if [ "$ENABLE_S3_UPLOAD" = true ]; then
        log ""
        log "上传备份到 S3..."
        for file in "${backup_files[@]}"; do
            upload_to_s3 "$file"
        done
    fi

    # 清理旧备份
    log ""
    cleanup_old_backups

    # 生成报告
    log ""
    generate_report

    # 最终状态
    log ""
    log "==============================================="
    if [ "$failed" = true ]; then
        log_error "备份完成（部分失败）"
        exit 1
    else
        log_success "备份全部完成"
        exit 0
    fi
}

# 执行主函数
main
