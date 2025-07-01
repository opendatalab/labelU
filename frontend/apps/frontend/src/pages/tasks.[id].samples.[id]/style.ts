import styled, { css } from 'styled-components';
import { FlexLayout } from '@labelu/components-react';

export const Wrapper = styled<any>(FlexLayout.Content)`
  position: relative;

  ${({ loading }) =>
    loading &&
    css`
      filter: blur(0.5rem);
    `}
`;

export const LoadingWrapper = styled(FlexLayout.Content)`
  position: absolute;
  top: 0;
  left: 0;
  background-color: rgb(255 255 255 / 41%);
  z-index: 1000;
  width: 100%;
  height: 100%;
`;
