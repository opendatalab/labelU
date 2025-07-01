import React, { useLayoutEffect, useMemo, useState } from 'react';
import { Link, useParams, useRevalidator, useRouteLoaderData, useSearchParams } from 'react-router-dom';
import type { ColumnsType, TableProps } from 'antd/es/table';
import { Table, Pagination, Button, Popconfirm, Tag, Tooltip, Avatar, Popover } from 'antd';
import { VideoCard, FlexLayout } from '@labelu/components-react';
import _ from 'lodash-es';
import formatter from '@labelu/formatter';
import styled from 'styled-components';
import { DownOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { useTranslation } from '@labelu/i18n';

import type { PreAnnotationFileResponse, SampleResponse } from '@/api/types';
import { MediaType, TaskStatus } from '@/api/types';
import ExportPortal from '@/components/ExportPortal';
import type { TaskLoaderResult } from '@/loaders/task.loader';
import BlockContainer from '@/layouts/BlockContainer';
import { downloadFromUrl, getThumbnailUrl } from '@/utils';
import { deletePreAnnotationFile } from '@/api/services/preAnnotations';
import { deleteSamples } from '@/api/services/samples';
import { UserAvatar } from '@/components/UserAvatar';
import useMe from '@/hooks/useMe';

import type { TaskStatusProps } from './components/Statistical';
import Statistical, { TaskStatus as TaskStatusComponent } from './components/Statistical';
import GoToEditTask from './components/GoToEditTask';
import type { TaskSampleUser } from '../../hooks/useSampleWs';

const HeaderWrapper = styled(FlexLayout.Header)`
  background-color: #fff;
  height: 3.5rem;
`;

const Samples = () => {
  const routerData = useRouteLoaderData('task') as TaskLoaderResult;
  const samples = _.get(routerData, 'samples.data');
  const revalidator = useRevalidator();
  const preAnnotations = _.get(routerData, 'preAnnotations.data') as any;
  const task = routerData.task;
  const metaData = routerData?.samples?.meta_data;
  const routeParams = useParams();
  const taskId = +routeParams.taskId!;
  const { t, i18n } = useTranslation();
  const me = useMe();
  const isMeTheCreator = task?.created_by?.id === me?.data?.id;

  // 查询参数
  const [searchParams, setSearchParams] = useSearchParams(
    new URLSearchParams({
      // 默认按照最后更新时间倒序
      page: '1',
      size: '10',
    }),
  );

  const taskStatus = _.get(task, 'status');
  const isTaskReadyToAnnotate =
    ![TaskStatus.DRAFT, TaskStatus.IMPORTED].includes(taskStatus!) &&
    task?.config &&
    Object.keys(task?.config).length > 0;
  const [enterRowId, setEnterRowId] = useState<any>(undefined);
  const [selectedSampleIds, setSelectedSampleIds] = useState<any>([]);

  const handleDeleteJsonl = async (id: number) => {
    await deletePreAnnotationFile({
      task_id: taskId,
      file_id: id,
    });

    revalidator.revalidate();
  };

  const handleDeleteSample = async (ids: number[]) => {
    await deleteSamples({ task_id: taskId }, { sample_ids: ids });
    revalidator.revalidate();
  };

  const columns: ColumnsType<SampleResponse | PreAnnotationFileResponse> = [
    {
      title: t('innerId'),
      dataIndex: 'inner_id',
      key: 'inner_id',
      align: 'left',
      sorter: true,
    },
    {
      title: t('filename'),
      dataIndex: ['file', 'filename'],
      key: 'filename',
      align: 'left',
      render: (filename, record) => {
        const _filename = (record as SampleResponse).file?.filename ?? '';

        if ((record as PreAnnotationFileResponse).sample_names) {
          return (
            <span>
              {formatter.format('ellipsis', _.get(record, 'filename'), { maxWidth: 160, type: 'tooltip' })}
              &nbsp;
              <Tag color="processing">{t('preAnnotation')}</Tag>
            </span>
          );
        }
        return formatter.format('ellipsis', _filename, { maxWidth: 160, type: 'tooltip' });
      },
    },
    {
      title: t('dataPreview'),
      dataIndex: 'file',
      key: 'file',
      align: 'left',
      render: (data, record) => {
        if ((record as PreAnnotationFileResponse).sample_names) {
          return '-';
        }

        if (task!.media_type === MediaType.IMAGE) {
          const thumbnailUrl = getThumbnailUrl(data.url!);
          return <img src={thumbnailUrl} style={{ width: '116px', height: '70px' }} />;
        } else if (task!.media_type === MediaType.AUDIO) {
          return <audio src={data?.url} controls />;
        } else {
          return <VideoCard size={{ width: 116, height: 70 }} src={data?.url} showPlayIcon showDuration />;
        }
      },
    },
    {
      title: (
        <>
          {t('preAnnotation')} &nbsp;
          <Tooltip
            title={
              <>
                {t('preAnnotationDescription')}{' '}
                <a
                  href={`https://opendatalab.github.io/labelU/${
                    i18n.language.startsWith('en') ? 'en/' : ''
                  }schema/pre-annotation/json`}
                  target="_blank"
                  rel="noreferrer"
                >
                  {t('example')}
                </a>
              </>
            }
          >
            <QuestionCircleOutlined />
          </Tooltip>
        </>
      ),
      dataIndex: 'is_pre_annotated',
      key: 'is_pre_annotated',
      align: 'left',
      render: (value: boolean, record) => {
        const sampleNames = _.get(record, 'sample_names');

        if (sampleNames) {
          return '';
        }

        return value ? t('yes') : '';
      },
    },
    {
      title: t('annotationState'),
      dataIndex: 'state',
      key: 'state',
      align: 'left',
      width: 90,
      render: (text, record) => {
        if (record.file?.filename?.endsWith('.jsonl')) {
          return '-';
        }

        if (!isTaskReadyToAnnotate) {
          return '-';
        }

        return <TaskStatusComponent status={_.lowerCase(text) as TaskStatusProps['status']} />;
      },
      sorter: true,
    },
    {
      title: t('annotationCount'),
      dataIndex: 'annotated_count',
      key: 'annotated_count',
      align: 'left',
      render: (_unused, record) => {
        const sampleNames = _.get(record, 'sample_names');

        if (sampleNames) {
          return '';
        }

        let result = 0;
        const resultJson = record?.data?.result ? JSON.parse(record?.data?.result) : {};
        for (const key in resultJson) {
          if (key.indexOf('Tool') > -1 && key !== 'textTool' && key !== 'tagTool') {
            const tool = resultJson[key];
            if (!tool.result) {
              let _temp = 0;
              if (tool.length) {
                _temp = tool.length;
              }
              result = result + _temp;
            } else {
              result = result + tool.result.length;
            }
          }
        }
        return result;
      },
      sorter: true,
      width: 90,
    },
    {
      title: t('updaters'),
      dataIndex: 'updaters',
      key: 'updaters',
      align: 'center',
      render: (updaters: TaskSampleUser[], record) => {
        const sampleNames = _.get(record, 'sample_names');

        if (sampleNames) {
          return '-';
        }

        if (!isTaskReadyToAnnotate) {
          return '-';
        }

        if (!updaters || updaters.length === 0) {
          return '-';
        }

        if (updaters.length === 1) {
          return <UserAvatar user={updaters[0]} />;
        }

        return (
          <Button type="text" style={{ padding: '0.25rem', cursor: 'default' }}>
            <FlexLayout items="center" gap=".5rem">
              <Avatar.Group>
                {updaters?.slice(0, 3).map((updater, index) => (
                  <UserAvatar key={index} user={updater} />
                ))}
              </Avatar.Group>
              {updaters.length > 3 && <span>{updaters.length}</span>}
              <Popover
                title={null}
                arrow={false}
                placement="bottom"
                content={
                  <FlexLayout flex="column" gap="1rem">
                    {updaters.map((updater) => (
                      <UserAvatar
                        key={updater.user_id}
                        user={updater}
                        showTooltip={false}
                        shortName={false}
                        style={{ backgroundColor: 'var(--color-primary)', color: '#fff' }}
                      />
                    ))}
                  </FlexLayout>
                }
              >
                <DownOutlined />
              </Popover>
            </FlexLayout>
          </Button>
        );
      },
    },
    {
      title: t('updatedAt'),
      dataIndex: 'updated_at',
      key: 'updated_at',
      align: 'left',
      sorter: true,
      render: (updated_at, record) => {
        const sampleNames = _.get(record, 'sample_names');

        if (sampleNames) {
          return '-';
        }

        if (!isTaskReadyToAnnotate) {
          return '';
        }

        return formatter.format('dateTime', new Date(updated_at), { style: 'YYYY-MM-DD HH:mm' });
      },
    },
    {
      title: '',
      dataIndex: 'option',
      key: 'option',
      width: 140,
      align: 'center',
      fixed: 'right',
      render: (x, record) => {
        const sampleNames = _.get(record, 'sample_names');

        if (record.id !== enterRowId) {
          return '';
        }

        if (sampleNames) {
          return (
            <FlexLayout items="center">
              <Button type="link" onClick={() => downloadFromUrl(record.url, record?.filename)}>
                {t('download')}
              </Button>
              {isMeTheCreator && (
                <Popconfirm title={t('deleteConfirm')} onConfirm={() => handleDeleteJsonl(record.id!)}>
                  <Button type="link" danger>
                    {t('delete')}
                  </Button>
                </Popconfirm>
              )}
            </FlexLayout>
          );
        }

        return (
          <FlexLayout items="center" gap="0.5rem">
            {isTaskReadyToAnnotate && (
              <Link to={`/tasks/${taskId}/samples/${record.id}`}>
                <Button type="link">{t('startAnnotate')}</Button>
              </Link>
            )}
            {isMeTheCreator && (
              <Popconfirm title={t('deleteConfirm')} onConfirm={() => handleDeleteSample([record.id!])}>
                <Button type="link" danger>
                  {t('delete')}
                </Button>
              </Popconfirm>
            )}
          </FlexLayout>
        );
      },
    },
  ];

  const rowSelection: TableProps<SampleResponse>['rowSelection'] = {
    columnWidth: 58,
    onChange: (selectedKeys) => {
      setSelectedSampleIds(selectedKeys);
    },
  };

  const handleTableChange: TableProps<SampleResponse>['onChange'] = (pagination, filters, sorter) => {
    if (!_.isEmpty(pagination)) {
      searchParams.set('page', `${pagination.current}`);
      searchParams.set('size', `${pagination.pageSize}`);
    }

    if (sorter) {
      let sortValue = '';
      // @ts-ignore
      switch (sorter.order) {
        case 'ascend':
          sortValue = 'asc';
          break;
        case 'descend':
          sortValue = 'desc';
          break;
        case undefined:
          sortValue = 'desc';
          break;
      }
      searchParams.set('sort', `${_.get(sorter, 'field')}:${sortValue}`);
    } else {
      searchParams.delete('sort');
    }

    setSearchParams(searchParams);
  };
  const handlePaginationChange = (page: number, pageSize: number) => {
    searchParams.set('page', `${page}`);
    searchParams.set('size', `${pageSize}`);
    setSearchParams(searchParams);
  };

  const onMouseEnterRow = (rowId: any) => {
    setEnterRowId(rowId);
  };
  const onRow = (record: any) => {
    return {
      onMouseLeave: () => setEnterRowId(undefined),
      onMouseOver: () => {
        onMouseEnterRow(record.id);
      },
    };
  };

  useLayoutEffect(() => {
    if (task?.media_type !== MediaType.AUDIO) {
      return;
    }

    const handleOnPlay = (e: Event) => {
      const audios = document.getElementsByTagName('audio');
      // 使当前只有一条音频在播放
      for (let i = 0, len = audios.length; i < len; i++) {
        if (audios[i] !== e.target) {
          (audios[i] as HTMLAudioElement).pause();
        }
      }
    };

    document.addEventListener('play', handleOnPlay, true);

    return () => {
      document.removeEventListener('play', handleOnPlay, true);
    };
  }, [task?.media_type]);

  const data = useMemo(() => {
    return [...(preAnnotations ?? []), ...(samples ?? [])];
  }, [preAnnotations, samples]);

  return (
    <FlexLayout flex="column" full gap="2rem">
      <HeaderWrapper flex items="center">
        <FlexLayout.Content full>
          <BlockContainer>
            {isTaskReadyToAnnotate ? <Statistical /> : <GoToEditTask taskStatus={taskStatus} />}
          </BlockContainer>
        </FlexLayout.Content>
      </HeaderWrapper>

      <FlexLayout.Content scroll>
        <FlexLayout justify="space-between" flex="column" gap="1rem" padding="0 1.5rem 1.5rem">
          <Table
            columns={columns}
            dataSource={data}
            pagination={false}
            rowKey={(record) => record.id!}
            rowSelection={rowSelection}
            onRow={onRow}
            onChange={handleTableChange}
          />
          <FlexLayout justify="space-between">
            <ExportPortal
              taskId={+taskId!}
              sampleIds={selectedSampleIds}
              mediaType={task!.media_type!}
              tools={task?.config?.tools}
            >
              <Button type="link" disabled={selectedSampleIds.length === 0}>
                {t('batchExport')}
              </Button>
            </ExportPortal>
            <Pagination
              current={parseInt(searchParams.get('page') || '1')}
              pageSize={parseInt(searchParams.get('size') || '10')}
              total={metaData?.total}
              showSizeChanger
              showQuickJumper
              onChange={handlePaginationChange}
            />
          </FlexLayout>
        </FlexLayout>
      </FlexLayout.Content>
    </FlexLayout>
  );
};

export default Samples;
