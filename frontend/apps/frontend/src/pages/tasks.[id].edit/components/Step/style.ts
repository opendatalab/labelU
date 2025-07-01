import styled, { css } from 'styled-components';
import { FlexLayout } from '@labelu/components-react';

export const StepItemWrapper = styled(FlexLayout)`
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5rem;
`;

export const StepItemInner = styled<any>(FlexLayout.Item)`
  cursor: pointer;
  font-size: 14px;
`;

export const IconWrapper = styled<any>(FlexLayout.Item)`
  width: 24px;
  height: 24px;
  margin-right: 8px;
  border-radius: 50%;
  font-weight: 400;
  background: #f2f3f5;

  ${({ active }) =>
    active &&
    css`
      background: var(--color-primary) !important;
      color: #fff !important;
    `}

  ${({ finished }) =>
    finished &&
    css`
      background-color: rgb(27 103 255 / 10%);
      color: var(--color-primary);
    `}
`;
