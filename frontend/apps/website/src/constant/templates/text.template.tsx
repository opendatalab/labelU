import { i18n } from '@labelu/i18n';

import type { FancyItemIdentifier } from '@/components/FancyInput/types';

export default [
  {
    field: 'tool',
    key: 'tool',
    type: 'string',
    hidden: true,
    initialValue: 'textTool',
  },
  {
    key: 'config',
    field: 'config',
    type: 'group',
    children: [
      {
        field: 'textConfigurable',
        key: 'textConfigurable',
        type: 'boolean',
        hidden: true,
        initialValue: false,
      },
      {
        type: 'category-attribute',
        key: 'field',
        field: 'attributes',
        label: '',
        addStringText: i18n.t('add'),
        disabledStringOptions: ['order'],
        showAddTag: false,
        initialValue: [
          {
            key: i18n.t('label1'),
            value: 'text-label-1',
            required: true,
            type: 'string',
            maxLength: 1000,
            stringType: 'text',
            defaultValue: '',
          },
        ],
      },
    ],
  },
] as FancyItemIdentifier[];
