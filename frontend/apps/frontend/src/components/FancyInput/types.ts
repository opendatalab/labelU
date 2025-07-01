import type { FormInstance, FormItemProps, Rule } from 'antd/es/form';
import type { NamePath } from 'antd/es/form/interface';

export interface FancyItemIdentifier {
  /** form field type */
  type: string;
  /** form field name */
  field: string;
  /** uniq key */
  key: string;
  label: string;
  initialValue: any;
  children?: FancyItemIdentifier[];
  hidden?: boolean;
  rules?: Rule[];
  layout?: 'horizontal' | 'vertical';
  /** antd input component props, only in template definition */
  antProps?: Record<string, unknown>;

  dependencies?: (string | number)[];
  fieldProps?: FormItemProps;

  disabled?: boolean;

  tooltip?: string;

  renderFormItem?: (params: FancyItemIdentifier, form: FormInstance, fullField: NamePath) => React.ReactNode;
  renderGroup?: (params: FancyItemIdentifier, form: FormInstance, fullField: NamePath) => React.ReactNode;
}

export interface FancyInputProps {
  type: string;
  [key: string]: any;
}
