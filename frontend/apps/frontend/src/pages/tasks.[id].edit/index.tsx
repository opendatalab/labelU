import React, { useState, useEffect, useMemo, useRef, useCallback, useLayoutEffect } from 'react';
import { Button, Form } from 'antd';
import { useLocation, useNavigate, useParams, useRevalidator, useRouteLoaderData } from 'react-router-dom';
import _, { filter, isEmpty, size } from 'lodash-es';
import { omit } from 'lodash/fp';
import { ArrowLeftOutlined, ArrowRightOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import { Bridge } from 'iframe-message-bridge';
import { FlexLayout } from '@labelu/components-react';
import { useIsFetching, useIsMutating } from '@tanstack/react-query';
import { useTranslation } from '@labelu/i18n';

import { message, modal } from '@/StaticAnt';
import type { OkRespCreateSampleResponse, TaskResponse } from '@/api/types';
import { MediaType, TaskStatus } from '@/api/types';
import { createSamples, deleteSamples } from '@/api/services/samples';
import { deleteFile, deleteTask } from '@/api/services/task';
import { convertAudioAndVideoConfig } from '@/utils/convertAudioAndVideoConfig';
import type { TaskLoaderResult } from '@/loaders/task.loader';
import { useAddTaskMutation, useUpdateTaskConfigMutation } from '@/api/mutations/task';
import { convertImageConfig } from '@/utils/convertImageConfig';
import { createPreAnnotations } from '@/api/services/preAnnotations';
import type { ToolsConfigState } from '@/types/toolConfig';

import type { QueuedFile } from './partials/InputData';
import InputData from './partials/InputData';
import AnnotationConfig from './partials/AnnotationConfig';
import InputInfoConfig from './partials/InputInfoConfig';
import type { StepData } from './components/Step';
import Step from './components/Step';
import commonController from '../../utils/common';
import { TaskCreationContext } from './taskCreation.context';
import { ContentWrapper, PreviewFrame, StepRow } from './style';
import { isPreAnnotationFile, UploadStatus } from './partials/InputData/utils';

enum StepEnum {
  Basic = 'basic',
  Upload = 'upload',
  Config = 'config',
}

const partialMapping = {
  [StepEnum.Basic]: InputInfoConfig,
  [StepEnum.Upload]: InputData,
  [StepEnum.Config]: AnnotationConfig,
};

const StyledFooter = styled.div`
  display: flex;
  justify-content: end;
  margin-top: 1rem;
  gap: 0.5rem;
`;

function isContainEmptyOption(config: ToolsConfigState) {
  for (const tool of config.tools) {
    const attributes = tool.config?.attributes ?? [];

    if (!attributes || attributes.length === 0) {
      return 'attribute';
    }

    const toolName = tool.tool;

    // 检查全局工具里的属性是否有空选项
    if (['tagTool', 'textTool'].includes(toolName)) {
      for (const attribute of attributes) {
        if (attribute.type === 'enum' && attribute.options.length === 0) {
          return 'option';
        }
      }
    }

    for (const attribute of attributes) {
      if (Array.isArray(attribute.attributes)) {
        for (const subAttribute of attribute.attributes) {
          if (subAttribute.type === 'enum' && subAttribute.options.length === 0) {
            return 'option';
          }
        }
      }
    }
  }
}

interface TaskStep extends StepData {
  value: StepEnum;
}

export interface PartialConfigProps {
  task: TaskResponse;
  updateFormData: (field: string) => (value: string) => void;
}

const CreateTask = () => {
  const revalidator = useRevalidator();
  const routerLoaderData = useRouteLoaderData('task') as TaskLoaderResult;
  const taskData = _.get(routerLoaderData, 'task');
  const samples = _.get(routerLoaderData, 'samples');
  const toolsConfig = taskData?.config;
  const navigate = useNavigate();
  const routeParams = useParams();
  const location = useLocation();
  const [annotationFormInstance] = Form.useForm();
  const [basicFormInstance] = Form.useForm();
  const modalRef = useRef<any>(null);
  const previewIframeRef = useRef<HTMLIFrameElement>(null);
  const bridgeRef = useRef<Bridge | null>(null);
  const { t } = useTranslation();

  const taskId = routeParams.taskId ? parseInt(routeParams.taskId, 10) : 0;
  const [currentStep, setCurrentStep] = useState<StepEnum>(
    location.hash ? (location.hash.replace('#', '') as StepEnum) : StepEnum.Basic,
  );
  const searchParams = new URLSearchParams(location.search);
  const isCreateNewTask = searchParams.get('isNew') === 'true';
  const [isAnnotationFormValid, toggleAnnotationFormValidation] = useState<boolean>(true);

  const addTask = useAddTaskMutation();
  const updateTaskConfig = useUpdateTaskConfigMutation(taskId);

  const isFetching = useIsFetching();
  const isMutating = useIsMutating();

  // 缓存上传的文件清单
  const [uploadFileList, setUploadFileList] = useState<QueuedFile[]>([]);

  const updateCurrentStep = useCallback(
    (step: StepEnum) => {
      setCurrentStep(step);
      navigate({
        pathname: location.pathname,
        hash: step,
        search: location.search,
      });
    },
    [location.pathname, location.search, navigate],
  );

  const stepTitleMapping = useMemo(
    () => ({
      [StepEnum.Basic]: t('basicConfig'),
      [StepEnum.Upload]: t('uploadData'),
      [StepEnum.Config]: t('annotationConfig'),
    }),
    [t],
  );

  const partials = useMemo(() => {
    return _.chain(partialMapping)
      .toPairs()
      .map(([key, Partial], index) => {
        return (
          <FlexLayout.Content key={index} style={{ display: currentStep === key ? 'flex' : 'none' }} flex="column">
            <Partial />
          </FlexLayout.Content>
        );
      })
      .value();
  }, [currentStep]);
  const loading = isMutating > 0 || isFetching > 0;
  const isExistTask = taskId > 0;
  const taskStatus = _.get(taskData, 'status') as TaskStatus;
  const stepDataSource: TaskStep[] = useMemo(
    () => [
      {
        title: stepTitleMapping[StepEnum.Basic],
        value: StepEnum.Basic,
        isFinished: isExistTask,
      },
      {
        title: stepTitleMapping[StepEnum.Upload],
        value: StepEnum.Upload,
        isFinished: taskStatus && taskStatus !== TaskStatus.DRAFT,
      },
      {
        title: stepTitleMapping[StepEnum.Config],
        value: StepEnum.Config,
        isFinished: [TaskStatus.CONFIGURED, TaskStatus.FINISHED, TaskStatus.INPROGRESS].includes(taskStatus),
      },
    ],
    [isExistTask, stepTitleMapping, taskStatus],
  );

  useEffect(() => {
    if (!location.hash) {
      return;
    }

    setCurrentStep(location.hash.replace('#', '') as StepEnum);
  }, [location.hash]);

  // 将store中的task toolConfig数据同步到本地页面中
  useEffect(() => {
    annotationFormInstance.setFieldsValue(toolsConfig);
  }, [annotationFormInstance, toolsConfig]);

  useEffect(() => {
    basicFormInstance.setFieldsValue(taskData);
  }, [annotationFormInstance, basicFormInstance, taskData]);

  useEffect(() => {
    if (isEmpty(toolsConfig?.tools)) {
      toggleAnnotationFormValidation(false);
    }
  }, [toolsConfig?.tools]);

  const onAnnotationFormChange = useCallback(() => {
    annotationFormInstance.validateFields().then((values) => {
      toggleAnnotationFormValidation(size(values.tools) > 0);
    });
  }, [annotationFormInstance]);

  const [template, setTemplate] = useState<unknown>(null);

  const handleSave = useCallback(
    async function (isFromCancel?: boolean) {
      try {
        await annotationFormInstance.validateFields();
      } catch (err) {
        commonController.notificationErrorMessage({ message: t('pleaseCheckToolConfig') }, 2);
        return;
      }

      const annotationConfig = annotationFormInstance.getFieldsValue();
      const emptyType = isContainEmptyOption(annotationConfig);

      if (emptyType === 'attribute') {
        commonController.notificationErrorMessage({ message: t('mustHaveAtLeastOneAttribute') }, 2);
        return;
      }

      if (emptyType === 'option') {
        commonController.notificationErrorMessage({ message: t('mustHaveAtLeastOneOption') }, 2);
        return;
      }

      if (
        _.chain(annotationConfig).get('tools').isEmpty().value() &&
        currentStep === StepEnum.Config &&
        !isFromCancel
      ) {
        commonController.notificationErrorMessage({ message: t('pleaseSelectTool') }, 2);
        return;
      }

      return updateTaskConfig
        .mutateAsync({
          ...taskData,
          ...basicFormInstance.getFieldsValue(),
          config: JSON.stringify(annotationConfig),
        })
        .then(() => {
          navigate(`/tasks/${taskData!.id}`);
          revalidator.revalidate();
        });
    },
    [annotationFormInstance, basicFormInstance, currentStep, navigate, revalidator, t, taskData, updateTaskConfig],
  );

  const [previewVisible, setPreviewVisible] = useState(false);
  const handleOpenPreview = useCallback(() => {
    annotationFormInstance
      .validateFields()
      .then(() => {
        setPreviewVisible(true);
      })
      .catch(() => {
        commonController.notificationErrorMessage({ message: t('pleaseCheckToolConfig') }, 1);
      });
  }, [annotationFormInstance, t]);

  const updateFileQueue = useCallback((files: any[], sampleIds: number[] | undefined = []) => {
    const fileIdSampleIdMapping = _.chain(files)
      .map((item, index) => {
        return [item.file_id, sampleIds[index]];
      })
      .fromPairs()
      .value();

    setUploadFileList((prev) => {
      return prev.map((item) => {
        if (fileIdSampleIdMapping[item.id!]) {
          return {
            ...item,
            refId: fileIdSampleIdMapping[item.id!],
          };
        }
        return item;
      });
    });
  }, []);

  const correctSampleIdsMappings = useMemo(
    () =>
      _.chain(samples)
        .get('data')
        .mapKeys((item) => {
          return item.file?.id;
        })
        .value(),
    [samples],
  );

  const submitForm: (isFromCancel?: boolean) => Promise<unknown> = useCallback(
    async function (isFromCancel) {
      let basicFormValues;
      try {
        basicFormValues = await basicFormInstance.validateFields();
      } catch (err) {
        return Promise.reject();
      }

      const mediaFileList = [];
      const preAnnotationFiles = [];

      for (const file of uploadFileList) {
        if (isPreAnnotationFile(file.file.name) && file.status === UploadStatus.Success && _.isNil(file.refId)) {
          preAnnotationFiles.push({
            file_id: file.id!,
          });
        } else if (file.status === UploadStatus.Success && _.isNil(file.refId)) {
          mediaFileList.push({
            file_id: file.id!,
            data: {
              result: '{}',
            },
          });
        }
      }

      if (isExistTask) {
        if (currentStep === StepEnum.Upload) {
          let response: OkRespCreateSampleResponse | undefined;
          if (!_.isEmpty(mediaFileList)) {
            response = await createSamples(taskId, mediaFileList);

            updateFileQueue(mediaFileList, response?.data?.ids);
          }

          if (!_.isEmpty(preAnnotationFiles)) {
            response = await createPreAnnotations(taskId, preAnnotationFiles);

            updateFileQueue(preAnnotationFiles, response?.data?.ids);
          }
        }

        const annotationConfig = annotationFormInstance.getFieldsValue();
        const config = omit(['media_type'])(annotationConfig);

        revalidator.revalidate();

        return updateTaskConfig
          .mutateAsync({
            ...taskData,
            ...basicFormValues,
            status: taskData?.status === TaskStatus.DRAFT ? TaskStatus.IMPORTED : taskData?.status,
            config: isCreateNewTask ? null : JSON.stringify(config),
          })
          .then(() => {
            if (isFromCancel) {
              navigate('/tasks');
            }
          });
      } else {
        return addTask.mutateAsync(basicFormValues).then((res) => {
          const newTask = res.data;

          // 取消并保存时，跳转到任务列表页
          if (isFromCancel) {
            navigate('/tasks');
          } else if (newTask) {
            navigate(`/tasks/${newTask.id}/edit${location.search}#${StepEnum.Upload}`);
          }
          return Promise.reject();
        });
      }
    },
    [
      addTask,
      annotationFormInstance,
      basicFormInstance,
      currentStep,
      isCreateNewTask,
      isExistTask,
      location.search,
      navigate,
      revalidator,
      taskData,
      taskId,
      updateFileQueue,
      updateTaskConfig,
      uploadFileList,
    ],
  );

  const handleCancel = useCallback(async () => {
    // 在上传数据界面取消时，需要删除已上传的文件\删除已创建的任务
    const uploadedFiles = filter(uploadFileList, (item) => item.status === UploadStatus.Success);
    if (uploadedFiles.length > 0) {
      await deleteFile(
        { task_id: taskId },
        {
          attachment_ids: uploadedFiles.map((item) => item.id!),
        },
      );

      const uploadedSampleIds = uploadedFiles
        .filter((item) => correctSampleIdsMappings[item.id!])
        .map((item) => correctSampleIdsMappings[item.id!].id!);

      if (uploadedSampleIds.length > 0) {
        await deleteSamples(
          {
            task_id: taskId,
          },
          { sample_ids: uploadedSampleIds },
        );
      }
    }

    if (isCreateNewTask && isExistTask) {
      await deleteTask(taskId);
    }

    modalRef.current.destroy();
    navigate('/tasks');
  }, [correctSampleIdsMappings, isCreateNewTask, isExistTask, navigate, taskId, uploadFileList]);

  const handleCancelConfirm = useCallback(() => {
    modalRef.current = modal.confirm({
      title: t('confirm'),
      content: t('saveUnModified'),
      okText: t('saveAndExit'),
      cancelText: t('dontSave'),
      closable: true,
      footer: (
        <StyledFooter>
          <Button onClick={handleCancel}>{t('dontSave')}</Button>
          <Button
            type="primary"
            onClick={async () => {
              modalRef.current.destroy();

              if (currentStep !== StepEnum.Config) {
                await submitForm(true);
              } else {
                await handleSave(true);
              }
            }}
          >
            {t('saveAndExit')}
          </Button>
        </StyledFooter>
      ),
    });
  }, [t, handleCancel, currentStep, submitForm, handleSave]);

  const handleNextStep = useCallback(
    async function (step: TaskStep | React.MouseEvent) {
      let nextStep = step;
      // 点击下一步时，step为事件参数
      if ((step as React.MouseEvent).target) {
        const stepIndex = stepDataSource.findIndex((item) => item.value === currentStep);
        nextStep = stepDataSource[stepIndex + 1];
      }

      // 如果是从基本信息步骤到下一步，需要校验基本信息表单
      if (currentStep === StepEnum.Basic) {
        try {
          await basicFormInstance.validateFields();
        } catch (err) {
          return;
        }
      }

      // 如果是从「数据导入」到下一步，没有文件时不可进入下一步
      if (
        currentStep === StepEnum.Upload &&
        isEmpty(samples?.data) &&
        filter(uploadFileList, (item) => item.status === UploadStatus.Success && !isPreAnnotationFile(item.name))
          .length === 0
      ) {
        message.error(t('atLeastUploadAFile'));
        return;
      }

      // 文件错误
      if (filter(uploadFileList, (item) => item.status === UploadStatus.Error).length > 0) {
        message.error(t('pleaseHandleErrorFile'));
        return;
      }

      submitForm()
        .then(() => {
          updateCurrentStep((nextStep as TaskStep).value);
          revalidator.revalidate();
        })
        .catch(() => {});
    },
    [
      basicFormInstance,
      currentStep,
      revalidator,
      samples?.data,
      stepDataSource,
      submitForm,
      updateCurrentStep,
      uploadFileList,
      t,
    ],
  );

  const handlePrevStep = async (step: TaskStep, lastStep: TaskStep) => {
    // 如果是从标注配置步骤回到上一步，需要校验配置表单
    if (lastStep.value === StepEnum.Config) {
      try {
        await annotationFormInstance.validateFields();
      } catch (err) {
        message.error(t('pleaseCheckToolConfig'));
        return;
      }

      if (previewVisible) {
        setPreviewVisible(false);
      }
    }
    submitForm()
      .then(() => {
        updateCurrentStep(step.value);
      })
      .catch(() => {});
  };

  const actionNodes = useMemo(() => {
    if (currentStep === StepEnum.Config) {
      if (previewVisible) {
        return (
          <Button onClick={() => setPreviewVisible(false)}>
            <ArrowLeftOutlined />
            {t('exitPreview')}
          </Button>
        );
      }
      const previewDisabled = !isAnnotationFormValid || isEmpty(samples?.data);

      return (
        <FlexLayout gap=".5rem">
          <Button onClick={handleOpenPreview} disabled={previewDisabled}>
            {t('preview')}
            <ArrowRightOutlined />
          </Button>
          <Button onClick={handleCancelConfirm}>{t('cancel')}</Button>
          <Button loading={loading} type="primary" onClick={commonController.debounce(handleSave, 200)}>
            {t('save')}
          </Button>
        </FlexLayout>
      );
    }

    return (
      <FlexLayout gap=".5rem">
        <Button onClick={handleCancelConfirm}>{t('cancel')}</Button>
        <Button loading={loading} type="primary" onClick={commonController.debounce(handleNextStep, 100)}>
          {t('nextStep')}
        </Button>
      </FlexLayout>
    );
  }, [
    currentStep,
    handleCancelConfirm,
    loading,
    handleNextStep,
    previewVisible,
    isAnnotationFormValid,
    samples?.data,
    handleOpenPreview,
    handleSave,
    t,
  ]);

  const taskCreationContextValue = useMemo(
    () => ({
      uploadFileList,
      setUploadFileList,
      annotationFormInstance,
      selectedTemplate: template,
      onTemplateSelect: setTemplate,
      basicFormInstance,
      task: taskData as NonNullable<TaskLoaderResult['task']>,
      onAnnotationFormChange,
    }),
    [uploadFileList, annotationFormInstance, template, basicFormInstance, taskData, onAnnotationFormChange],
  );

  useLayoutEffect(() => {
    if (!previewIframeRef.current) {
      return;
    }

    if (bridgeRef.current) {
      bridgeRef.current.destroy();
      bridgeRef.current = null;
    }

    bridgeRef.current = new Bridge(previewIframeRef.current.contentWindow!);
    bridgeRef.current.on('ready', () => {
      if (!taskData?.media_type) {
        console.warn('media_type is empty');
        return;
      }

      let _config;

      if ([MediaType.VIDEO, MediaType.AUDIO].includes(taskData?.media_type)) {
        _config = convertAudioAndVideoConfig(annotationFormInstance.getFieldsValue());
      } else if (taskData?.media_type === MediaType.IMAGE) {
        _config = convertImageConfig(annotationFormInstance.getFieldsValue());
      }

      if (bridgeRef.current) {
        bridgeRef.current.post('preview', _config);
      }
    });
  }, [previewVisible, annotationFormInstance, taskData?.media_type]);

  return (
    <FlexLayout.Content flex="column">
      <StepRow flex items="center" justify="space-between">
        <FlexLayout.Header>
          <Step steps={stepDataSource} currentStep={currentStep} onNext={handleNextStep} onPrev={handlePrevStep} />
        </FlexLayout.Header>
        <FlexLayout.Footer>{actionNodes}</FlexLayout.Footer>
      </StepRow>
      <ContentWrapper scroll flex="column">
        <TaskCreationContext.Provider value={taskCreationContextValue}>
          <FlexLayout.Content style={{ display: previewVisible ? 'none' : 'flex' }} flex="column">
            {partials}
          </FlexLayout.Content>

          {previewVisible && (
            <PreviewFrame
              referrerPolicy="no-referrer"
              ref={previewIframeRef}
              src={`/tasks/${taskData!.id}/samples/${samples?.data?.[0].id}?noSave=true`}
            />
          )}
        </TaskCreationContext.Provider>
      </ContentWrapper>
    </FlexLayout.Content>
  );
};

export default CreateTask;
