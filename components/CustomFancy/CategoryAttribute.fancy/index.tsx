import type { AffixProps, ButtonProps } from 'antd';
import { Affix, Select, InputNumber, Button, Form, Input, Tag, Tooltip, Tree } from 'antd';
import type { NamePath } from 'antd/es/form/interface';
import type { DataNode, TreeProps } from 'antd/es/tree';
import { filter, isEqual, map, omit, set, size, update } from 'lodash/fp';
import { forwardRef, useCallback, useEffect, useImperativeHandle, useMemo, useRef, useState } from 'react';
import Icon, { CloseCircleFilled, DeleteOutlined, PlusOutlined, StarFilled, SwapOutlined } from '@ant-design/icons';
import { FlexLayout } from '@labelu/components-react';
import { i18n, useTranslation } from '@labelu/i18n';

import type { FancyInputProps } from '../../FancyInput/types';

import { duplicatedValueValidator, listOmitWithId, listWrapWithId, wrapWithId } from '../utils';
import TagSwitcher from './TagSwitcher';

export enum CategoryType {
  Enum = 'enum',
  Array = 'array',
  String = 'string',
}

export enum StringType {
  Text = 'text',
  Number = 'number',
  Order = 'order',
  Regexp = 'regexp',
  English = 'english',
}

export interface CategoryAttributeItem {
  key: string;
  value: string;
  /** enum 为单选；tuple为多选；string为文本描述 */
  type: keyof typeof CategoryType;
  stringType?: keyof typeof StringType;
  /** 以下是属性分类才有的字段 */
  isDefault?: boolean;
  options?: CategoryAttributeOption[];
}

type CategoryAttributeOption = Omit<CategoryAttributeItem, 'options'>;

type CategoryAttributeStateOption = Omit<CategoryAttributeStateItem, 'options'>;

interface CategoryAttributeStateItem extends CategoryAttributeOption {
  id: string;
  options?: CategoryAttributeStateOption[];
}

export interface FancyCategoryAttributeProps extends FancyInputProps {
  value: CategoryAttributeItem[];
  defaultValue?: CategoryAttributeItem[];
  onChange?: (value: CategoryAttributeItem[]) => void;
  className?: string;
  style?: React.CSSProperties;
  affixProps?: AffixProps;
  addTagText?: string;
  addStringText?: string;
  showAddTag?: boolean;
  showAddString?: boolean;
  disabledStringOptions?: string[];
}

export interface FancyCategoryAttributeRef {
  addCategory: (cateType: CategoryType) => () => void;
  removeCategory: (category: CategoryAttributeStateItem) => () => void;
}


// ======================= end =======================

const nestedWithoutId = map((item: CategoryAttributeStateItem) => {
  if (Array.isArray(item.options)) {
    return {
      ...omit(['id'])(item),
      options: listOmitWithId(item.options),
    };
  }

  return omit(['id'])(item);
});

const nestedWithId = map((item: CategoryAttributeItem) => {
  if (Array.isArray(item.options)) {
    return {
      ...wrapWithId(item),
      options: listWrapWithId(item.options),
    };
  }

  return wrapWithId(item);
});

const tagTitleMapping: Record<CategoryType, string> = {
  [CategoryType.Enum]: i18n.t('radio'),
  [CategoryType.Array]: i18n.t('checkbox'),
  [CategoryType.String]: i18n.t('string'),
};

const tooltipTitleMapping: Record<CategoryType, string> = {
  [CategoryType.Enum]: i18n.t('switchToCheckbox'),
  [CategoryType.Array]: i18n.t('switchToRadio'),
  [CategoryType.String]: i18n.t('switchToText'),
};

const stringTypeOptions = [
  { label: i18n.t('anyCharacter'), value: StringType.Text },
  { label: i18n.t('order'), value: StringType.Order },
  { label: i18n.t('numberOnly'), value: StringType.Number },
  { label: i18n.t('englishOnly'), value: StringType.English },
  { label: i18n.t('customFormat'), value: StringType.Regexp },
];

