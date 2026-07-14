import React, { useEffect, useState } from 'react';
import { Table, Tag, Typography, Button, Space, Modal } from 'antd';
import { ReloadOutlined, VideoCameraOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title } = Typography;

interface Task {
    id: number;
    title: string;
    status: string;
    output_url?: string;
}

const TaskList: React.FC = () => {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [videoModalVisible, setVideoModalVisible] = useState(false);
    const [currentVideoUrl, setCurrentVideoUrl] = useState<string>('');

    const fetchTasks = async () => {
        setLoading(true);
        try {
            const response = await axios.get('/api/tasks');
            // 假设 API 返回一个数组
            if (Array.isArray(response.data)) {
                setTasks(response.data);
            }
        } catch (error) {
            console.error('Failed to fetch tasks', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTasks();
        // 简单轮询（因为 MVP 阶段 WebSocket 可能尚未完全连通到前端状态流转）
        const interval = setInterval(fetchTasks, 3000);
        return () => clearInterval(interval);
    }, []);

    const showVideo = (url: string) => {
        setCurrentVideoUrl(url);
        setVideoModalVisible(true);
    };

    const columns = [
        {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
        },
        {
            title: '任务名称',
            dataIndex: 'title',
            key: 'title',
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => {
                let color = 'default';
                if (status === 'done') color = 'success';
                else if (status === 'failed') color = 'error';
                else if (status !== 'pending') color = 'processing';
                return <Tag color={color}>{status.toUpperCase()}</Tag>;
            },
        },
        {
            title: '操作',
            key: 'action',
            render: (_: any, record: Task) => (
                <Space size="middle">
                    {record.status === 'done' && record.output_url && (
                        <Button 
                            type="link" 
                            icon={<VideoCameraOutlined />}
                            onClick={() => showVideo(record.output_url!)}
                        >
                            查看成片
                        </Button>
                    )}
                </Space>
            ),
        },
    ];

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <Title level={2} style={{ margin: 0 }}>任务队列</Title>
                <Button icon={<ReloadOutlined />} onClick={fetchTasks} loading={loading}>
                    刷新
                </Button>
            </div>
            <Table dataSource={tasks} columns={columns} rowKey="id" loading={loading} />

            <Modal
                title="视频预览"
                open={videoModalVisible}
                onCancel={() => {
                    setVideoModalVisible(false);
                    setCurrentVideoUrl('');
                }}
                footer={null}
                width={400}
                destroyOnClose
            >
                {currentVideoUrl && (
                    <video 
                        controls 
                        autoPlay 
                        style={{ width: '100%', borderRadius: 8 }}
                        src={currentVideoUrl}
                    >
                        Your browser does not support the video tag.
                    </video>
                )}
            </Modal>
        </div>
    );
};

export default TaskList;
