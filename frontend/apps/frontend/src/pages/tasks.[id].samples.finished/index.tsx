import { CheckOutlined } from '@ant-design/icons';
import { useNavigate, useParams, useRevalidator, useRouteLoaderData } from 'react-router';
import { Button } from 'antd';
import styled from 'styled-components';
import { useTranslation } from '@labelu/i18n';
import { FlexLayout } from '@labelu/components-react';

import ExportPortal from '@/components/ExportPortal';
import type { TaskLoaderResult } from '@/loaders/task.loader';

const Wrapper = styled(FlexLayout)`
  background: #fff;
  height: calc(100vh - var(--header-height));
`;

const Inner = styled(FlexLayout.Item)`
  width: 312px;
  height: 290px;
`;

const CircleCheck = styled(FlexLayout.Item)`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: var(--color-success-bg);
`;

const Statistic = styled(FlexLayout)`
  font-size: 1rem;
`;

const ButtonWrapper = styled(FlexLayout)`
  button {
    padding: 0.375rem 2.5rem !important;
    height: 3rem !important;
  }
`;

const SamplesFinished = () => {
  const { task: taskData } = useRouteLoaderData('task') as TaskLoaderResult;
  const routeParams = useParams();
  const taskId = +routeParams.taskId!;
  const navigate = useNavigate();
  const revalidator = useRevalidator();
  const handleGoHome = () => {
    navigate(`/tasks/${taskId}?t=${Date.now()}`);
    setTimeout(revalidator.revalidate);
  };
  const { t } = useTranslation();

  return (
    <Wrapper flex="column" items="center" justify="center">
      <Inner flex="column" justify="space-between" items="center">
        <CircleCheck items="center" justify="center" flex>
          <CheckOutlined style={{ color: 'var(--color-success)', fontSize: '40px' }} />
        </CircleCheck>
        <h1>{t('finished')}</h1>
        <Statistic>
          <div>
            {t('annotated')} {taskData?.stats?.done}，
          </div>
          <div>
            {t('unannotated')} <span style={{ color: 'red' }}>{taskData?.stats?.new}</span>，
          </div>
          <div>
            {t('skipped')} {taskData?.stats?.skipped}
          </div>
        </Statistic>
        <ButtonWrapper gap="1.5rem">
          <ExportPortal taskId={taskId} mediaType={taskData?.media_type} tools={taskData?.config?.tools}>
            <Button type="primary" size="large">
              {t('export')}
            </Button>
          </ExportPortal>
          <Button type="default" size="large" onClick={handleGoHome}>
            {t('backToSamples')}
          </Button>
        </ButtonWrapper>
      </Inner>
    </Wrapper>
  );
};

export default SamplesFinished;
