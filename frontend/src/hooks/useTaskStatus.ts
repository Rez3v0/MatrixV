import { useState, useEffect } from 'react';

export function useTaskStatus(taskId: number | null) {
  const [status, setStatus] = useState<string>('unknown');
  
  useEffect(() => {
    if (!taskId) return;
    
    // 模拟轮询获取任务状态
    setStatus('pending');
    const timer = setInterval(() => {
      setStatus(prev => {
        if (prev === 'pending') return 'scraping';
        if (prev === 'scraping') return 'writing';
        if (prev === 'writing') return 'rendering';
        if (prev === 'rendering') return 'publishing';
        if (prev === 'publishing') return 'done';
        return prev;
      });
    }, 3000);

    return () => clearInterval(timer);
  }, [taskId]);

  return status;
}
