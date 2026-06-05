"""
备份管理工具
提供备份和恢复的自动化管理
"""

import os
import subprocess
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import boto3
from botocore.exceptions import ClientError


class BackupManager:
    """备份管理器"""

    def __init__(
        self,
        backup_dir: str = "/backups",
        retention_days: int = 7,
        s3_bucket: Optional[str] = None
    ):
        """
        初始化备份管理器

        Args:
            backup_dir: 本地备份目录
            retention_days: 备份保留天数
            s3_bucket: S3 存储桶名称（可选）
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        self.s3_bucket = s3_bucket

        if s3_bucket:
            self.s3_client = boto3.client('s3')

    def create_backup(self, component: str) -> Dict:
        """
        创建备份

        Args:
            component: 组件名称 (postgres/redis/vector_db/configs)

        Returns:
            备份信息字典
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_info = {
            'component': component,
            'timestamp': timestamp,
            'status': 'started',
            'start_time': datetime.now().isoformat()
        }

        try:
            if component == 'postgres':
                backup_file = self._backup_postgresql(timestamp)
            elif component == 'redis':
                backup_file = self._backup_redis(timestamp)
            elif component == 'vector_db':
                backup_file = self._backup_vector_db(timestamp)
            elif component == 'configs':
                backup_file = self._backup_configs(timestamp)
            else:
                raise ValueError(f"未知组件: {component}")

            backup_info.update({
                'status': 'success',
                'backup_file': str(backup_file),
                'file_size': backup_file.stat().st_size,
                'end_time': datetime.now().isoformat()
            })

            # 上传到 S3
            if self.s3_bucket and backup_file.exists():
                self._upload_to_s3(backup_file)
                backup_info['s3_uploaded'] = True

            # 保存备份元数据
            self._save_backup_metadata(backup_info)

            return backup_info

        except Exception as e:
            backup_info.update({
                'status': 'failed',
                'error': str(e),
                'end_time': datetime.now().isoformat()
            })
            return backup_info

    def _backup_postgresql(self, timestamp: str) -> Path:
        """备份 PostgreSQL"""
        backup_file = self.backup_dir / f"postgres_{timestamp}.sql.gz"

        cmd = [
            'pg_dump',
            '-h', os.getenv('PG_HOST', 'localhost'),
            '-p', os.getenv('PG_PORT', '5432'),
            '-U', os.getenv('PG_USER', 'postgres'),
            os.getenv('PG_DB', 'agentdb')
        ]

        # 执行备份并压缩
        with open(backup_file, 'wb') as f:
            dump = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            subprocess.run(['gzip'], stdin=dump.stdout, stdout=f, check=True)
            dump.wait()

        return backup_file

    def _backup_redis(self, timestamp: str) -> Path:
        """备份 Redis"""
        backup_file = self.backup_dir / f"redis_{timestamp}.rdb.gz"

        # 触发 Redis BGSAVE
        subprocess.run(
            ['redis-cli', 'BGSAVE'],
            check=True,
            capture_output=True
        )

        # 等待备份完成
        import time
        time.sleep(2)

        # 复制并压缩 RDB 文件
        redis_rdb = Path('/var/lib/redis/dump.rdb')
        if redis_rdb.exists():
            subprocess.run(
                ['gzip', '-c', str(redis_rdb)],
                stdout=open(backup_file, 'wb'),
                check=True
            )

        return backup_file

    def _backup_vector_db(self, timestamp: str) -> Path:
        """备份向量数据库"""
        backup_file = self.backup_dir / f"vector_db_{timestamp}.tar.gz"
        vector_db_path = Path('/data/vector_db')

        if vector_db_path.exists():
            subprocess.run(
                ['tar', '-czf', str(backup_file), '-C',
                 str(vector_db_path.parent), vector_db_path.name],
                check=True
            )

        return backup_file

    def _backup_configs(self, timestamp: str) -> Path:
        """备份配置文件"""
        backup_file = self.backup_dir / f"configs_{timestamp}.tar.gz"
        config_dirs = ['/app/config', '/etc/agent']

        existing_dirs = [d for d in config_dirs if Path(d).exists()]

        if existing_dirs:
            subprocess.run(
                ['tar', '-czf', str(backup_file)] + existing_dirs,
                check=True
            )

        return backup_file

    def _upload_to_s3(self, file_path: Path):
        """上传文件到 S3"""
        try:
            self.s3_client.upload_file(
                str(file_path),
                self.s3_bucket,
                f"backups/{file_path.name}"
            )
            print(f"✓ 已上传到 S3: {self.s3_bucket}/backups/{file_path.name}")
        except ClientError as e:
            print(f"✗ S3 上传失败: {e}")

    def _save_backup_metadata(self, backup_info: Dict):
        """保存备份元数据"""
        metadata_file = self.backup_dir / "backup_metadata.jsonl"

        with open(metadata_file, 'a') as f:
            f.write(json.dumps(backup_info) + '\n')

    def list_backups(self, component: Optional[str] = None) -> List[Dict]:
        """
        列出备份

        Args:
            component: 组件名称（可选，用于过滤）

        Returns:
            备份列表
        """
        backups = []

        pattern = f"{component}_*" if component else "*"

        for file in self.backup_dir.glob(pattern):
            if file.is_file() and file.suffix in ['.gz', '.sql', '.rdb', '.tar']:
                backups.append({
                    'name': file.name,
                    'path': str(file),
                    'size': file.stat().st_size,
                    'created': datetime.fromtimestamp(
                        file.stat().st_mtime
                    ).isoformat()
                })

        return sorted(backups, key=lambda x: x['created'], reverse=True)

    def cleanup_old_backups(self) -> int:
        """
        清理过期备份

        Returns:
            删除的文件数量
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0

        for file in self.backup_dir.glob("*"):
            if file.is_file():
                file_time = datetime.fromtimestamp(file.stat().st_mtime)

                if file_time < cutoff_date:
                    file.unlink()
                    deleted_count += 1
                    print(f"已删除旧备份: {file.name}")

        return deleted_count

    def restore_backup(self, backup_file: str, component: str) -> bool:
        """
        恢复备份

        Args:
            backup_file: 备份文件路径
            component: 组件名称

        Returns:
            是否成功
        """
        file_path = Path(backup_file)

        if not file_path.exists():
            print(f"✗ 备份文件不存在: {backup_file}")
            return False

        try:
            if component == 'postgres':
                return self._restore_postgresql(file_path)
            elif component == 'redis':
                return self._restore_redis(file_path)
            elif component == 'vector_db':
                return self._restore_vector_db(file_path)
            elif component == 'configs':
                return self._restore_configs(file_path)
            else:
                print(f"✗ 未知组件: {component}")
                return False

        except Exception as e:
            print(f"✗ 恢复失败: {e}")
            return False

    def _restore_postgresql(self, backup_file: Path) -> bool:
        """恢复 PostgreSQL"""
        print(f"恢复 PostgreSQL: {backup_file}")

        # 解压并导入
        cmd = f"gunzip -c {backup_file} | psql -h localhost -U postgres agentdb"
        result = subprocess.run(cmd, shell=True, capture_output=True)

        return result.returncode == 0

    def _restore_redis(self, backup_file: Path) -> bool:
        """恢复 Redis"""
        print(f"恢复 Redis: {backup_file}")

        # 停止 Redis，替换 RDB，重启
        subprocess.run(['redis-cli', 'SHUTDOWN', 'NOSAVE'])

        redis_rdb = Path('/var/lib/redis/dump.rdb')
        subprocess.run(f"gunzip -c {backup_file} > {redis_rdb}", shell=True)

        subprocess.run(['redis-server', '--daemonize', 'yes'])

        return True

    def _restore_vector_db(self, backup_file: Path) -> bool:
        """恢复向量数据库"""
        print(f"恢复向量数据库: {backup_file}")

        vector_db_path = Path('/data/vector_db')

        # 备份当前数据
        if vector_db_path.exists():
            vector_db_path.rename(f"{vector_db_path}.old")

        # 解压恢复
        subprocess.run(
            ['tar', '-xzf', str(backup_file), '-C', str(vector_db_path.parent)],
            check=True
        )

        return True

    def _restore_configs(self, backup_file: Path) -> bool:
        """恢复配置文件"""
        print(f"恢复配置: {backup_file}")

        subprocess.run(['tar', '-xzf', str(backup_file), '-C', '/'], check=True)

        return True

    def verify_backup(self, backup_file: str) -> bool:
        """
        验证备份文件完整性

        Args:
            backup_file: 备份文件路径

        Returns:
            是否有效
        """
        file_path = Path(backup_file)

        if not file_path.exists():
            return False

        # 检查文件大小
        if file_path.stat().st_size < 1024:
            print(f"✗ 文件太小: {file_path.stat().st_size} bytes")
            return False

        # 测试 gzip 完整性
        if file_path.suffix == '.gz':
            result = subprocess.run(
                ['gzip', '-t', str(file_path)],
                capture_output=True
            )
            if result.returncode != 0:
                print("✗ 压缩文件损坏")
                return False

        print("✓ 备份文件验证通过")
        return True


# 使用示例
if __name__ == "__main__":
    manager = BackupManager(
        backup_dir="/backups",
        retention_days=7,
        s3_bucket=None  # 设置为实际的 S3 bucket 名称以启用
    )

    print("=== AI Agent 备份管理工具 ===\n")

    # 创建备份
    print("1. 创建备份...")
    components = ['postgres', 'redis', 'vector_db', 'configs']

    for component in components:
        result = manager.create_backup(component)
        status_icon = "✓" if result['status'] == 'success' else "✗"
        print(f"{status_icon} {component}: {result['status']}")

    # 列出备份
    print("\n2. 当前备份列表:")
    backups = manager.list_backups()
    for backup in backups[:5]:  # 显示最近5个
        size_mb = backup['size'] / (1024 * 1024)
        print(f"  - {backup['name']} ({size_mb:.2f} MB) - {backup['created']}")

    # 清理旧备份
    print("\n3. 清理旧备份...")
    deleted = manager.cleanup_old_backups()
    print(f"删除了 {deleted} 个过期备份")

    print("\n备份管理完成！")
