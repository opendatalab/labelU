import type { InputProps } from 'antd';
import { Input } from 'antd';
import type { TextAreaProps } from 'antd/es/input';

export interface FancyStringProps extends InputProps {
  alias?: 'input' | 'textarea';
  antProps: InputProps | TextAreaProps;
}

export function FancyString({ alias = 'input', antProps }: FancyStringProps) {
  if (alias === 'input') {
    return <Input {...(antProps as InputProps)} />;
  }

  return <Input.TextArea {...(antProps as TextAreaProps)} />;
}
