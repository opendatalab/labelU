import formatter from '@labelu/formatter';
import { Popover, Tooltip } from 'antd';
import type { TooltipPropsWithTitle } from 'antd/lib/tooltip';
import React from 'react';
import styled from 'styled-components';
import type AnalyzeWiz from 'analyze-wiz';

import './analyze';

/**
 * 此文件用于应用初始化时的准备工作，比如一些注册处理函数，库的初始配置等
 */

declare global {
  interface Window {
    // 是否开发环境
    DEV: boolean;
    IS_ONLINE: boolean;

    AnalyzeWiz: typeof AnalyzeWiz;

    __backend: {
      version: string;
      build_time: string;
      name: 'labelu';
      commit: string;
    };
    __frontend: {
      version: string;
      deps: Record<string, string>;
    };
  }
}

// ==========================【formatter】=========================
const Ellipse = styled.span`
  flex: 1 1;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  display: inline-block;
  line-height: 100%;
`;

interface EllipseOption extends TooltipPropsWithTitle {
  maxWidth?: Pick<React.CSSProperties, 'maxWidth'> | string;
  maxLength: number;
  type?: 'tooltip' | 'popover';
}

formatter.add({
  type: 'ellipsis',
  name: '省略显示',
  format: (value: string, { maxWidth = '100%', type = 'popover', maxLength = 0, ...restProps }: EllipseOption) => {
    const Overlay = ({ children }: { children: React.ReactNode }) =>
      type === 'popover' ? (
        <Popover {...restProps} content={value}>
          {children}
        </Popover>
      ) : (
        <Tooltip {...restProps} title={value}>
          {children}
        </Tooltip>
      );
    if (maxLength > 0) {
      return value.length > maxLength ? <Overlay>{`${value.substr(0, maxLength)}...`}</Overlay> : value;
    }

    return (
      <Overlay>
        <Ellipse style={{ maxWidth } as React.CSSProperties}>{value}</Ellipse>
      </Overlay>
    );
  },
});
// ==========================【formatter】=========================
