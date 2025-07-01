import React, { useMemo } from 'react';
import { Button, Progress, Tooltip } from 'antd';
import { useNavigate, useRevalidator } from 'react-router';
import Icon from '@ant-design/icons';
import formatter from '@labelu/formatter';
import { EllipsisText, FlexLayout } from '@labelu/components-react';
import { useTranslation } from '@labelu/i18n';

import { modal } from '@/StaticAnt';
import { ReactComponent as DeleteIcon } from '@/assets/svg/delete.svg';
import { ReactComponent as OutputIcon } from '@/assets/svg/outputData.svg';
import { deleteTask } from '@/api/services/task';
import Status from '@/components/Status';
import ExportPortal from '@/components/ExportPortal';
import { MediaTypeText } from '@/constants/mediaType';
import type { MediaType, TaskResponse } from '@/api/types';
import { TaskStatus } from '@/api/types';
import { jsonParse } from '@/utils';
import useMe from '@/hooks/useMe';

import { ActionRow, CardWrapper, MediaBadge, Row, TaskName } from './style';

function MediaTypeTag({ type, status }: React.PropsWithChildren<{ type: MediaType; status: TaskStatus }>) {
  const { t } = useTranslation();
  let children = MediaTypeText[type];
  let color = 'var(--color-primary)';
  let bgColor = 'var(--color-primary-bg)';

  if (status === TaskStatus.DRAFT || status === TaskStatus.IMPORTED) {
    children = t('draft');
    color = 'var(--color-warning-text)';
    bgColor = 'var(--color-warning-bg)';
  } else {
    children = MediaTypeText[type];
  }

  return (
    <MediaBadge color={color} bg={bgColor}>
      {children}
    </MediaBadge>
  );
}

export interface TaskCardProps {
  cardInfo: TaskResponse;
  className?: string;
}

const TaskCard = (props: TaskCardProps) => {
  const { cardInfo, className } = props;
  const revalidator = useRevalidator();
  const { t } = useTranslation();
  const { stats, id, status } = cardInfo;
  const unDoneSample = stats.new ?? 0;
  const doneSample = (stats?.done ?? 0) + (stats?.skipped ?? 0);
  const total = unDoneSample + doneSample;
  const tools = useMemo(() => {
    return jsonParse(cardInfo?.config ?? '{}')?.tools;
  }, [cardInfo]);
  const navigate = useNavigate();
  const me = useMe();
  const isMeTheCreator = cardInfo?.created_by?.id === me?.data?.id;
  const turnToAnnotation = (e: any) => {
    if (!e.currentTarget.contains(e.target)) {
      return;
    }

    e.stopPropagation();
    e.stopPropagation();
    e.nativeEvent.stopImmediatePropagation();

    navigate('/tasks/' + id);
  };

  const handleDeleteTask = (e: React.MouseEvent) => {
    e.stopPropagation();

    modal.confirm({
      title: t('deleteTask'),
      content: t('confirmDeleteTask'),
      okText: t('ok'),
      cancelText: t('cancel'),
      onOk: async () => {
        await deleteTask(id!);
        revalidator.revalidate();
      },
    });
  };

  return (
    <CardWrapper className={className} onClick={turnToAnnotation} gap=".5rem">
      <Row justify="space-between">
        <FlexLayout items="center" gap=".5rem">
          <EllipsisText maxWidth={120} title={cardInfo.name}>
            <TaskName>{cardInfo.name}</TaskName>
          </EllipsisText>
          <MediaTypeTag type={cardInfo.media_type as MediaType} status={cardInfo.status!} />
        </FlexLayout>
        <ActionRow justify="flex-end" items="center">
          {cardInfo.config && (
            <ExportPortal taskId={cardInfo.id!} mediaType={cardInfo.media_type} tools={tools}>
              <Tooltip placement={'top'} title={t('export')}>
                <Button size="small" type="text" icon={<Icon component={OutputIcon} />} />
              </Tooltip>
            </ExportPortal>
          )}

          {isMeTheCreator && (
            <Tooltip title={t('deleteTask')} placement={'top'}>
              <Button onClick={handleDeleteTask} size="small" type="text" icon={<Icon component={DeleteIcon} />} />
            </Tooltip>
          )}
        </ActionRow>
      </Row>

      <Row>{cardInfo.created_by?.username}</Row>
      <Row>{formatter.format('dateTime', cardInfo.created_at, { style: 'YYYY-MM-DD HH:mm' })}</Row>

      {doneSample === total && status !== 'DRAFT' && status !== 'IMPORTED' && (
        <FlexLayout gap=".5rem">
          <FlexLayout.Header>
            {total}/{total}
          </FlexLayout.Header>
          <FlexLayout.Footer>
            <Status type="success">{t('done')}</Status>
          </FlexLayout.Footer>
        </FlexLayout>
      )}
      {doneSample !== total && status !== 'DRAFT' && status !== 'IMPORTED' && (
        <FlexLayout gap=".5rem">
          <FlexLayout.Content>
            <Progress percent={Math.trunc((doneSample * 100) / total)} showInfo={false} />
          </FlexLayout.Content>
          <FlexLayout.Footer>
            {doneSample}/{total}
          </FlexLayout.Footer>
        </FlexLayout>
      )}
    </CardWrapper>
  );
};
export default TaskCard;
