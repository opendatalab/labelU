import styled from 'styled-components';
import { FlexLayout } from '@labelu/components-react';

export const StepRow = styled(FlexLayout.Header)`
  background: #fff;
  height: 56px;
  padding: 0 1.5rem;
`;

export const ContentWrapper = styled(FlexLayout.Content)`
  background-color: white;
  border-top: 1px solid var(--color-border-secondary);
`;

export const PreviewFrame = styled.iframe`
  flex: 1 auto;
  border: 0;
`;
