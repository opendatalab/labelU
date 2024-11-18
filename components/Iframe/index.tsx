
import React, { useEffect, useRef } from 'react';

export interface DynamicIframeProps {
  src: string;
  offsetTop: number;
}

export default function DynamicIframe ({
  src,
  offsetTop = 0,
}: DynamicIframeProps) {
  const iframeRef = useRef(null);

  useEffect(() => {
    const handleResize = () => {
      if (iframeRef.current) {
        iframeRef.current.style.height = `${window.innerHeight - offsetTop}px`;
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize(); // Set initial height

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <iframe
      ref={iframeRef}
      width="100%"
      src={src}
      style={{ border: 'none' }}
    />
  );
}
