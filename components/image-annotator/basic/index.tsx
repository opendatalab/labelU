import React, { useEffect, useLayoutEffect, useMemo, useRef } from 'react';
import { useState } from 'react';
import { Annotator } from '@labelu/image';
import './index.css'

export const useEngine = (containerRef: React.RefObject<HTMLDivElement>, options?: any) => {
  const [engine, setAnnotationEngine] = useState<any | null>(null);
  const [optionsState, setOptionsState] = useState<any | null>(options);

  useEffect(() => {
    setOptionsState(options);
  }, [options]);

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }

    const ae = new Annotator({
      container: containerRef.current,
      ...(options || {}),
    });

    setAnnotationEngine(ae);

    return () => {
      setAnnotationEngine(null);
      ae.destroy();
    };
  }, [optionsState, containerRef]);

  return engine;
};

export default function Basic() {
  const ref = useRef<HTMLDivElement>(null);
  const options = useMemo(() => {
    return {
      width: 500,
      height: 400,
      showOrder: true,
      rect: {
        outOfImage: false,
        minWidth: 10,
        minHeight: 10,
        labels: [
          {
            id: '4',
            key: 'Nose',
            value: 'nose',
            color: '#ff00d9'
          },
          {
            id: '5',
            key: 'Mouth',
            value: 'mouth',
            color: '#ff7700'
          }, {
            id: '2',
            key: 'Helmet',
            value: 'helmet',
            color: '#05d77c'
          },
        ],
      },
    }
  }, [])
  const engine = useEngine(ref, options);

  useLayoutEffect(() => {
    if (!engine) {
      return;
    }

    engine.loadImage('/assets/rect.jpg').then(() => {
      engine.loadData('rect', [
        {
          x: 925,
          y: 233,
          width: 100,
          height: 80,
          valid: true,
          id: 'AcO6GXyc',
          order: 1,
          label: 'helmet',
        },
      ]);
      engine.switch('rect', 'helmet');
      engine.backgroundRenderer.backgroundColor = 'rgba(0, 0, 0, 0.1)';
    });
  }, [engine]);

  return (
    <div style={{ border: '1px solid rgb(0 0 0 / 15%)', borderRadius: 6 }} ref={ref} />
  );
}
