import { useMemo, useCallback, useContext } from 'react';
import type { TableColumnType } from 'antd';
import { Popconfirm, Button, Table, Tooltip, Tag, Form, Input, Select } from 'antd';
import _ from 'lodash-es';
import formatter from '@labelu/formatter';
import { FileOutlined, FolderOpenOutlined, QuestionCircleOutlined, UploadOutlined } from '@ant-design/icons';
import type { RcFile } from 'antd/lib/upload/interface';
import { FlexLayout } from '@labelu/components-react';
import { useRevalidator } from 'react-router';
import { useTranslation } from '@labelu/i18n';

import IconText from '@/components/IconText';
import type { StatusType } from '@/components/Status';
import Status from '@/components/Status';
import { ReactComponent as FileIcon } from '@/assets/svg/file.svg';
import commonController from '@/utils/common';
import NativeUpload from '@/components/NativeUpload';
import { deleteFile } from '@/api/services/task';
import { ReactComponent as UploadBg } from '@/assets/svg/upload-bg.svg';
import { MediaType, FileCloudStorageType } from '@/api/types';
import { FileExtensionText, FileMimeType } from '@/constants/mediaType';
import type { TaskInLoader } from '@/loaders/task.loader';
import { useUploadFileMutation } from '@/api/mutations/attachment';
import { deleteSamples } from '@/api/services/samples';
import { deletePreAnnotationFile } from '@/api/services/preAnnotations';

import { TaskCreationContext } from '../../taskCreation.context';
import { Bar, ButtonWrapper, Header, Left, Right, Spot, UploadArea, Wrapper } from './style';
import imageSchema from './imagePreAnnotationJsonl.schema.json';
import imageJsonSchema from './imagePreAnnotationJson.schema.json';
import audioJsonSchema from './audioPreAnnotationJson.schema.json';
import videoJsonSchema from './videoPreAnnotationJson.schema.json';
import audioSchema from './audioPreAnnotationJsonl.schema.json';
import videoSchema from './videoPreAnnotationJsonl.schema.json';
import { isCorrectFiles, isPreAnnotationFile, normalizeFiles, readFile, UploadStatus } from './utils';

const jsonlMapping = {
  [MediaType.IMAGE]: imageSchema,
  [MediaType.VIDEO]: videoSchema,
  [MediaType.AUDIO]: audioSchema,
};

const jsonMapping = {
  [MediaType.IMAGE]: imageJsonSchema,
  [MediaType.VIDEO]: videoJsonSchema,
  [MediaType.AUDIO]: audioJsonSchema,
};

export interface QueuedFile {
  id?: number;
  url?: string;
  uid: string;
  name: string;
  size: number;
  status: UploadStatus;
  reason?: string;
  file: File;
  // sample id or pre-annotation id
  refId?: number;
}

