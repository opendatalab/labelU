import type { TooltipProps } from 'antd';
import { Avatar, Tooltip } from 'antd';
import { useMemo, useState } from 'react';
import { FlexLayout } from '@labelu/components-react';

import type { UserResponse } from '@/api/types';

export interface UserAvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  user?: UserResponse;
  showTooltip?: boolean;
  style?: React.CSSProperties;
  shortName?: boolean;
  placement?: TooltipProps['placement'];
}

export function UserAvatar({
  user,
  showTooltip = true,
  shortName = true,
  style,
  placement,
  ...props
}: UserAvatarProps) {
  const [open, setOpen] = useState(false);

  const content = useMemo(() => {
    return (
      <Tooltip title={user?.username} open={showTooltip && open} onOpenChange={setOpen} placement={placement}>
        {/* @ts-ignore */}
        <Avatar
          size="small"
          style={{ backgroundColor: 'rgba(230, 242, 255, 1)', color: 'rgba(18, 19, 22, 0.8)', ...style }}
          {...props}
        >
          {user?.username?.[0]?.toUpperCase() ?? 'U'}
        </Avatar>
      </Tooltip>
    );
  }, [user?.username, showTooltip, open, placement, style, props]);

  if (!shortName) {
    return (
      <FlexLayout flex="row" items="center" gap=".5rem" {...props}>
        {content}
        {user?.username}
      </FlexLayout>
    );
  }

  return content;
}
