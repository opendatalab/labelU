import type { SelectProps } from 'antd';
import { Select } from 'antd';

export interface FancyEnumProps {
  antProps: SelectProps;
}

export function FancyEnum({ antProps, ...props }: FancyEnumProps) {
  return <Select {...antProps} {...props} />;
}
