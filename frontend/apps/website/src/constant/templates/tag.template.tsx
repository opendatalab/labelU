import { i18n } from '@labelu/i18n';

import type { FancyItemIdentifier } from '@/components/FancyInput/types';

export default [
  {
    field: 'tool',
    key: 'tool',
    type: 'string',
    hidden: true,
    initialValue: 'tagTool',
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
        addTagText: i18n.t('add'),
        showAddString: false,
        initialValue: [
          {
            key: i18n.t('label1'),
            value: 'tag-label-1',
            required: true,
            type: 'enum',
            options: [
              {
                key: i18n.t('label1-1'),
                value: 'tag-label-1-1',
              },
            ],
          },
        ],
      },
    ],
  },
] as FancyItemIdentifier[];
