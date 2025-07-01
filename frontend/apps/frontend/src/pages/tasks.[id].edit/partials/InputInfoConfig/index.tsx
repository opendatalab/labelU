import React, { memo, useContext } from 'react';
import { Form, Input, Select } from 'antd';
import styled from 'styled-components';
import { FlexLayout } from '@labelu/components-react';
import { useTranslation } from '@labelu/i18n';

import { MediaType } from '@/api/types';

import { TaskCreationContext } from '../../taskCreation.context';

const Inner = styled(FlexLayout)`
  width: 740px;
  margin: auto;
`;

const InputInfoConfig = () => {
  const { basicFormInstance } = useContext(TaskCreationContext);
  const { t } = useTranslation();

  return (
    <FlexLayout padding="1rem" flex="column">
      <Inner flex="column">
        <h2>{t('basicConfig')}</h2>
        <FlexLayout.Content>
          <Form form={basicFormInstance} labelCol={{ span: 3 }} wrapperCol={{ span: 21 }}>
            <Form.Item
              label={t('taskName')}
              name="name"
              required
              rules={[{ required: true, message: t('taskNameRequired') }]}
            >
              <Input placeholder={t('taskName50CharactersPlease')} maxLength={50} />
            </Form.Item>
            <Form.Item
              label={t('mediaType')}
              name="media_type"
              rules={[{ required: true, message: t('mediaTypeRequired') }]}
            >
              <Select
                placeholder={t('selectMediaTypePlease')}
                options={[
                  {
                    label: t('image'),
                    value: MediaType.IMAGE,
                  },
                  {
                    label: t('video'),
                    value: MediaType.VIDEO,
                  },
                  {
                    label: t('audio'),
                    value: MediaType.AUDIO,
                  },
                ]}
              />
            </Form.Item>
            <Form.Item label={t('taskDescription')} name="description">
              <Input.TextArea placeholder={t('taskDescription500CharactersPlease')} maxLength={500} rows={6} />
            </Form.Item>
            <Form.Item label={t('taskTip')} name="tips">
              <Input.TextArea placeholder={t('taskTipPlaceholder')} maxLength={1000} rows={6} />
            </Form.Item>
          </Form>
        </FlexLayout.Content>
      </Inner>
    </FlexLayout>
  );
};
export default memo(InputInfoConfig);
