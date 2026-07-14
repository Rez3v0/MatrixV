import React, { useState } from 'react';
import { Card, Statistic, Row, Col, Typography, Button, message } from 'antd';
import { PlayCircleOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title } = Typography;

const Dashboard: React.FC = () => {
    const [loading, setLoading] = useState(false);

    const handleStartTask = async () => {
        setLoading(true);
        try {
            const response = await axios.post('/api/tasks/start');
            message.success(`任务已启动！任务ID: ${response.data.task_id}`);
        } catch (error) {
            message.error('启动任务失败，请检查后端服务。');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <Title level={2}>控制台概览</Title>
            <Row gutter={16} style={{ marginBottom: '24px' }}>
                <Col span={24}>
                    <Button 
                        type="primary" 
                        size="large"
                        icon={<PlayCircleOutlined />} 
                        onClick={handleStartTask}
                        loading={loading}
                    >
                        一键生成爆款视频
                    </Button>
                </Col>
            </Row>
            <Row gutter={16}>
                <Col span={8}>
                    <Card>
                        <Statistic title="今日生成视频数" value={0} />
                    </Card>
                </Col>
                <Col span={8}>
                    <Card>
                        <Statistic title="运行中的节点" value={5} />
                    </Card>
                </Col>
                <Col span={8}>
                    <Card>
                        <Statistic title="系统状态" value="Normal" valueStyle={{ color: '#3f8600' }} />
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

export default Dashboard;
