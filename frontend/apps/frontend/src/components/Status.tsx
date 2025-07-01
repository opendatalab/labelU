import {
  CheckCircleFilled,
  ClockCircleFilled,
  CloseCircleFilled,
  ExclamationCircleFilled,
  LoadingOutlined,
} from '@ant-design/icons';
import { useMemo } from 'react';

import IconText from './IconText';

export type StatusType = 'success' | 'error' | 'warning' | 'waiting' | 'processing' | 'completed' | 'failed';

export interface StatusProps {
  type: StatusType;
  className?: string;
  tooltip?: string;
  icon?: React.ReactNode;
  style?: React.CSSProperties;
  color?: string;
  children: React.ReactNode;
}

const typeColorMapping = {
  success: 'var(--color-success)',
  error: 'var(--color-error)',
  warning: 'var(--color-warning)',
  waiting: 'var(--color-warning)',
  processing: 'var(--color-primary)',
  completed: 'var(--color-success)',
  failed: 'var(--color-error)',
  fail: 'var(--color-error)',
};

const typeIconMapping = {
  success: <CheckCircleFilled />,
  error: <CloseCircleFilled />,
  warning: <ExclamationCircleFilled />,
  waiting: <ClockCircleFilled />,
  processing: <LoadingOutlined />,
  completed: <CheckCircleFilled />,
  failed: <CloseCircleFilled />,
  fail: <CloseCircleFilled />,
};

export default function Status({
  type = 'processing',
  icon = typeIconMapping[type],
  className,
  children,
  ...restProps
}: StatusProps) {
  const color = restProps.color ?? typeColorMapping[type];
  const style = useMemo(() => ({ color, '--status-color': color, ...restProps.style }), [color, restProps.style]);

  return (
    <IconText className={className} icon={icon} style={style}>
      {children}
    </IconText>
  );
}
