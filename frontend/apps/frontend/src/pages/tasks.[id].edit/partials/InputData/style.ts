import styled from 'styled-components';
import { FlexLayout } from '@labelu/components-react';

export const Header = styled(FlexLayout.Header)`
  height: 44px;
  background: #fafafa;
`;

export const Wrapper = styled(FlexLayout)`
  padding: 1.5rem 1.5rem 0;
`;

export const Bar = styled.span`
  width: 3px;
  height: 16px;
  background: var(--color-primary);
  border-radius: 10px;
  margin-right: 4px;
  margin-left: 16px;
`;

export const Left = styled(FlexLayout.Item)`
  width: 450px;
`;

export const Right = styled(FlexLayout.Content)`
  border-left: 1px solid rgb(0 0 0 / 5%);
  padding: 1.5rem 0 0 1.5rem;

  .ant-table-thead > tr > th {
    background: #fff;
  }
`;

export const UploadArea = styled(FlexLayout)`
  background: #fbfcff;
  border: 1px dashed #d0dfff;
  border-radius: 8px;
  padding: 1rem;
`;

export const ButtonWrapper = styled(FlexLayout.Footer)`
  font-size: 12px;
  color: var(--color-text-secondary);
`;

export const Spot = styled.span`
  width: 0.5rem;
  height: 0.5rem;
  display: inline-block;
  border-radius: 50%;
  background-color: var(--status-color);
`;
