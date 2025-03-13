import { Form, Button, Modal, Drawer } from 'antd';
import { compose, get, isEqual, size } from 'lodash/fp';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ExclamationCircleFilled, PlusOutlined } from '@ant-design/icons';
import { FlexLayout } from '@labelu/components-react';
import { useTranslation } from '@labelu/i18n';
import type { CategoryAttributeItem, FancyCategoryAttributeRef } from '../CategoryAttribute.fancy';
import { CategoryType, FancyCategoryAttribute } from '../CategoryAttribute.fancy';

export interface AttributeConfigurationProps {
  visible: boolean;
  onClose: () => void;
  value?: CategoryAttributeItem[];
  defaultValue?: CategoryAttributeItem[];
  onChange?: (value: CategoryAttributeItem[]) => void;
}

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
        Modal.info({
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
      Modal.confirm({
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
      <div className="addition flex flex-col items-start gap-2">
        <button className="flex gap-1 items-center addition-button new-category-attr" onClick={handleAddCategoryAttribute(CategoryType.Enum)}>
          <Button icon={<PlusOutlined />} />
          <span className="title">{t('addCategory')}</span>
          <sub className="text-slate-500">{t('selectType')}</sub>
        </button>

        <button className="flex gap-1 items-center addition-button new-text-attr" onClick={handleAddCategoryAttribute(CategoryType.String)}>
          <Button icon={<PlusOutlined />} />
          <span className="title">{t('addDescription')}</span>
          <sub className="text-slate-500">{t('textarea')}</sub>
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
    <Drawer
      open={visible}
      title={t('attributesConfig')}
      width={600}
      onClose={handleClose}
      footer={isValueEmpty ? null : footer}
      bodyStyle={{ display: 'flex', justifyContent: 'center' }}
    >
      {isValueEmpty && emptyPlaceholder}
      {content}
    </Drawer>
  );
}
