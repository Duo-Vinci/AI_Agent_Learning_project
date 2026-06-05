// K6 负载测试脚本
// 用于性能测试和压力测试

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');

// 测试配置
export const options = {
    // 测试阶段
    stages: [
        { duration: '30s', target: 10 },   // 30秒内逐步增加到 10 个虚拟用户
        { duration: '1m', target: 50 },    // 1分钟内增加到 50 个虚拟用户
        { duration: '2m', target: 100 },   // 2分钟内增加到 100 个虚拟用户
        { duration: '1m', target: 50 },    // 1分钟内降到 50 个虚拟用户
        { duration: '30s', target: 0 },    // 30秒内降到 0
    ],

    // 性能阈值
    thresholds: {
        http_req_duration: ['p(95)<500', 'p(99)<1000'],  // 95% 请求 < 500ms, 99% < 1s
        http_req_failed: ['rate<0.01'],  // 错误率 < 1%
        errors: ['rate<0.05'],  // 自定义错误率 < 5%
    },
};

// 测试环境变量
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// 测试数据
const queries = [
    'What is AI?',
    'Explain machine learning',
    'How does deep learning work?',
    'What is natural language processing?',
    'Tell me about neural networks'
];

// 主测试函数
export default function() {
    // 1. 健康检查
    const healthRes = http.get(`${BASE_URL}/health`);
    check(healthRes, {
        'health check status is 200': (r) => r.status === 200,
        'health check response time < 200ms': (r) => r.timings.duration < 200,
    }) || errorRate.add(1);

    sleep(1);

    // 2. API 状态检查
    const statusRes = http.get(`${BASE_URL}/api/v1/status`);
    check(statusRes, {
        'status check is 200': (r) => r.status === 200,
        'status is operational': (r) => JSON.parse(r.body).status === 'operational',
    }) || errorRate.add(1);

    sleep(1);

    // 3. Agent 查询
    const randomQuery = queries[Math.floor(Math.random() * queries.length)];
    const payload = JSON.stringify({ query: randomQuery });
    const params = {
        headers: { 'Content-Type': 'application/json' },
    };

    const agentRes = http.post(`${BASE_URL}/api/v1/agent`, payload, params);
    check(agentRes, {
        'agent response is 200': (r) => r.status === 200,
        'agent response time < 1000ms': (r) => r.timings.duration < 1000,
        'agent response has status': (r) => JSON.parse(r.body).status === 'success',
    }) || errorRate.add(1);

    sleep(2);
}

// 测试开始时执行
export function setup() {
    console.log(`Starting load test on ${BASE_URL}`);

    // 预热请求
    const warmupRes = http.get(`${BASE_URL}/health`);
    if (warmupRes.status !== 200) {
        throw new Error('Service is not ready');
    }
}

// 测试结束时执行
export function teardown(data) {
    console.log('Load test completed');
}
