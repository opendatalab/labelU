import type { HTMLAttributes, PropsWithChildren } from 'react';
import React, { createRef, useEffect } from 'react';
import type { RcFile } from 'antd/lib/upload/interface';
import styled from 'styled-components';
import Button from 'antd/es/button';
import type { ButtonProps } from 'antd/lib';

const Wrapper = styled(Button)`
  position: relative;
  overflow: hidden;
  display: inline;
  cursor: pointer;
  > input {
    opacity: 0;
    position: absolute;
    height: 100%;
    width: 100%;
    z-index: 10;
    top: 0;
    left: 0;
    cursor: pointer;
  }
`;

type UploadProps = Omit<HTMLAttributes<HTMLInputElement>, 'onChange'> &
  Omit<ButtonProps, 'onChange'> & {
    accept?: string;
    directory?: boolean;
    multiple?: boolean;
    onChange?: (files: RcFile[]) => void;
  };

const NativeUpload: React.FC<PropsWithChildren<UploadProps>> = (props) => {
  const inputRef = createRef<any>();
  const { children, directory, multiple, onChange, accept, ...req } = props;

  useEffect(() => {
    inputRef.current.webkitdirectory = directory;
    inputRef.current.multiple = multiple;
  }, [directory, inputRef, multiple]);

  return (
    <Wrapper {...req}>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        name="fileList"
        onChange={(e) => {
          onChange?.(Array.from(e.target.files || []) as RcFile[]);
          e.target.value = '';
        }}
      />
      {children}
    </Wrapper>
  );
};

export default NativeUpload;
