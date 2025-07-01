import { ArrowDownOutlined, ArrowUpOutlined } from '@ant-design/icons';
import type { RuleRender } from 'antd/es/form';
import { i18n } from '@labelu/i18n';

import type { FancyItemIdentifier } from '@/components/FancyInput/types';
import FancyInput from '@/components/FancyInput';

export default [
  {
    field: 'tool',
    key: 'tool',
    type: 'string',
    hidden: true,
    initialValue: 'polygonTool',
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
        field: 'lineType',
        key: 'lineType',
        type: 'enum',
        label: i18n.t('lineType'),
        initialValue: 0,
        antProps: {
          options: [
            { label: i18n.t('straightLine'), value: 0 },
            { label: i18n.t('spline'), value: 1 },
          ],
        },
      },
      {
        type: 'group',
        key: 'pointNum',
        layout: 'horizontal',
        label: i18n.t('closedPointNumber'),
        children: [
          {
            field: 'lowerLimitPointNum',
            key: 'lowerLimitPointNum',
            type: 'number',
            label: undefined,
            initialValue: 2,
            antProps: {
              addonAfter: <ArrowDownOutlined />,
              min: 0,
              placeholder: i18n.t('minimumClosedPointNumber'),
            },
            rules: [
              {
                required: true,
                message: i18n.t('minimumClosedPointNumberRequired'),
              },
              (({ getFieldValue }) => ({
                // @ts-ignore
                validator({ fullField }, value: number) {
                  const maxNum = getFieldValue(
                    fullField.replace('lowerLimitPointNum', 'upperLimitPointNum').split('.'),
                  );
                  if (value > maxNum) {
                    return Promise.reject(new Error(i18n.t('minimumClosedPointCannotExceedMaximum')));
                  }

                  return Promise.resolve();
                },
              })) as RuleRender,
            ],
          },
          {
            field: 'upperLimitPointNum',
            key: 'upperLimitPointNum',
            type: 'number',
            label: undefined,
            antProps: {
              addonAfter: <ArrowUpOutlined />,
              min: 0,
              placeholder: i18n.t('maximumClosedPointNumber'),
            },
            initialValue: 100,
            rules: [
              {
                required: true,
                message: i18n.t('maximumClosedPointNumberRequired'),
              },
              ({ getFieldValue }) => ({
                // @ts-ignore
                validator({ fullField }, value: number) {
                  const minNum = getFieldValue(
                    fullField.replace('upperLimitPointNum', 'lowerLimitPointNum').split('.'),
                  );
                  if (value < minNum) {
                    return Promise.reject(new Error(i18n.t('maximumClosedPointCannotSmallThanMinimumClosedPoint')));
                  }

                  return Promise.resolve();
                },
              }),
            ],
          },
        ],
      },
      {
        field: 'edgeAdsorption',
        key: 'edgeAdsorption',
        type: 'boolean',
        label: i18n.t('edgeAdsorption'),
        initialValue: false,
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
