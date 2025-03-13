import type { InputNumberProps } from 'antd';
import { InputNumber } from 'antd';

export interface FancyNumberProps {
  antProps: InputNumberProps;
}

export function FancyNumber({ antProps, ...props }: FancyNumberProps) {
  return <InputNumber {...antProps} {...props} />;
}
