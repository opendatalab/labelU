import { i18n } from '@labelu/i18n';

import type { FancyItemIdentifier } from '@/components/FancyInput/types';

export default [
  {
    field: 'tool',
    key: 'tool',
    type: 'string',
    hidden: true,
    initialValue: 'rectTool',
  },
  {
    key: 'config',
    field: 'config',
    type: 'group',
    children: [
      {
        type: 'group',
        key: 'minSize',
        layout: 'horizontal',
        label: i18n.t('minSize'),
        children: [
          {
            field: 'attributeConfigurable',
            key: 'attributeConfigurable',
            type: 'boolean',
            hidden: true,
            initialValue: true,
          },
          {
            field: 'minWidth',
            key: 'minWidth',
            type: 'number',
            label: undefined,
            initialValue: 1,
            antProps: {
              addonAfter: 'W',
              min: 0,
              placeholder: i18n.t('minWidth'),
            },
            rules: [
              {
                required: true,
                message: i18n.t('minWidthRequired'),
              },
            ],
          },
          {
            field: 'minHeight',
            key: 'minHeight',
            type: 'number',
            label: undefined,
            antProps: {
              addonAfter: 'H',
              min: 0,
              placeholder: i18n.t('minHeight'),
            },
            initialValue: 1,
            rules: [
              {
                required: true,
                message: i18n.t('minHeightRequired'),
              },
            ],
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
