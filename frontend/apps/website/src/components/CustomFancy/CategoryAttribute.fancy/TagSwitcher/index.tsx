import { SwapOutlined } from '@ant-design/icons';
import { Tag } from 'antd';
import { useCallback, useState } from 'react';
import styled from 'styled-components';

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
  titleMapping = { true: '开', false: '关' },
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