const InputData = () => {
  // 上传队列，包括成功和失败的任务
  const {
    uploadFileList: fileQueue,
    setUploadFileList: setFileQueue,
    task = {} as NonNullable<TaskInLoader>,
  } = useContext(TaskCreationContext);
  const uploadMutation = useUploadFileMutation();
  const revalidator = useRevalidator();
  const { t, i18n } = useTranslation();

  const statusTextMapping = useMemo(
    () => ({
      [UploadStatus.Uploading]: t('uploading'),
      [UploadStatus.Waiting]: t('uploadPending'),
      [UploadStatus.Success]: t('uploadSuccess'),
      [UploadStatus.Fail]: t('uploadFailed'),
      [UploadStatus.Error]: t('parseError'),
    }),
    [t],
  );

  const taskId = task.id;

  const amountMapping = useMemo(() => {
    let succeeded = 0;
    let failed = 0;
    let uploading = 0;

    for (const file of fileQueue) {
      switch (file.status) {
        case UploadStatus.Success:
          succeeded++;
          break;
        case UploadStatus.Fail:
          failed++;
          break;
        case UploadStatus.Uploading:
          uploading++;
          break;
        default:
          break;
      }
    }
    return {
      succeeded,
      failed,
      uploading,
    };
  }, [fileQueue]);

  const processUpload = useCallback(
    async (files: QueuedFile[], mediaType: MediaType) => {
      // 开始上传
      setFileQueue((pre) => _.uniqBy([...pre, ...files], 'uid'));
      let succeed = 0;
      let failed = 0;

      const { Draft07 } = await import('json-schema-library');
      const jsonSchema = new Draft07(jsonlMapping[mediaType]);

      for (const file of files) {
        const { file: fileBlob } = file;

        // jsonl需要校验文件内容
        if (fileBlob.name.endsWith('.jsonl')) {
          try {
            const content = await readFile(fileBlob, 'text');

            for (const line of content.split('\n')) {
              const jsonLine = JSON.parse(line as string);

              // 校验 jsonl 文件格式
              const errors = jsonSchema.validate(jsonLine);

              if (errors.length > 0) {
                throw new Error(errors.map((error) => error.message).join('; \n'));
              }
            }
          } catch (error: any) {
            setFileQueue((pre) =>
              pre.map((item) => {
                if (item.uid === file.uid) {
                  return {
                    ...item,
                    status: UploadStatus.Error,
                    reason: error.message,
                  };
                }
                return item;
              }),
            );

            continue;
          }
        }

        // 解析labelu导出的json文件
        if (fileBlob.name.endsWith('.json')) {
          try {
            const preAnnotationJsonSchema = new Draft07(jsonMapping[mediaType]);
            const content = await readFile(fileBlob, 'text');
            const json = JSON.parse(content);

            if (!Array.isArray(json)) {
              throw new Error(t('mustBeLabelUJson') as string);
            }

            for (let i = 0; i < json.length; i += 1) {
              if (typeof json[i].result === 'string') {
                json[i].result = JSON.parse(json[i].result);
              } else {
                throw new Error('result should be a string');
              }

              const errors = preAnnotationJsonSchema.validate(json[i]);

              if (errors.length > 0) {
                throw new Error(errors.map((error) => error.message).join('; \n'));
              }
            }
          } catch (error: any) {
            setFileQueue((pre) =>
              pre.map((item) => {
                if (item.uid === file.uid) {
                  return {
                    ...item,
                    status: UploadStatus.Error,
                    reason: error.message,
                  };
                }
                return item;
              }),
            );

            continue;
          }
        }

        if ([UploadStatus.Success, UploadStatus.Uploading].includes(file.status)) {
          continue;
        }

        try {
          const { data } = await uploadMutation.mutateAsync({
            task_id: taskId!,
            file: fileBlob,
          });

          succeed += 1;

          await setFileQueue((pre) =>
            pre.map((item) => {
              if (item.uid === file.uid) {
                return {
                  ...item,
                  ...data,
                  status: UploadStatus.Success,
                };
              }
              return item;
            }),
          );
        } catch (error) {
          failed += 1;
          await setFileQueue((pre) =>
            pre.map((item) => {
              if (item.uid === file.uid) {
                return {
                  ...item,
                  status: UploadStatus.Fail,
                };
              }
              return item;
            }),
          );
        }
      }

      if (succeed > 0 && failed > 0) {
        commonController.notificationWarnMessage(
          { message: `${succeed} ${t('filesUploaded')}${failed} ${t('filesFailed')}` },
          3,
        );
      } else if (succeed > 0 && failed === 0) {
        commonController.notificationSuccessMessage({ message: `${succeed} ${t('filesUploaded')}` }, 3);
      } else if (failed > 0 && succeed === 0) {
        commonController.notificationWarnMessage({ message: `${failed} ${t('filesFailed')}` }, 3);
      }
    },
    [setFileQueue, taskId, uploadMutation, t],
  );

  const handleFilesChange = (files: RcFile[]) => {
    const isCorrectCondition = isCorrectFiles(files, task.media_type!);

    if (!isCorrectCondition) {
      return;
    } else {
      commonController.notificationSuccessMessage({ message: t('added') + files.length + t('filesToList') }, 3);
    }

    processUpload(normalizeFiles(files), task.media_type!);
  };

  const handleFileDelete = useCallback(
    async (file: QueuedFile) => {
      if (file.status === UploadStatus.Success) {
        await deleteFile(
          { task_id: taskId! },
          {
            attachment_ids: [file.id!],
          },
        );
      }

      if (file.refId) {
        if (isPreAnnotationFile(file.name)) {
          // 删除预标注
          await deletePreAnnotationFile({
            task_id: taskId!,
            file_id: file.refId,
          });
        } else {
          // 删除样本
          await deleteSamples(
            {
              task_id: taskId!,
            },
            { sample_ids: [file.refId] },
          );
        }
      }

      setFileQueue((pre) => pre.filter((item) => item.uid !== file.uid));
      commonController.notificationSuccessMessage({ message: t('fileDeleted') }, 3);
      revalidator.revalidate();
    },
    [revalidator, setFileQueue, taskId, t],
  );

  const tableColumns = useMemo(() => {
    return [
      {
        title: t('filename'),
        dataIndex: 'name',
        align: 'left',
        responsive: ['md', 'lg', 'sm'],
        key: 'name',
        render: (text: string) => {
          return (
            <IconText icon={<FileIcon />}>
              <div>
                {formatter.format('ellipsis', text, { maxWidth: 540, type: 'tooltip' })}
                &nbsp;
                {isPreAnnotationFile(text) && <Tag color="processing">{t('preAnnotation')}</Tag>}
              </div>
            </IconText>
          );
        },
      },
      {
        title: 'Url',
        dataIndex: 'url',
        align: 'left',
        responsive: ['md', 'lg'],
        key: 'url',
        render: (text: string) => {
          return formatter.format('ellipsis', `${location.protocol}//${location.host}${text}`, {
            maxWidth: 160,
            type: 'tooltip',
          });
        },
      },
      {
        title: t('status'),
        dataIndex: 'status',
        align: 'left',
        responsive: ['md', 'lg', 'sm'],
        width: 160,
        key: 'status',
        render: (text: UploadStatus, record: QueuedFile) => {
          return (
            <FlexLayout.Item flex gap="0.5rem">
              <Status type={_.lowerCase(record.status) as StatusType} icon={<Spot />}>
                {statusTextMapping[text]}
              </Status>
              {record.reason && (
                <Tooltip title={record.reason}>
                  <QuestionCircleOutlined />
                </Tooltip>
              )}
            </FlexLayout.Item>
          );
        },
      },
      {
        title: t('actions'),
        dataIndex: 'action',
        align: 'left',
        responsive: ['md', 'lg'],
        width: 160,
        key: 'action',
        render: (text: string, record: QueuedFile) => {
          return (
            <>
              {record.status === UploadStatus.Fail && (
                <Button
                  type="link"
                  size="small"
                  onClick={() => {
                    processUpload(fileQueue, task.media_type!);
                  }}
                >
                  {t('reupload')}
                </Button>
              )}
              <Popconfirm
                title={t('deleteConfirm')}
                onConfirm={() => {
                  handleFileDelete(record);
                }}
              >
                <Button type="link" size="small" danger>
                  {t('delete')}
                </Button>
              </Popconfirm>
            </>
          );
        },
      },
    ] as TableColumnType<QueuedFile>[];
  }, [t, statusTextMapping, processUpload, fileQueue, task.media_type, handleFileDelete]);

  return (
    <Wrapper flex="column" full>
      <Header flex items="center">
        <Bar />
        <h3>{t('uploadData')}</h3>
      </Header>
      <FlexLayout.Content flex items="stretch" gap="1.5rem">
        <Left flex="column">
          <h4>{t('filesCloudStorageInfo')}</h4>
          <Form.Item
            label={t('filesCloudStorageType')}
            name="file_cloud_storage_type"
            rules={[{ required: true, message: t('fileCloudStorageTypeRequired') }]}
          >
            <Select
              placeholder={t('selectFileStorageTypePlease')}
              options={[
                {
                  label: t('storageCos'),
                  value: FileCloudStorageType.COS,
                },
                {
                  label: t('storageOss'),
                  value: FileCloudStorageType.OSS,
                },
              ]}
            />
          </Form.Item>
          <Form.Item
            label={t('fileCloudUrl')}
            name="file_cloud_url"
            required
            rules={[{ required: true, message: t('fileCloudUrlRequired') }]}
          >
            <Input placeholder={t('fileCloudUrlRequired')} maxLength={100} />
          </Form.Item>

          <h4>{t('filesUpload')}</h4>
          <UploadArea flex="column" gap="1rem" items="center">
            <UploadBg />

            <FlexLayout gap="1rem">
              <NativeUpload
                type="primary"
                icon={<FileOutlined />}
                onChange={handleFilesChange}
                directory={false}
                multiple={true}
                accept={FileMimeType[task.media_type!]}
              >
                {t('uploadFile')}
              </NativeUpload>
              <NativeUpload
                type="primary"
                ghost
                icon={<FolderOpenOutlined />}
                onChange={handleFilesChange}
                directory={true}
                accept={FileMimeType[task.media_type!]}
              >
                {t('uploadFolder')}
              </NativeUpload>
            </FlexLayout>
            <ButtonWrapper flex="column" items="center" gap="0.25rem">
              <div>
                {t('fileTypeSupportsInclude')}
                {FileExtensionText[task.media_type!]}
              </div>
            </ButtonWrapper>
          </UploadArea>
          <h4>{t('preAnnotationFileUpload')}</h4>
          <FlexLayout.Item flex="column" items="flex-start" gap="0.5rem">
            <NativeUpload
              icon={<UploadOutlined />}
              onChange={handleFilesChange}
              directory={false}
              multiple={true}
              accept={'.jsonl, .json'}
            >
              {t('uploadFile')}
            </NativeUpload>
            <div style={{ color: '#999', fontSize: 12 }}>
              {t('preAnnotationFileUploadDescription')}
              <a
                target="_blank"
                href={`https://opendatalab.github.io/labelU/${
                  i18n.language.startsWith('en') ? 'en/' : ''
                }schema/pre-annotation/json`}
                rel="noreferrer"
              >
                {t('example')}
              </a>
            </div>
          </FlexLayout.Item>
        </Left>
        <Right flex="column" gap="1rem">
          {fileQueue.length > 0 && (
            <FlexLayout.Header items="center" gap="0.25rem" flex>
              <b>{t('uploadQueue')}</b>
              <div>{t('uploading')}</div>
              <FlexLayout gap=".25rem">
                <span style={{ display: 'inline-block', color: 'var(--color-primary)' }}>
                  {amountMapping.uploading}
                </span>
              </FlexLayout>
              <FlexLayout gap=".25rem">
                <span>{t('uploadSuccess')}</span>
                <Status type="success" icon={null} style={{ display: 'inline-block' }}>
                  {amountMapping.succeeded}
                </Status>
                <span>个，</span>
              </FlexLayout>
              <FlexLayout gap=".25rem">
                <span>{t('uploadFailed')}</span>
                <Status type="failed" icon={null} style={{ display: 'inline-block' }}>
                  {amountMapping.failed}
                </Status>
              </FlexLayout>
            </FlexLayout.Header>
          )}
          <FlexLayout.Content scroll>
            <Table columns={tableColumns} dataSource={fileQueue} rowKey={(record) => record.uid} />
          </FlexLayout.Content>
        </Right>
      </FlexLayout.Content>
    </Wrapper>
  );
};

export default InputData;
