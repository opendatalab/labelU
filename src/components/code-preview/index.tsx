import CodeMirror from '@uiw/react-codemirror';
import { json } from '@codemirror/lang-json';
import { useMemo } from 'react';

export interface CodePreviewProps {
  value: string;
}

export default function CodePreview({ value }: CodePreviewProps) {
  const code = useMemo(() => {
    try {
      if (typeof value !== 'string') {
        return JSON.stringify(value, null, 2);
      }

      return value;
    } catch (error) {
      return value;
    }
  }, []);


  return <CodeMirror className='border' value={code} height="auto" extensions={[json()]} />;
}
