import styled from 'styled-components';
import { Button } from 'antd';
import { FlexLayout } from '@labelu/components-react';

export const LoginWrapper = styled(FlexLayout)`
  height: 100vh;

  .ant-input-affix-wrapper {
    border-radius: 8px;
    border: 1px solid rgb(0 0 0 / 10%);
    height: 3rem;
  }
`;

export const FormWrapper = styled(FlexLayout.Item)`
  width: 380px;

  h1 {
    text-align: center;
  }

  .ant-form-item {
    margin-bottom: 1rem;
  }
`;

export const ButtonWrapper = styled(Button)`
  height: 3rem;
  border-radius: 8px;
  margin-top: 1rem;
`;
