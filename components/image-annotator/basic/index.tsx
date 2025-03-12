import React, { useEffect, useLayoutEffect, useRef } from 'react';
import { useState } from 'react';
import { Annotator } from '@labelu/image';
import './index.css'

export const useEngine = (containerRef: React.RefObject<HTMLDivElement>, options?: any) => {
  const [engine, setAnnotationEngine] = useState<any | null>(null);
  const [optionsState, setOptionsState] = useState<any | null>(options);

  useEffect(() => {
    if (JSON.stringify(options) === JSON.stringify(optionsState)) {
      return;
    }

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
  const engine = useEngine(ref, {
    width: 600,
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
  });

  const [tool, setTool] = useState('point');
  const [label, setLabel] = useState('car');

  useLayoutEffect(() => {
    if (!engine) {
      return;
    }

    engine.loadImage('/assets/rect.jpg').then(() => {
      engine.switch('rect', 'helmet');
      engine.loadData('rect', [
        {
          x: 148.66463414634154,
          y: 294.4123475609755,
          width: 168.1326219512195,
          height: 134.5060975609756,
          valid: true,
          id: '0kjFS5rI',
          order: 6,
          label: 'helmet',
        },
        {
          x: 515.016768292683,
          y: 103.2614329268292,
          width: 194.67987804878047,
          height: 69.02286585365853,
          valid: true,
          id: 'AcO6GXyc',
          order: 7,
          label: 'helmet',
        },
      ]);

      engine.switch('point', 'car');
    });

    engine.on('hover', (data) => {
      console.log('hover', data);
    });

    engine.on('add', (...args) => {
      console.info('add', ...args);
    });

    engine.on('select', (...args) => {
      console.info('select', ...args);
    });

    engine.on('unselect', (...args) => {
      console.info('unselect', ...args);
    });

    engine.on('complete', () => {
      console.log("Engine's ready");
    });
    engine.on('error', (error) => {
      console.error('Error', error);
    });
    engine.on('delete', (...args) => {
      console.info('Delete', ...args);
    });
    engine.on('render', () => {
      console.log('Render');
    });
    engine.on('toolChange', (toolName: string, label: string) => {
      setTool(toolName);
      setLabel(label);
    });
  }, [engine]);

  return (
    <div style={{ border: '1px solid #e2e2e2', borderRadius: 6 }} ref={ref} />
  );
}
