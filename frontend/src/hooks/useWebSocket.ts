import { useState, useEffect } from 'react';

export function useWebSocket(url: string) {
  const [messages, setMessages] = useState<any[]>([]);
  const [status, setStatus] = useState<string>('Connecting...');

  useEffect(() => {
    // 模拟 WebSocket 骨架
    setStatus('Connected');
    
    // 模拟接收消息
    const timer = setInterval(() => {
      setMessages(prev => [...prev, { time: new Date().toISOString(), data: 'mock status update' }]);
    }, 5000);

    return () => {
      setStatus('Disconnected');
      clearInterval(timer);
    };
  }, [url]);

  return { messages, status };
}
