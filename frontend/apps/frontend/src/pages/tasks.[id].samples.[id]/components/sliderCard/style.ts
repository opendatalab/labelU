import styled, { css } from 'styled-components';
import { FlexLayout } from '@labelu/components-react';

export const ImageWrapper = styled(FlexLayout)`
  gap: 0.5rem;
  cursor: pointer;
  position: relative;
  width: 100%;
`;

export const AnnotatingUser = styled.div`
  position: absolute;
  z-index: 3;
  top: 0.5rem;
  left: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: #999;

  .annotating-text {
    color: #fff;
    text-shadow: 0 0 3px #000;
  }
`;

export const IdWrapper = styled.div`
  border-radius: 2px;
  padding: 0 0.25rem;
`;

export const SkipWrapper = styled.div`
  position: absolute;
  top: 0;
  right: 0;
  z-index: 1000;
  background: #f80;
  border-radius: 0 4px;
  width: 36px;
  height: 25px;
  color: white;
  text-align: center;
  font-weight: 400;
  font-size: 12px;
  line-height: 25px;
`;

export const ContentWrapper = styled<any>(FlexLayout.Content)`
  position: relative;
  max-height: 118px;
  background: #fff;
  overflow: hidden;

  /* & > * { */
  ${({ active }) =>
    active &&
    css`
      outline: 3px solid var(--color-primary);
    `}
  /* } */

  & > img, & > div {
    &:first-child {
      width: 200px;
      height: 120px;
      object-fit: cover;
    }
  }

  ${({ active }) =>
    active &&
    css`
      & + ${IdWrapper} {
        background: var(--color-primary);
        color: #fff;
      }
    `}
`;

export const CheckBg = styled.div`
  & > svg {
    position: absolute;
    top: 0.15rem;
    right: 0.15rem;
    font-size: 12px;
    z-index: 1001;
    color: #fff;
  }
`;

export const Triangle = styled.div`
  position: absolute;
  top: 0;
  right: 0;
  z-index: 1000;
  width: 0px;
  height: 0px;
  border-style: solid;
  border-width: 0 28px 28px 0;
  border-color: transparent var(--color-primary) transparent transparent;
  transform: rotate(0deg);
`;

export const AudioWrapper = styled(FlexLayout)`
  position: relative;
  overflow: hidden;
  margin-bottom: 10px;
  align-items: center;
  cursor: pointer;
  border-radius: 3px;
`;
