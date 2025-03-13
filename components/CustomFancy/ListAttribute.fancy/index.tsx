import { CloseCircleFilled, PlusOutlined } from '@ant-design/icons';
import { Button, Form, Input, Tooltip, Badge } from 'antd';
import { set, isEqual, size } from 'lodash/fp';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { NamePath } from 'antd/es/form/interface';
import { useTranslation } from '@labelu/i18n';

import ColorPalette from '../ColorPalette';
import type { FancyInputProps } from '../../FancyInput/types';

import type { CategoryAttributeItem } from '../CategoryAttribute.fancy';
import AttributeConfiguration from './AttributeConfiguration';
import { duplicatedValueValidator, listOmitWithId, listWrapWithId, wrapWithId } from '../utils';
import { FlexLayout } from '@labelu/components-react';

const colorPalette = new ColorPalette();

export interface AttributeItem {
  color: string;
  key: string;
  value: string;
  attributes?: CategoryAttributeItem[];
}

interface AttributeItemInState extends AttributeItem {
  id: string;
}

export interface FancyAttributeListProps extends FancyInputProps {
  value: AttributeItem[];
  defaultValue: AttributeItem[];
  deletable?: boolean;
  onChange: (value: AttributeItem[]) => void;
}

// ====================== style ======================



// ======================= end =======================

export function FancyAttributeList({
  value,
  onChange,
  defaultValue = [],
  deletable = true,
  fullField,
}: FancyAttributeListProps) {
  const defaultValueWithId = useMemo(() => {
    return listWrapWithId(defaultValue);
  }, [defaultValue]);
  const [stateValue, setValue] = useState<AttributeItemInState[]>(defaultValueWithId);
  const attributeMapping = useRef<Record<string, AttributeItemInState>>({});
  const { t } = useTranslation();

  const handleOnChange = useCallback(
    (fieldPath: string) => (changedValue: string | React.ChangeEvent<HTMLInputElement>) => {
      const targetValue = typeof changedValue === 'string' ? changedValue : changedValue.target.value;
      const newValue = set(fieldPath)(targetValue)(stateValue);

      setValue(newValue);
    },
    [stateValue],
  );

  const handleAddAttribute = useCallback(() => {
    const newAttribute = wrapWithId({
      color: colorPalette.pick(),
      key: '',
      value: '',
    });
    const newValue = [...stateValue, newAttribute];

    setValue(newValue);
    onChange?.(listOmitWithId(newValue) as AttributeItem[]);
  }, [onChange, stateValue]);

  const handleRemoveAttribute = useCallback(
    (attribute: AttributeItemInState) => () => {
      const newValue = stateValue.filter((item) => item.id !== attribute.id);

      setValue(newValue);
      onChange?.(listOmitWithId(newValue) as AttributeItem[]);
    },
    [onChange, stateValue],
  );

  const [isAttributeConfigurationOpen, setAttributeConfigurationOpen] = useState(false);
  const [activeAttributeIndex, setActiveAttributeIndex] = useState<number>(0);
  const handleOpenAttributeConfiguration = useCallback((index: number) => {
    setAttributeConfigurationOpen(true);
    setActiveAttributeIndex(index);
  }, []);

  const handleChangeAttributes = useCallback(
    (values: CategoryAttributeItem[]) => {
      const newValue = set(`[${activeAttributeIndex}].attributes`)(values)(stateValue);
      setValue(newValue);
      onChange?.(listOmitWithId(newValue) as AttributeItem[]);
    },
    [activeAttributeIndex, onChange, stateValue],
  );

  const handleCloseAttributeConfiguration = useCallback(() => {
    setAttributeConfigurationOpen(false);
  }, []);

  useEffect(() => {
    if (!Array.isArray(value) || isEqual(value)(listOmitWithId(stateValue))) {
      return;
    }

    setValue(
      value.map((item) => {
        if (!attributeMapping.current[item.value]) {
          return wrapWithId(item);
        }

        return {
          ...item,
          id: attributeMapping.current[item.value].id,
        };
      }),
    );
  }, [stateValue, value]);

  useEffect(() => {
    const newMapping = stateValue.reduce((acc, item) => {
      acc[item.value] = item;
      return acc;
    }, {} as Record<string, AttributeItemInState>);

    attributeMapping.current = newMapping;
  }, [stateValue]);

  const preFields = useMemo(() => {
    if (Array.isArray(fullField)) {
      return fullField;
    }

    return [fullField];
  }, [fullField]);

  const attributes = useMemo(
    () =>
      stateValue.map((item, index) => {
        const otherValueFields: NamePath[] = [];

        stateValue.forEach((_, inputIndex) => {
          if (inputIndex !== index) {
            otherValueFields.push([...preFields, inputIndex, 'value']);
          }
        });

        return (
          <FlexLayout flex="row" key={item.id}>
            <div className="sn">{index + 1}</div>
            <Form.Item name={[...preFields, index, 'color']} rules={[{ required: true }]}>
              <input type="color" className="color" value={item.color} onChange={handleOnChange(`[${index}].color`)} />
            </Form.Item>
            <Form.Item
              name={[...preFields, index, 'key']}
              className="input"
              rules={[{ required: true, message: t('required') }]}
            >
              <Input placeholder={t('key')} value={item.key} onChange={handleOnChange(`[${index}].key`)} />
            </Form.Item>
            <Form.Item
              name={[...preFields, index, 'value']}
              className="input"
              dependencies={otherValueFields}
              // @ts-ignore
              rules={[{ required: true, message: t('required') }, duplicatedValueValidator(preFields, index)]}
            >
              <Input placeholder={t('value')} value={item.value} onChange={handleOnChange(`[${index}].value`)} />
            </Form.Item>
            <div className="add-wrapper">
              <Button type="link" onClick={() => handleOpenAttributeConfiguration(index)}>
                {t('addAttribute')}
              </Button>
              <Badge count={size(item.attributes)} showZero color="var(--color-fill-secondary)" />
            </div>
            {deletable && (
              <Tooltip title={t('delete')}>
                <div className="remove-wrapper">
                  <CloseCircleFilled className="remove" onClick={handleRemoveAttribute(item)} />
                </div>
              </Tooltip>
            )}
          </FlexLayout>
        );
      }),
    [t, deletable, handleOnChange, handleOpenAttributeConfiguration, handleRemoveAttribute, preFields, stateValue],
  );

  return (
    <div className="attribute-wrapper">
      {attributes}
      <Button className="add" icon={<PlusOutlined />} type="link" onClick={handleAddAttribute}>
        {t('add')}
      </Button>
      <AttributeConfiguration
        visible={isAttributeConfigurationOpen}
        value={stateValue[activeAttributeIndex]?.attributes || []}
        onClose={handleCloseAttributeConfiguration}
        onChange={handleChangeAttributes}
      />
    </div>
  );
}