export const FancyCategoryAttribute = forwardRef<FancyCategoryAttributeRef, FancyCategoryAttributeProps>(
  function ForwardRefFancyCategoryAttribute(
    {
      defaultValue = [],
      value,
      fullField,
      onChange,
      className,
      style,
      affixProps,
      addTagText = i18n.t('addCategory'),
      addStringText = i18n.t('addDescription'),
      showAddTag = true,
      showAddString = true,
      disabledStringOptions,
    },
    ref,
  ) {
    const defaultValueWithId = useMemo(() => {
      return nestedWithId(defaultValue);
    }, [defaultValue]);
    const [stateValue, setValue] = useState<CategoryAttributeStateItem[]>(defaultValueWithId);
    const categoryMapping = useRef<Record<string, CategoryAttributeStateItem>>({});
    const optionMapping = useRef<Record<string, CategoryAttributeStateOption>>({});
    const { t } = useTranslation();

    const handleOnChange = useCallback(
      (fieldPath: string) =>
        (
          changedValue: string | number | boolean | React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | null,
        ) => {
          const targetValue = ['string', 'number', 'boolean'].includes(typeof changedValue)
            ? changedValue
            : changedValue === null
            ? ''
            : (changedValue as React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>).target.value;
          const newValue = set(fieldPath)(targetValue)(stateValue);

          setValue(newValue);
        },
      [stateValue],
    );

    const handleAddAttribute = useCallback(
      (cateType: CategoryType) => () => {
        const newAttribute =
          cateType === CategoryType.Enum
            ? wrapWithId({
                key: '',
                value: '',
                type: cateType,
                required: true,
                options: [],
              })
            : wrapWithId({
                key: '',
                value: '',
                type: cateType,
                required: true,
                maxLength: 1000,
                stringType: StringType.Text,
                defaultValue: '',
                regexp: '',
              });
        const newValue = [...stateValue, newAttribute];

        setValue(newValue);
        onChange?.(nestedWithoutId(newValue) as CategoryAttributeItem[]);
      },
      [onChange, stateValue],
    );

    const handleRemoveAttribute = useCallback(
      (category: CategoryAttributeStateItem) => () => {
        const newValue = stateValue.filter((item) => item.id !== category.id);

        setValue(newValue);
        onChange?.(nestedWithoutId(newValue) as CategoryAttributeItem[]);
      },
      [onChange, stateValue],
    );

    const handleAddOption = useCallback(
      (cateIndex: number) => () => {
        const newOption = wrapWithId({
          key: '',
          value: '',
        });
        const newValue = update(`[${cateIndex}]`)((cate) => {
          return {
            ...cate,
            options: [...cate.options, newOption],
          };
        })(stateValue);

        setValue(newValue);
        onChange?.(nestedWithoutId(newValue) as CategoryAttributeItem[]);
      },
      [onChange, stateValue],
    );

    const handleRemoveOption = useCallback(
      (cateIndex: number, option: CategoryAttributeStateItem) => () => {
        const newValue = update(`[${cateIndex}].options`)(
          filter((item: CategoryAttributeStateOption) => item.id !== option.id),
        )(stateValue);

        setValue(newValue);
        onChange?.(nestedWithoutId(newValue) as CategoryAttributeItem[]);
      },
      [onChange, stateValue],
    );

    const handleToggleDefault = useCallback(
      (cateIndex: number, optionIndex: number) => () => {
        const newValue = update(`[${cateIndex}].options[${optionIndex}].isDefault`)((isDefault: boolean) => {
          return !isDefault;
        })(stateValue);

        // isMultiple true，可以有多个默认值
        if ((newValue[cateIndex].type as CategoryType) === CategoryType.Enum) {
          for (let i = 0; i < size(stateValue[cateIndex].options); i++) {
            if (i !== optionIndex) {
              newValue[cateIndex].options[i].isDefault = false;
            }
          }
        }

        setValue(newValue);
        onChange?.(nestedWithoutId(newValue) as CategoryAttributeItem[]);
      },
      [onChange, stateValue],
    );

    const handleToggleMultiple = useCallback(
      (cateIndex: number) => () => {
        let newValue = update(`[${cateIndex}].type`)((itemType: CategoryType) => {
          return itemType === CategoryType.Enum ? CategoryType.Array : CategoryType.Enum;
        })(stateValue) as CategoryAttributeStateItem[];

        // 如果 isMultiple 由 true 变为 false，需要把所有 isDefault 为 true 的选项都变为 false
        if ((newValue[cateIndex].type as CategoryType) === CategoryType.Enum) {
          for (let i = 0; i < size(newValue[cateIndex].options); i++) {
            newValue = set(`[${cateIndex}].options[${i}].isDefault`)(false)(newValue);
          }
        }

        setValue(newValue);
        onChange?.(nestedWithoutId(newValue) as CategoryAttributeItem[]);
      },
      [onChange, stateValue],
    );

    useEffect(() => {
      categoryMapping.current = {};
      optionMapping.current = {};

      for (const item of stateValue) {
        if (item.options) {
          for (const option of item.options) {
            optionMapping.current[`${item.value}-${option.value}`] = option;
          }
        }

        categoryMapping.current[item.value] = item;
      }
    }, [stateValue]);

    // 暴露添加函数
    useImperativeHandle(
      ref,
      () => ({
        addCategory: handleAddAttribute,
        removeCategory: handleRemoveAttribute,
      }),
      [handleAddAttribute, handleRemoveAttribute],
    );

    // 给所有选项加上 id
    useEffect(() => {
      const stateValueWithoutId = nestedWithoutId(stateValue);

      if (!Array.isArray(value) || isEqual(value)(stateValueWithoutId)) {
        return;
      }

      setValue(
        value.map((item) => {
          if (!categoryMapping.current[item.value]) {
            if (!item.options) {
              return wrapWithId(item);
            }

            return {
              ...wrapWithId(item),
              options: map((option: CategoryAttributeOption) => {
                if (!optionMapping.current[`${item.value}-${option.value}`]) {
                  return wrapWithId(option);
                }

                return {
                  ...option,
                  id: optionMapping.current[`${item.value}-${option.value}`].id,
                };
              })(item.options),
            };
          }

          return {
            ...item,
            id: categoryMapping.current[item.value].id,
          };
        }),
      );
    }, [stateValue, value]);

    const finalStringTypeOptions = useMemo(() => {
      if (!disabledStringOptions) {
        return stringTypeOptions;
      }

      return stringTypeOptions.filter((option) => !disabledStringOptions.includes(option.value));
    }, [disabledStringOptions]);

    const makeTreeData = useCallback(
      (input: CategoryAttributeStateItem[], path: NamePath, preIndex?: number): DataNode[] => {
        if (!Array.isArray(input)) {
          // eslint-disable-next-line no-console
          console.warn('makeTreeData: input is not an array');
          return [];
        }

        return input.map((item, index) => {
          const itemType = item.type as CategoryType;
          const otherValueFields: NamePath[] = [];

          input.forEach((_, inputIndex) => {
            if (inputIndex !== index) {
              otherValueFields.push([...path, inputIndex, 'value']);
            }
          });

          if (Array.isArray(item.options) && [CategoryType.Enum, CategoryType.Array].includes(itemType)) {
            return {
              title: (
                <div className="category">
                  <div className="sn">{index + 1}</div>
                  <Form.Item name={[...path, index, 'key']} rules={[{ required: true, message: t('required') }]}>
                    <Input placeholder={t('key')} onChange={handleOnChange(`[${index}].key`)} />
                  </Form.Item>
                  <Form.Item
                    name={[...path, index, 'value']}
                    dependencies={otherValueFields}
                    // @ts-ignore
                    rules={[{ required: true, message: t('required') }, duplicatedValueValidator(path, index)]}
                  >
                    <Input placeholder={t('value')} onChange={handleOnChange(`[${index}].value`)} />
                  </Form.Item>
                  <FlexLayout>
                    <Tooltip title={t('isRequiredOrNot')}>
                      <Form.Item name={[...path, index, 'required']} label="">
                        <TagSwitcher
                          titleMapping={{
                            true: t('isRequired'),
                            false: t('optional'),
                          }}
                          onChange={handleOnChange(`[${index}].required`)}
                        />
                      </Form.Item>
                    </Tooltip>
                  </FlexLayout>
                  <div className="should-align-center">
                    <Tooltip title={tooltipTitleMapping[itemType]}>
                      <Tag className="multiple-switcher" onClick={handleToggleMultiple(index)}>
                        {tagTitleMapping[itemType]} <SwapOutlined />
                      </Tag>
                    </Tooltip>
                    <Tooltip title={t('delete')}>
                      <Button icon={<DeleteOutlined />} onClick={handleRemoveAttribute(item)} />
                    </Tooltip>
                  </div>
                </div>
              ),
              key: item.id,
              children: [
                // @ts-ignore
                ...makeTreeData(item.options, [...path, index, 'options'], index),
                {
                  key: `${item.id}-add`,
                  title: (
                    <Button className="add-option" icon={<PlusOutlined />} type="link" onClick={handleAddOption(index)}>
                      {t('addOption')}
                    </Button>
                  ),
                },
              ],
            };
          } else if (itemType === CategoryType.String) {
            return {
              title: (
                <div className="category">
                  <div className="sn">{index + 1}</div>
                  <Form.Item name={[...path, index, 'key']} rules={[{ required: true, message: t('required') }]}>
                    <Input placeholder={t('key')} onChange={handleOnChange(`[${index}].key`)} />
                  </Form.Item>
                  <Form.Item
                    name={[...path, index, 'value']}
                    dependencies={otherValueFields}
                    // @ts-ignore
                    rules={[{ required: true, message: t('required') }, duplicatedValueValidator(path, index)]}
                  >
                    <Input placeholder={t('value')} onChange={handleOnChange(`[${index}].value`)} />
                  </Form.Item>
                  <FlexLayout>
                    <Tooltip title={t('isRequiredOrNot')}>
                      <Form.Item name={[...path, index, 'required']} label="">
                        <TagSwitcher
                          titleMapping={{
                            true: t('isRequired'),
                            false: t('optional'),
                          }}
                          onChange={handleOnChange(`[${index}].required`)}
                        />
                      </Form.Item>
                    </Tooltip>
                  </FlexLayout>
                  <div className="should-align-center">
                    <Tag>{tagTitleMapping[itemType]}</Tag>
                    <Tooltip title={t('delete')}>
                      <Button icon={<DeleteOutlined />} onClick={handleRemoveAttribute(item)} />
                    </Tooltip>
                  </div>
                </div>
              ),
              key: item.id,
              children: [
                {
                  key: `${item.id}-string`,
                  title: (
                    <div className="text-form-wrapper">
                      {/* @ts-ignore */}
                      <Form.Item name={[...path, index, 'maxLength']} label={t('maxLength')}>
                        <InputNumber
                          style={{ width: '71.5%' }}
                          min={1}
                          onChange={handleOnChange(`[${index}].maxLength`)}
                        />
                      </Form.Item>
                      <Form.Item name={[...path, index, 'stringType']} label={t('stringType')}>
                        <Select
                          style={{ width: '71.5%' }}
                          options={finalStringTypeOptions}
                          onChange={handleOnChange(`[${index}].stringType`)}
                        />
                      </Form.Item>
                      {(item.stringType as StringType) === StringType.Regexp && (
                        <Form.Item name={[...path, index, 'regexp']} label={t('customFormat')}>
                          <Input.TextArea style={{ width: '71.5%' }} onChange={handleOnChange(`[${index}].regexp`)} />
                        </Form.Item>
                      )}
                      <Form.Item name={[...path, index, 'defaultValue']} label={t('defaultValue')}>
                        <Input.TextArea
                          style={{ width: '71.5%' }}
                          onChange={handleOnChange(`[${index}].defaultValue`)}
                        />
                      </Form.Item>
                    </div>
                  ),
                },
              ],
            };
          }

          return {
            title: (
              <div className="option">
                <Form.Item
                  name={[...path, index, 'key']}
                  // @ts-ignore
                  rules={[{ required: true, message: t('required') }]}
                >
                  <Input placeholder={t('key')} onChange={handleOnChange(`[${preIndex}]options[${index}].key`)} />
                </Form.Item>
                <Form.Item
                  name={[...path, index, 'value']}
                  // @ts-ignore
                  rules={[{ required: true, message: t('required') }, duplicatedValueValidator(path, index)]}
                >
                  <Input placeholder={t('value')} onChange={handleOnChange(`[${preIndex}]options[${index}].value`)} />
                </Form.Item>
                <Tooltip title={t('setAsDefault')}>
                  <Button
                    icon={<StarFilled className="star-icon" />}
                    size="small"
                    type="text"
                    onClick={handleToggleDefault(preIndex!, index)}
                  />
                </Tooltip>
                <Tooltip title={t('delete')}>
                  <div className="remove-wrapper">
                    <CloseCircleFilled className="remove" onClick={handleRemoveOption(preIndex!, item)} />
                  </div>
                </Tooltip>
              </div>
            ),
            key: item.id,
          };
        });
      },
      [
        t,
        finalStringTypeOptions,
        handleAddOption,
        handleOnChange,
        handleRemoveAttribute,
        handleRemoveOption,
        handleToggleDefault,
        handleToggleMultiple,
      ],
    );

    const treeData = useMemo(() => makeTreeData(stateValue, fullField), [fullField, makeTreeData, stateValue]);
    const buttons = (
      <FlexLayout gap=".5rem" className="buttons">
        {showAddTag && (
          <Button
            className="add"
            icon={<PlusOutlined />}
            type="primary"
            ghost
            onClick={handleAddAttribute(CategoryType.Enum)}
          >
            {addTagText}
          </Button>
        )}
        {showAddString && (
          <Button
            className="add"
            icon={<PlusOutlined />}
            type="primary"
            ghost
            onClick={handleAddAttribute(CategoryType.String)}
          >
            {addStringText}
          </Button>
        )}
      </FlexLayout>
    );

    return (
      <div className={className} style={style}>
        <Tree
          treeData={treeData}
          selectable={false}
          blockNode
        />
        {affixProps ? <Affix {...affixProps}>{buttons}</Affix> : buttons}
      </div>
    );
  },
);
