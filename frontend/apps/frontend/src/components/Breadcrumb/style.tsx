import type { LinkProps } from 'react-router-dom';
import styled, { css } from 'styled-components';

import type { BreadcrumbProps } from './index';

const StyledBreadcrumb = styled.div.attrs((props: BreadcrumbProps) => ({
  ...props,
  className: 'breadcrumbs',
}))`
  display: flex;
  justify-content: flex-start;

  ${() =>
    window.IS_ONLINE
      ? css`
          font-size: 1rem;
        `
      : css`
          font-size: 14px;
        `}
  .breadcrumb-item-wrap {
    display: flex;
    align-items: center;
  }

  .breadcrumb-item-separator {
    margin: 0 0.5rem;
    color: rgba(0, 0, 0, 0.45);
  }
`;

export interface BreadcrumbItemProps extends LinkProps {
  isCurrent?: boolean;
}

export const BreadcrumbItem = styled.span.attrs((props: BreadcrumbItemProps) => ({
  ...props,
  className: 'breadcrumb-item',
}))`
  color: ${({ isCurrent }: BreadcrumbItemProps) => (isCurrent ? '#333' : '#999')};
  cursor: pointer;

  ${({ isCurrent }: BreadcrumbItemProps) =>
    !isCurrent &&
    css`
      &:hover {
        color: var(--color-primary);
      }
    `}
`;

export default StyledBreadcrumb;
