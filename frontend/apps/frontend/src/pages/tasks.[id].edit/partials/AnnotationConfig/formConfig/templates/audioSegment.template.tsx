import { i18n } from '@labelu/i18n';

import type { FancyItemIdentifier } from '@/components/FancyInput/types';

export default [
  {
    field: 'tool',
    key: 'tool',
    type: 'string',
    hidden: true,
    initialValue: 'audioSegmentTool',
  },
  {
    key: 'config',
    field: 'config',
    type: 'group',
    children: [
      {
        field: 'attributes',
        key: 'attributes',
        type: 'list-attribute',
        label: i18n.t('labelConfig'),
        initialValue: [
          {
            color: '#ff6600',
            key: i18n.t('label1'),
            value: 'label-1',
          },
        ],
      },
    ],
  },
] as FancyItemIdentifier[];
