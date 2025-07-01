import { Alert, Button, Pagination, Popover } from 'antd';
import { useNavigate, useRouteLoaderData, useSearchParams } from 'react-router-dom';
import _ from 'lodash';
import styled from 'styled-components';
import { FlexLayout } from '@labelu/components-react';
import { useTranslation } from '@labelu/i18n';

import type { TaskListResponseWithStatics } from '@/api/types';
import { usePageSize } from '@/hooks/usePageSize';
import { ResponsiveGrid } from '@/components/ResponsiveGrid';

import TaskCard from './components/taskCard';
import NullTask from './components/nullTask';

const Wrapper = styled(FlexLayout)`
  height: calc(100vh - var(--header-height));
  padding: 0 1.5rem;
  box-sizing: border-box;
`;

const CardsWrapper = styled(ResponsiveGrid)`
  height: 100%;
`;

const Header = styled(FlexLayout.Header)`
  padding: 1rem 0;
`;

const Footer = styled(FlexLayout.Footer)`
  padding: 1rem 0;
`;

const AppVersion = styled(FlexLayout.Footer)`
  text-align: center;
  color: var(--color-text-tertiary);
`;

const TaskCardItem = styled(TaskCard)``;

const TaskList = () => {
  const navigate = useNavigate();
  const routerLoaderData = useRouteLoaderData('tasks') as TaskListResponseWithStatics;
  const tasksResponse = _.get(routerLoaderData, 'data');
  const tasks = _.get(tasksResponse, 'data', []);
  const meta_data = _.get(tasksResponse, 'meta_data');
  const labeluVersion = _.get(routerLoaderData, ['headers', 'labelu-version']);
  const pageSize = usePageSize();
  const { t, i18n } = useTranslation();

  const [searchParams, setSearchParams] = useSearchParams({
    size: String(pageSize),
  });

  const createTask = () => {
    navigate('/tasks/0/edit?isNew=true');
  };

  const versionInfo = (
    <div>
      frontend: {_.get(window.__frontend, 'version', 'unknown')}
      <br />
      {_.chain(window.__frontend.deps)
        .keys()
        .map((key) => {
          return (
            <div key={key}>
              {key}: {window.__frontend.deps[key]}
            </div>
          );
        })
        .value()}
    </div>
  );

  return (
    <Wrapper flex="column">
      <FlexLayout.Content scroll flex="column">
        {window.IS_ONLINE && (
          <Alert
            type="info"
            style={{
              marginTop: '1rem',
            }}
            showIcon
            message={
              <div>
                {t('demoTips')}
                <a
                  data-wiz="local-deploy-alert"
                  href={`https://opendatalab.github.io/labelU/${
                    i18n.language.startsWith('en') ? 'en/' : ''
                  }guide/install`}
                  target="_blank"
                  rel="noreferrer"
                >
                  {t('localDeploy')}
                </a>
              </div>
            }
          />
        )}
        {tasks.length > 0 && (
          <Header>
            <Button type="primary" onClick={createTask}>
              {t('Create Task')}
            </Button>
          </Header>
        )}
        <FlexLayout.Content scroll>
          {meta_data && meta_data?.total > 0 ? (
            <CardsWrapper>
              {tasks.map((cardInfo: any, cardInfoIndex: number) => {
                return <TaskCardItem key={cardInfoIndex} cardInfo={cardInfo} />;
              })}
            </CardsWrapper>
          ) : (
            <NullTask />
          )}
        </FlexLayout.Content>
      </FlexLayout.Content>
      <Footer flex="row" items="flex-between" justify="space-between">
        <AppVersion>
          <Popover content={versionInfo}>labelu@{labeluVersion}</Popover>
        </AppVersion>
        {meta_data && searchParams && meta_data?.total > pageSize && (
          <Pagination
            defaultCurrent={searchParams.get('page') ? +searchParams.get('page')! : 1}
            total={meta_data?.total ?? 0}
            pageSize={+searchParams.get('size')!}
            onChange={(value: number, _pageSize: number) => {
              searchParams.set('size', String(_pageSize));
              searchParams.set('page', String(value));
              setSearchParams(searchParams);
            }}
          />
        )}
      </Footer>
    </Wrapper>
  );
};

export default TaskList;
