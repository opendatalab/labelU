import styled from 'styled-components';

const Wrapper = styled.div`
  border-top: 1px solid rgba(0, 0, 0, 0.16);
  width: 91px;
  height: 0px;
  margin: auto 1rem;
`;

export default function Separator() {
  return <Wrapper />;
}
