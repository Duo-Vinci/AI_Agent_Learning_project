"""
异步任务处理器 - SQS Worker
用于处理来自 SQS 队列的异步任务
"""

import json
import os
from typing import Dict, Any
import structlog

logger = structlog.get_logger()


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    SQS Worker Lambda 函数

    处理来自 SQS 队列的消息

    Args:
        event: SQS 事件对象，包含一批消息
        context: Lambda 上下文

    Returns:
        处理结果
    """
    logger.info("sqs_worker_triggered", record_count=len(event['Records']))

    successful = 0
    failed = 0
    failures = []

    # 处理每条消息
    for record in event['Records']:
        try:
            # 解析消息体
            message_body = json.loads(record['body'])

            # 提取任务信息
            task_type = message_body.get('task_type')
            task_data = message_body.get('data', {})

            logger.info(
                "processing_task",
                task_type=task_type,
                message_id=record['messageId']
            )

            # 根据任务类型处理
            result = process_task(task_type, task_data)

            logger.info(
                "task_completed",
                task_type=task_type,
                message_id=record['messageId'],
                result=result
            )

            successful += 1

        except Exception as e:
            logger.error(
                "task_failed",
                message_id=record['messageId'],
                error=str(e)
            )

            failed += 1
            failures.append({
                'itemIdentifier': record['messageId'],
                'message': str(e)
            })

    # 返回批处理结果
    response = {
        'statusCode': 200 if failed == 0 else 207,
        'body': json.dumps({
            'successful': successful,
            'failed': failed
        })
    }

    # 如果有失败的消息，返回失败列表（SQS 会重试）
    if failures:
        response['batchItemFailures'] = failures

    return response


def process_task(task_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理具体任务

    Args:
        task_type: 任务类型
        data: 任务数据

    Returns:
        处理结果
    """
    if task_type == 'generate_report':
        return generate_report(data)

    elif task_type == 'send_email':
        return send_email(data)

    elif task_type == 'process_data':
        return process_data(data)

    else:
        raise ValueError(f"Unknown task type: {task_type}")


def generate_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """生成报告"""
    logger.info("generating_report", data=data)

    # 实际的报告生成逻辑
    report_id = data.get('report_id')

    # 模拟处理
    return {
        'status': 'completed',
        'report_id': report_id,
        'output_url': f's3://bucket/reports/{report_id}.pdf'
    }


def send_email(data: Dict[str, Any]) -> Dict[str, Any]:
    """发送邮件"""
    logger.info("sending_email", recipient=data.get('to'))

    # 使用 AWS SES 发送邮件
    # import boto3
    # ses_client = boto3.client('ses')
    # ...

    return {
        'status': 'sent',
        'message_id': 'msg-123'
    }


def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """处理数据"""
    logger.info("processing_data", data_size=len(data))

    # 数据处理逻辑
    return {
        'status': 'processed',
        'records_processed': len(data)
    }


if __name__ == "__main__":
    # 本地测试
    test_event = {
        'Records': [
            {
                'messageId': 'test-msg-1',
                'body': json.dumps({
                    'task_type': 'generate_report',
                    'data': {
                        'report_id': 'report-123'
                    }
                })
            }
        ]
    }

    result = handler(test_event, None)
    print(json.dumps(result, indent=2))
