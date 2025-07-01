import styled, { css } from 'styled-components';

export interface IconTextProps {
  icon: React.ReactNode;
  iconPlacement?: 'left' | 'right';
  className?: string;
  style?: React.CSSProperties;
  children: React.ReactNode;
}

const IconTextWrapper = styled.div.attrs<Pick<IconTextProps, 'className'>>({
  className: 'icon-text',
})`
  display: flex;
  align-items: center;

  .icon {
    ${({ iconPlacement }: Pick<IconTextProps, 'iconPlacement'>) =>
      iconPlacement === 'left'
        ? css`
            margin-right: 0.25rem;
          `
        : css`
            margin-left: 0.25rem;
          `}
  }
`;

// TODO: 后期将其移动到设计系统中，所以这里使用 styled-components 管理样式
export default function IconText({ className, style, icon = null, iconPlacement = 'left', children }: IconTextProps) {
  const comps = [
    <div key="icon" className="icon">
      {icon}
    </div>,
    <div key="text" className="text">
      {children}
    </div>,
  ];

  if (iconPlacement === 'right') {
    comps.reverse();
  }
  return (
    <IconTextWrapper className={className} style={style} iconPlacement={iconPlacement}>
      {comps}
    </IconTextWrapper>
  );
}
