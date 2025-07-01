import type { SwitchProps } from 'antd';
import { Switch } from 'antd';

export interface FancyBooleanProps extends SwitchProps {
  value: boolean;
  antProps: SwitchProps;
}

export function FancyBoolean({ antProps, value, ...rest }: FancyBooleanProps) {
  return <Switch {...antProps} checked={value} {...rest} />;
}
