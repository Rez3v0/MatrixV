import React from 'react';
import { Table, Tag, Button } from 'antd';
import { useTaskStatus } from '../hooks/useTaskStatus';
import { useWebSocket } from '../hooks/useWebSocket';

const TaskList: React.FC = () => {
  const { status: wsStatus } = useWebSocket('ws://localhost:8000/ws');
  
  // Mocking task 1 status updates
  const task1Status = useTaskStatus(1);

  const dataSource = [
    { key: '1', id: 1, name: '热点新闻改写', status: task1Status, agent: 'Agent 1-5' },
    { key: '2', id: 2, name: '搞笑段子搬运', status: 'done', agent: 'Agent 6' },
  ];

  const columns = [
    { title: 'Task ID', dataIndex: 'id', key: 'id' },
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { 
      title: 'Status', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => {
        let color = 'blue';
        if (status === 'done') color = 'green';
        if (status === 'failed') color = 'red';
        return <Tag color={color}>{status.toUpperCase()}</Tag>;
      }
    },
    { title: 'Agent', dataIndex: 'agent', key: 'agent' },
    {
      title: 'Action',
      key: 'action',
      render: () => <Button type="link">View Logs</Button>,
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <h1>Task List</h1>
      <div style={{ marginBottom: 16 }}>
        <strong>WebSocket Status: </strong>
        <Tag color={wsStatus === 'Connected' ? 'green' : 'orange'}>{wsStatus}</Tag>
      </div>
      <Table dataSource={dataSource} columns={columns} />
    </div>
  );
};

export default TaskList;
