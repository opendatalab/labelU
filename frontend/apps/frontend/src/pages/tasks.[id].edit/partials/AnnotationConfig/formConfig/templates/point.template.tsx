import { i18n } from '@labelu/i18n';

import type { FancyItemIdentifier } from '@/components/FancyInput/types';

export default [
  {
    field: 'tool',
    key: 'tool',
    type: 'string',
    hidden: true,
    initialValue: 'pointTool',
  },
  {
    key: 'config',
    field: 'config',
    type: 'group',
    children: [
      {
        field: 'attributeConfigurable',
        key: 'attributeConfigurable',
        type: 'boolean',
        hidden: true,
        initialValue: true,
      },
      {
        type: 'number',
        key: 'upperLimit',
        field: 'upperLimit',
        label: i18n.t('maxPointNumber'),
        initialValue: 100,
        rules: [
          {
            required: true,
            message: i18n.t('maxPointNumberRequired'),
          },
        ],
      },
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
