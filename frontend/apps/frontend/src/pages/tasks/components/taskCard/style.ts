import styled from 'styled-components';
import { FlexLayout } from '@labelu/components-react';

export const Row = styled(FlexLayout.Header)`
  display: flex;
  gap: 0.5rem;
  font-size: 14px;
`;

export const ActionRow = styled(FlexLayout)`
  opacity: 0;
  color: #a3a3a3;
  font-size: 1rem;
  gap: 0.5rem;
`;

export const MediaBadge = styled.div<{ color: string; bg: string }>`
  color: ${(props) => props.color};
  background-color: ${(props) => props.bg};
  padding: 0 0.25rem;
  height: 22px;
  line-height: 22px;
  border-radius: 2px;
  font-weight: 400;
  font-size: 14px;
  text-align: center;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

export const CardWrapper = styled(FlexLayout)`
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  border: 1px solid #fff;
  background-color: #fff;
  border-radius: 8px;
  cursor: pointer;
  padding: 1.25rem 1.5rem;
  min-height: 10rem;
  box-sizing: border-box;

  &:hover {
    border: 1px solid var(--color-primary);

    ${ActionRow} {
      opacity: 1;
    }
  }
`;

export const TaskName = styled.div`
  font-weight: 500;
  font-size: 18px;
  color: rgb(0 0 0 / 87%);
`;
