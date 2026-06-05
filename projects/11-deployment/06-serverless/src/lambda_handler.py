"""
AWS Lambda 部署 - Serverless
使用 Mangum 将 FastAPI 应用适配为 Lambda 函数
"""

import json
from mangum import Mangum
from typing import Dict, Any

# 导入 FastAPI 应用
try:
    from app.main import app
except ImportError:
    # 如果在 Lambda 环境中
    import sys
    sys.path.append('/var/task')
    from app.main import app


# 创建 Lambda handler
# Mangum 会自动将 Lambda 事件转换为 ASGI 请求
handler = Mangum(app, lifespan="off")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda 入口函数

    Args:
        event: Lambda 事件对象
        context: Lambda 上下文对象

    Returns:
        Lambda 响应对象
    """
    print(f"收到事件: {json.dumps(event)}")

    # 使用 Mangum 处理请求
    response = handler(event, context)

    print(f"返回响应: {json.dumps(response)}")

    return response


# 冷启动优化
def warm_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    预热处理器 - 减少冷启动时间
    """
    if event.get('source') == 'aws.events':
        # CloudWatch Events 定期触发的预热请求
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'warm'})
        }

    return lambda_handler(event, context)


if __name__ == "__main__":
    # 本地测试
    import uvicorn

    print("本地运行模式 - 使用 uvicorn")
    uvicorn.run(app, host="0.0.0.0", port=8000)
