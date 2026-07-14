import React from 'react';
import { Card, Row, Col, Statistic, Table } from 'antd';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const dataSource = [
    { key: '1', name: '抖音项目A', status: 'rendering', time: '10 mins' },
    { key: '2', name: '小红书项目B', status: 'done', time: '1 hour' },
  ];

  const columns = [
    { title: 'Project Name', dataIndex: 'name', key: 'name' },
    { title: 'Status', dataIndex: 'status', key: 'status' },
    { title: 'Time Elapsed', dataIndex: 'time', key: 'time' },
    { 
      title: 'Action', 
      key: 'action', 
      render: () => <Link to="/tasks">View Tasks</Link> 
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <h1>Dashboard</h1>
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic title="Total Tasks" value={112} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="Running" value={3} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic title="Failed" value={1} valueStyle={{ color: '#cf1322' }} />
          </Card>
        </Col>
      </Row>
      
      <h2 style={{ marginTop: '24px' }}>Recent Projects</h2>
      <Table dataSource={dataSource} columns={columns} />
    </div>
  );
};

export default Dashboard;
