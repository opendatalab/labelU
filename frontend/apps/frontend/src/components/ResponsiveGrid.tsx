import styled, { css } from 'styled-components';

import { useGridSizeByPage } from '@/hooks/useGridSizeByPage';

export interface ResponsiveGridProps {
  className?: string;
  style?: React.CSSProperties;
}

const GridWrapper = styled.div<{
  size: number;
}>`
  display: grid;
  gap: 1rem;

  ${({ size }) => css`
    grid-template-columns: repeat(${size}, 1fr);
    grid-template-rows: repeat(4, 1fr);
  `}
`;

export function ResponsiveGrid({ children, style, className }: React.PropsWithChildren<ResponsiveGridProps>) {
  const gridSize = useGridSizeByPage();

  return (
    <GridWrapper size={gridSize} style={style} className={className}>
      {children}
    </GridWrapper>
  );
}
