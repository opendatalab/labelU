import { i18n } from '@labelu/i18n';

import type { FancyItemIdentifier } from '../../FancyInput/types';
import FancyInput from '../../FancyInput';

export default [
  {
    field: 'tool',
    key: 'tool',
    type: 'string',
    hidden: true,
    initialValue: 'relationTool',
  },
  {
    key: 'config',
    field: 'config',
    type: 'group',
    children: [
      {
        field: 'lineStyle',
        key: 'lineStyle',
        type: 'enum',
        label: i18n.t('lineStyle'),
        initialValue: 'dashed',
        antProps: {
          options: [
            { label: i18n.t('solid'), value: 'solid' },
            { label: i18n.t('dashed'), value: 'dashed' },
            { label: i18n.t('dotted'), value: 'dotted' },
          ],
        },
        renderFormItem({ antProps, ...props }, form, fullField) {
          const lineType = form.getFieldValue([...(fullField as any[]).slice(0, -1), 'lineType']);

          if (lineType === 1) {
            return null;
          }

          return <FancyInput {...props} {...antProps} />;
        },
      },

      {
        field: 'arrowType',
        key: 'arrowType',
        type: 'enum',
        label: i18n.t('arrowType'),
        initialValue: 'single',
        antProps: {
          options: [
            { label: i18n.t('single'), value: 'single' },
            { label: i18n.t('double'), value: 'double' },
            { label: i18n.t('none'), value: 'none' },
          ],
        },
        renderFormItem({ antProps, ...props }, form, fullField) {
          const lineType = form.getFieldValue([...(fullField as any[]).slice(0, -1), 'lineType']);

          if (lineType === 1) {
            return null;
          }

          return <FancyInput {...props} {...antProps} />;
        },
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
