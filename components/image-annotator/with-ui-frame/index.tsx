import React, { useMemo } from 'react';
import { Annotator } from '@labelu/image-annotator-react';
import './index.css';

export default function Basic() {
  const editingSample = useMemo(() => ({
    id: '1',
    name: 'rect',
    url: '/assets/rect.jpg',
    data: {
      line: [],
      point: [],
      rect: []
    }
  }))

  const config = useMemo(() => ({
    line: {
      labels: [{
        id: '1',
        key: 'Lane',
        value: 'lane',
        color: '#ff0000'
      }]
    },
    point: {
      labels: [
        {
          id: '3',
          key: 'Eye',
          value: 'eye',
          color: '#00a2ff'
        },
      ]
    },
    rect: {
      labels: [{
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
      }]
    },
  }), []);

  return (
      <Annotator
        offsetTop={320}
        config={config}
        editingSample={editingSample}
        renderSidebar={null}
      />
  );
}
