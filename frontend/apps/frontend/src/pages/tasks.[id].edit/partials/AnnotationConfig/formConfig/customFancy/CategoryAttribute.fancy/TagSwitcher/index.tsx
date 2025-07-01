import { SwapOutlined } from '@ant-design/icons';
import { Tag } from 'antd';
import { useCallback, useState } from 'react';
import styled from 'styled-components';
import { i18n } from '@labelu/i18n';

export interface TagSwitcherProps {
  value?: boolean;
  disabled?: boolean;
  onChange: (value: boolean) => void;
  titleMapping?: Record<string, string>;
}

const TagWrapper = styled(Tag)`
  margin: 0;
  cursor: pointer;
`;

export default function TagSwitcher({
  value = false,
  disabled,
  onChange,
  titleMapping = { true: i18n.t('on'), false: i18n.t('off') },
}: TagSwitcherProps) {
  const [open, setOpen] = useState(value);

  const handleChange = useCallback(() => {
    setOpen((pre) => {
      onChange?.(!pre);

      return !pre;
    });
  }, [onChange]);

  return (
    <TagWrapper onClick={!disabled ? handleChange : undefined}>
      {titleMapping[String(open)]} <SwapOutlined />
    </TagWrapper>
  );
}
