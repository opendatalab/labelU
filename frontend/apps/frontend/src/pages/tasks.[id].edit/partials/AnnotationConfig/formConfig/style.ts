import styled from 'styled-components';
import { Form } from 'antd';
import { FlexLayout } from '@labelu/components-react';

export const TabForm = styled(FlexLayout)`
  padding: 1rem;
  border: 1px solid var(--color-border-secondary);
  border-top: 0;
  border-radius: 0 0 var(--border-radius) var(--border-radius);

  & > .ant-form-item {
    margin-bottom: 0;
  }
`;

export const AttributeBox = styled.div`
  padding: 1rem;
  border: 1px solid var(--color-border-secondary);
  border-radius: var(--border-radius);
`;

export const ConfigForm = styled<any>(Form)`
  .ant-tabs-nav {
    margin-bottom: 0;
  }
`;

export const AttributeFormItem = styled(Form.Item)`
  .ant-form-item {
    margin-bottom: 0;
  }
`;
