import type { DrawerProps } from 'antd';
import { Form, Button, Drawer } from 'antd';
import { compose, get, isEqual, size } from 'lodash/fp';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import styled from 'styled-components';
import Icon, { ExclamationCircleFilled } from '@ant-design/icons';
import { FlexLayout } from '@labelu/components-react';
import { useTranslation } from '@labelu/i18n';

import { ReactComponent as AddCategoryIcon } from '@/assets/add-category.svg';
import { ReactComponent as AddTextIcon } from '@/assets/add-text.svg';
import { modal } from '@/components/StaticAnt';

import type { CategoryAttributeItem, FancyCategoryAttributeRef } from '../CategoryAttribute.fancy';
import { CategoryType, FancyCategoryAttribute, StyledFancyAttributeWrapper } from '../CategoryAttribute.fancy';

export interface AttributeConfigurationProps {
  visible: boolean;
  onClose: () => void;
  value?: CategoryAttributeItem[];
  defaultValue?: CategoryAttributeItem[];
  onChange?: (value: CategoryAttributeItem[]) => void;
}

const StyledDrawer = styled<React.FC<DrawerProps>>(Drawer)`
  .addition {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .addition-button {
    display: flex;
    padding: 1.5rem 3rem;
    align-items: center;
    justify-content: center;
    border-radius: var(--border-radius);
    cursor: pointer;
    background-color: #fff;
    flex-direction: column;
    border-style: dashed;
    border-width: 1px;
    background-color: #fafcff;
    border-color: #d0dfff;
    transition: all var(--motion-duration-fast);

    &:hover {
      border-color: var(--color-primary-border-hover);
    }

    &:active {
      border-color: var(--color-primary-active);
    }
  }

  .new-category-attr {
    margin-right: 1.5rem;
  }

  .icon {
    font-size: 3rem;
  }

  .title {
    margin: 1rem 0 0.5rem;
  }

  sub {
    color: var(--color-text-secondary);
  }

  .footer {
    padding: 0.375rem;
  }

  ${StyledFancyAttributeWrapper} {
    margin-bottom: 1rem;
    .buttons {
      padding: 1rem 0 1rem;
    }
  }
`;

interface AttributeConfigurationState {
  list: CategoryAttributeItem[];
}

export default function AttributeConfiguration({ onClose, visible, value, onChange }: AttributeConfigurationProps) {
  const [stateValue, setStateValue] = useState<AttributeConfigurationState>({ list: value || [] });
  const ref = useRef<FancyCategoryAttributeRef>(null);
  const [form] = Form.useForm();
  const { t } = useTranslation();

  useEffect(() => {
    if (!visible) {
      return;
    }

    setStateValue({ list: value || [] });
    form.setFieldsValue({ list: value || [] });
  }, [form, value, visible]);

  const handleAddCategoryAttribute = useCallback(
    (type: CategoryType) => () => {
      if (!ref.current) {
        return;
      }

      ref.current?.addCategory(type)();
    },
    [],
  );

  const reset = useCallback(() => {
    form.resetFields();
    setStateValue({ list: [] });
  }, [form]);

  const handleSave = useCallback(() => {
    form
      .validateFields()
      .then((values) => {
        onChange?.(values.list);
        onClose();
        reset();
      })
      .catch((error) => {
        modal.info({
          title: t('pleaseCompleteTheAttribute'),
          okText: t('iKnown'),
          content: t('completeAndSave'),
          icon: <ExclamationCircleFilled style={{ color: 'var(--color-warning)' }} />,
          onOk: () => {
            form.scrollToField(error.errorFields[0].name);
          },
        });
      });
  }, [t, form, onChange, onClose, reset]);

  const handleCancel = useCallback(() => {
    reset();
    onClose();
  }, [onClose, reset]);

  const handleClose = useCallback(() => {
    if (!isEqual(value)(form.getFieldsValue().list)) {
      modal.confirm({
        title: t('categoryExitConfirm'),
        onOk: handleCancel,
        okText: t('exit'),
        cancelText: t('continueEdit'),
      });

      return;
    }

    onClose();
  }, [t, form, handleCancel, onClose, value]);

  const emptyPlaceholder = useMemo(
    () => (
      <div className="addition">
        <button className="addition-button new-category-attr" onClick={handleAddCategoryAttribute(CategoryType.Enum)}>
          <Icon className="icon" component={AddCategoryIcon} />
          <span className="title">{t('addCategory')}</span>
          <sub>{t('selectType')}</sub>
        </button>

        <button className="addition-button new-text-attr" onClick={handleAddCategoryAttribute(CategoryType.String)}>
          <Icon className="icon" component={AddTextIcon} />
          <span className="title">{t('addDescription')}</span>
          <sub>{t('textarea')}</sub>
        </button>
      </div>
    ),
    [t, handleAddCategoryAttribute],
  );
  const footer = useMemo(
    () => (
      <FlexLayout gap=".5rem" className="footer">
        <Button type="primary" onClick={handleSave}>
          {t('save')}
        </Button>
        <Button onClick={handleClose}>{t('cancel')}</Button>
      </FlexLayout>
    ),
    [t, handleSave, handleClose],
  );

  const isValueEmpty = useMemo(() => {
    return compose(size, get('list'))(form.getFieldsValue()) === 0;
    // stateValue 只用于判断是否为空
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form, stateValue]);

  const content = useMemo(
    () => (
      <Form
        form={form}
        labelCol={{ span: 0 }}
        wrapperCol={{ span: 24 }}
        colon={false}
        onValuesChange={(_, allValues) => {
          setStateValue(allValues);
        }}
        style={{ display: isValueEmpty ? 'none' : 'block', width: '100%' }}
        validateTrigger="onBlur"
      >
        <Form.Item name="list" label="">
          <FancyCategoryAttribute
            className="category-content"
            ref={ref}
            fullField={['list']}
            affixProps={{
              offsetBottom: 61,
            }}
          />
        </Form.Item>
      </Form>
    ),
    [form, isValueEmpty],
  );

  return (
    <StyledDrawer
      open={visible}
      title={t('attributesConfig')}
      width={600}
      onClose={handleClose}
      footer={isValueEmpty ? null : footer}
      bodyStyle={{ display: 'flex', justifyContent: 'center' }}
    >
      {isValueEmpty && emptyPlaceholder}
      {content}
    </StyledDrawer>
  );
}
