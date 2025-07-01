import { UploadOutlined, SettingOutlined } from '@ant-design/icons';
import { useNavigate, useRouteLoaderData } from 'react-router';
import { Button } from 'antd';
import _ from 'lodash-es';
import styled from 'styled-components';
import { FlexLayout } from '@labelu/components-react';
import { useTranslation } from '@labelu/i18n';

import type { TaskLoaderResult } from '@/loaders/task.loader';
import { MediaType } from '@/api/types';
import useMe from '@/hooks/useMe';

import commonController from '../../../../utils/common';
import ExportPortal from '../../../../components/ExportPortal';
import CollaboratorPortal from '../CollaboratorModal';

const Circle = styled.div<{
  color: string;
}>`
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background-color: ${({ color }) => color};
`;

export interface TaskStatusProps {
  status?: 'done' | 'new' | 'skipped';
  count?: number;
}

export function TaskStatus({ children, status, count }: React.PropsWithChildren<TaskStatusProps>) {
  const { t } = useTranslation();
  const colorMapping = {
    done: 'var(--color-primary)',
    new: 'var(--color-text-tertiary)',
    skipped: 'var(--orange)',
  };

  const textMapping = {
    done: t('annotated'),
    new: t('new'),
    skipped: t('skipped'),
  };

  const color = status ? colorMapping[status] : colorMapping.new;
  const title = status ? textMapping[status] : children;

  return (
    <FlexLayout items="center" gap=".5rem">
      {status && <Circle color={color} />}
      <b>{title}</b>
      {count && <b>{count}</b>}
    </FlexLayout>
  );
}

const Statistical = () => {
  const routerLoaderData = useRouteLoaderData('task') as TaskLoaderResult;
  const taskData = routerLoaderData.task;
  const { stats = {} } = taskData || {};
  const taskId = _.get(taskData, 'id');
  const mediaType = _.get(taskData, 'media_type', MediaType.IMAGE);
  const { t } = useTranslation();
  const me = useMe();
  const isMeTheCreator = taskData?.created_by?.id === me.data?.id;

  const samples = routerLoaderData.samples;

  const navigate = useNavigate();

  const handleGoAnnotation = () => {
    if (!samples || samples.data.length === 0) {
      return;
    }

    navigate(`/tasks/${taskId}/samples/${samples.data[0].id}`);
  };
  const handleGoConfig = () => {
    navigate(`/tasks/${taskId}/edit#config`);
  };
  const handleGoUpload = () => {
    navigate(`/tasks/${taskId}/edit#upload`);
  };

  return (
    <FlexLayout justify="space-between" items="center">
      <FlexLayout items="center" gap="3rem">
        <b>{t('dataOverview')}</b>
        <TaskStatus status="done" count={stats.done} />
        <TaskStatus status="new" count={stats.new} />
        <TaskStatus status="skipped" count={stats.skipped} />
        <TaskStatus count={stats.done! + stats.new! + stats.skipped!}>{t('total')}</TaskStatus>
      </FlexLayout>
      <FlexLayout gap=".5rem">
        {isMeTheCreator && <CollaboratorPortal />}
        {isMeTheCreator && (
          <Button type="text" icon={<SettingOutlined />} onClick={handleGoConfig}>
            {t('taskConfig')}
          </Button>
        )}
        <ExportPortal taskId={+taskId!} mediaType={mediaType} tools={taskData?.config?.tools}>
          <Button type="text" icon={<UploadOutlined />}>
            {t('export')}
          </Button>
        </ExportPortal>
        <Button type="primary" ghost onClick={handleGoUpload}>
          {t('uploadData')}
        </Button>
        <Button type="primary" onClick={commonController.debounce(handleGoAnnotation, 100)}>
          {t('startAnnotate')}
        </Button>
      </FlexLayout>
    </FlexLayout>
  );
};
export default Statistical;
