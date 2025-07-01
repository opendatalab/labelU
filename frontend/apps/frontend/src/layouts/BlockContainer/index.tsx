import styled from 'styled-components';

const StyledContainer = styled.div`
  padding: 0 1.5rem;
`;
export default function BlockContainer({
  children,
  className,
  style,
}: React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement>) {
  return (
    <StyledContainer style={style} className={className}>
      {children}
    </StyledContainer>
  );
}
