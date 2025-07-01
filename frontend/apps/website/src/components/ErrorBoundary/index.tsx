import Result from 'antd/es/result';
import type { ErrorInfo } from 'react';
import React from 'react';

class ErrorBoundary extends React.Component<{ children?: React.ReactNode }, { hasError: boolean; errorInfo: string }> {
  state = { hasError: false, errorInfo: '' };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, errorInfo: error.message };
  }

  componentDidCatch(error: any, errorInfo: ErrorInfo) {
    // TODO: 上报错误到sentry
    console.log(error, errorInfo);
    const isRefreshed = Boolean(sessionStorage.getItem('error::refreshed'));

    // 如果遇到文件更新（比如升级）时，异步文件加载失败，刷新一次页面
    if (!isRefreshed) {
      sessionStorage.setItem('error::refreshed', 'true');
      window.location.reload();
    }
  }

  render() {
    if (this.state.hasError) {
      return <Result status="error" title="Something went wrong." extra={this.state.errorInfo} />;
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
