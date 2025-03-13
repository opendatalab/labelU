import { message } from "antd";

export function copy(value: object, successMessage: string) {
  // 检查是否在浏览器环境中
  if (typeof document === 'undefined') {
    return;
  }

  // 检查是否支持 clipboard API
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    // 复制到剪切板
    navigator.clipboard.writeText(JSON.stringify(value, null, 2))
      .then(() => {
        message.success(successMessage);
      })
      .catch((err) => {
        console.error('复制失败:', err);
        message.error('复制失败');
      });
  } else {
    // 浏览器环境但不支持 clipboard API 的情况
    message.warning('您的浏览器不支持自动复制');
    
    // 可选: 使用备用复制方法
    try {
      const textArea = document.createElement('textarea');
      textArea.value = JSON.stringify(value, null, 2);
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      message.success(successMessage);
    } catch (err) {
      console.error('备用复制方法失败:', err);
      message.error('复制失败');
    }
  }
}