import { useState, createRef, useMemo, useCallback, useRef, useLayoutEffect, useEffect } from 'react';
import _ from 'lodash-es';
import { Empty, Spin, message } from 'antd';
import { Annotator } from '@labelu/video-annotator-react';
import type { AudioAndVideoAnnotatorRef } from '@labelu/audio-annotator-react';
import { Annotator as AudioAnnotator } from '@labelu/audio-annotator-react';
import { useSearchParams, useParams, useRouteLoaderData } from 'react-router-dom';
import { Bridge } from 'iframe-message-bridge';
import type { ImageAnnotatorProps, AnnotatorRef as ImageAnnotatorRef } from '@labelu/image-annotator-react';
import { Annotator as ImageAnnotator } from '@labelu/image-annotator-react';
import { useIsFetching, useIsMutating } from '@tanstack/react-query';
import { FlexLayout } from '@labelu/components-react';
import type { ToolName } from '@labelu/image';
import type { ILabel } from '@labelu/interface';
import { useTranslation } from '@labelu/i18n';

import { MediaType, SampleState, type SampleResponse } from '@/api/types';
import { useScrollFetch } from '@/hooks/useScrollFetch';
import type { getSample } from '@/api/services/samples';
import { getSamples } from '@/api/services/samples';
import { convertAudioAndVideoConfig } from '@/utils/convertAudioAndVideoConfig';
import { convertAudioAndVideoSample, convertMediaAnnotations } from '@/utils/convertAudioAndVideoSample';
import type { TaskLoaderResult } from '@/loaders/task.loader';
import { convertImageConfig } from '@/utils/convertImageConfig';
import { convertImageAnnotations, convertImageSample } from '@/utils/convertImageSample';
import { TOOL_NAME } from '@/constants/toolName';
import useMe from '@/hooks/useMe';

import SlideLoader from './components/slideLoader';
import AnnotationRightCorner from './components/annotationRightCorner';
import AnnotationContext from './annotation.context';
import { LoadingWrapper, Wrapper } from './style';
import useSampleWs from '../../hooks/useSampleWs';

type AllToolName = ToolName | 'segment' | 'frame' | 'tag' | 'text';

export const imageAnnotationRef = createRef<ImageAnnotatorRef>();
export const videoAnnotationRef = createRef<AudioAndVideoAnnotatorRef>();
export const audioAnnotationRef = createRef<AudioAndVideoAnnotatorRef>();

const AnnotationPage = () => {
  const routeParams = useParams();
  const { task } = useRouteLoaderData('task') as TaskLoaderResult;
  const sample = (useRouteLoaderData('annotation') as any).sample as Awaited<ReturnType<typeof getSample>>;
  const preAnnotation = (useRouteLoaderData('annotation') as any).preAnnotation;
  const { t } = useTranslation();

  const preAnnotationConfig = useMemo(() => {
    const result: Partial<Record<AllToolName, any>> = {};

    if (preAnnotation) {
      const preAnnotationResult = JSON.parse(_.get(preAnnotation, 'data[0].data', 'null'));

      if (!preAnnotationResult) {
        return {};
      }

      const config = preAnnotationResult.config;

      if (!config) {
        return {};
      }

      Object.keys(preAnnotationResult.config).forEach((key) => {
        let toolName = key.replace(/Tool$/, '') as AllToolName;

        if (key.includes('audio') || key.includes('video')) {
          // audioSegmentTool => segment
          toolName = toolName.replace(/audio|video/, '').toLowerCase() as AllToolName;
        }

        result[toolName] = preAnnotationResult.config[key as keyof typeof config];
      });
    }

    return result;
  }, [preAnnotation]);
  const preAnnotations = useMemo(() => {
    if (!preAnnotation) {
      return {};
    }

    const preAnnotationResult = JSON.parse(_.get(preAnnotation, 'data[0].data', 'null'));
    let _annotations = _.get(preAnnotationResult, 'annotations', {});
    const preAnnotationFile = _.get(preAnnotation, 'data[0].file', {});
    // 兼容json预标注
    if (preAnnotationFile.filename?.endsWith('.json')) {
      _annotations = _.chain(preAnnotationResult)
        .get('result.annotations')
        .map((item) => {
          return [
            item.toolName,
            {
              toolName: item.toolName,
              result: item.result,
            },
          ];
        })
        .fromPairs()
        .value();
    }

    if (task?.media_type === MediaType.IMAGE) {
      return convertImageAnnotations(_annotations, preAnnotationConfig);
    } else if (task?.media_type === MediaType.VIDEO || task?.media_type === MediaType.AUDIO) {
      return convertMediaAnnotations(task.media_type, _annotations, preAnnotationConfig);
    }

    return {};
  }, [preAnnotation, preAnnotationConfig, task?.media_type]);

  const [searchParams] = useSearchParams();
  const taskConfig = _.get(task, 'config');
  const isFetching = useIsFetching();
  const isMutating = useIsMutating();
  const me = useMe();
  const [currentSampleConns, taskConns] = useSampleWs();
  const isMeTheCurrentEditingUser = currentSampleConns?.[0]?.user_id === me.data?.id;

  // TODO： labelu/image中的错误定义
  const onError = useCallback(
    (err: any) => {
      const value = err.value;

      if (err.type === 'rotate') {
        message.error(t('cannotRotateWhenAnnotationExist'));
      }

      if (err.type === 'minPointAmount') {
        message.error(`${t('minPointAmountCannotSmallThan')} ${value}`);
      }

      if (err.type === 'maxPointAmount') {
        message.error(`${t('maxPointAmountCannotExceed')} ${value}`);
      }

      if (err.type === 'minWidth') {
        message.error(`${t('minWidthCannotSmallThan')}${value}`);
      }

      if (err.type === 'minHeight') {
        message.error(`${t('minHeightCannotSmallThan')} ${value}`);
      }
    },
    [t],
  );

  // 滚动加载
  const [totalCount, setTotalCount] = useState<number>(0);
  const currentPage = useRef<number>(1);
  const fetchSamples = useCallback(async () => {
    if (!routeParams.taskId) {
      return Promise.resolve([]);
    }

    const { data, meta_data } = await getSamples({
      task_id: +routeParams.taskId!,
      page: currentPage.current,
      size: 40,
    });

    currentPage.current += 1;
    setTotalCount(meta_data?.total ?? 0);

    return data;
  }, [routeParams.taskId]);
  const [samples = [] as SampleResponse[], loading, setSamples, svc] = useScrollFetch(
    fetchSamples,
    () =>
      document.querySelector('.labelu-image__sidebar div') ||
      document.querySelector('.labelu-audio__sidebar div') ||
      document.querySelector('.labelu-video__sidebar div'),
    {
      isEnd: () => totalCount === samples.length,
    },
  );

  const leftSiderContent = useMemo(() => <SlideLoader />, []);

  const topActionContent = (
    <AnnotationRightCorner totalSize={totalCount} fetchNext={svc} noSave={!!searchParams.get('noSave')} />
  );

  const annotationContextValue = useMemo(() => {
    return {
      samples,
      setSamples,
      taskConnections: taskConns,
      task,
      currentEditingUser: currentSampleConns[0],
      isEnd: totalCount === samples.length,
    };
  }, [currentSampleConns, taskConns, samples, setSamples, task, totalCount]);

  let content = null;

  const editorConfig = useMemo(() => {
    if (task?.media_type === MediaType.VIDEO || task?.media_type === MediaType.AUDIO) {
      return convertAudioAndVideoConfig(taskConfig);
    }

    return convertImageConfig(taskConfig);
  }, [task?.media_type, taskConfig]);

  const editingSample = useMemo(() => {
    if (task?.media_type === MediaType.IMAGE) {
      return convertImageSample(sample?.data, editorConfig);
    } else if (task?.media_type === MediaType.VIDEO || task?.media_type === MediaType.AUDIO) {
      return convertAudioAndVideoSample(sample?.data, editorConfig, task.media_type);
    }
  }, [editorConfig, sample?.data, task?.media_type]);

  const renderSidebar = useMemo(() => {
    return () => leftSiderContent;
  }, [leftSiderContent]);

  // =================== preview config ===================
  const [configFromParent, setConfigFromParent] = useState<any>();
  useLayoutEffect(() => {
    const bridge = new Bridge(window.parent);

    bridge.on('preview', (data) => {
      setConfigFromParent(data);
    });

    bridge.post('ready').catch(() => {});

    return () => bridge.destroy();
  }, []);

  const isLoading = useMemo(() => loading || isFetching > 0 || isMutating > 0, [loading, isFetching, isMutating]);

  const config = useMemo(() => {
    return configFromParent || editorConfig;
  }, [configFromParent, editorConfig]);

  useEffect(() => {
    if (me.data && currentSampleConns?.[0] && !isMeTheCurrentEditingUser) {
      message.destroy();
      message.error(t('currentSampleIsAnnotating'));
    }
  }, [currentSampleConns, isMeTheCurrentEditingUser, me.data, t]);

  const requestEdit = useCallback<NonNullable<ImageAnnotatorProps['requestEdit']>>(
    (editType, { toolName, label }) => {
      if (!toolName) {
        return false;
      }

      const toolConfig = config[toolName];
      const toolNameKey =
        (toolName.includes('frame') || toolName.includes('segment')
          ? task!.media_type?.toLowerCase() + _.upperFirst(toolName)
          : toolName) + 'Tool';

      if (editType === 'create' && !toolConfig?.labels?.find((item: ILabel) => item.value === label)) {
        message.destroy();
        message.error(`${t('currentTool')}【${TOOL_NAME[toolNameKey]}】${t('doesntInclude')}【${label}】`);

        return false;
      }

      if (editType === 'update' && !config[toolName]) {
        message.destroy();
        message.error(`${t('currentConfigDoesntInclude')}【${TOOL_NAME[toolNameKey]}】`);
        return false;
      }

      return true;
    },
    [config, task, t],
  );

  const [currentTool, setCurrentTool] = useState<any>();
  const [labelMapping, setLabelMapping] = useState<Record<any, string>>();

  const handleLabelChange = useCallback((toolName: any, label: ILabel) => {
    // 缓存当前标签
    setLabelMapping((prev) => {
      return {
        ...prev,
        [toolName]: label.value,
      };
    });
  }, []);

  const handleToolChange = useCallback((toolName: any) => {
    setCurrentTool(toolName);
  }, []);

  const currentLabel = useMemo(() => {
    return labelMapping?.[currentTool];
  }, [currentTool, labelMapping]);

  const disabled = useMemo(() => {
    return me.data && currentSampleConns[0] && !isMeTheCurrentEditingUser;
  }, [currentSampleConns, isMeTheCurrentEditingUser, me.data]);

  if (task?.media_type === MediaType.IMAGE) {
    content = (
      <ImageAnnotator
        renderSidebar={renderSidebar}
        toolbarRight={topActionContent}
        ref={imageAnnotationRef}
        onError={onError}
        offsetTop={configFromParent ? 100 : 156}
        editingSample={editingSample}
        config={config}
        disabled={disabled}
        requestEdit={requestEdit}
        onLabelChange={handleLabelChange}
        onToolChange={handleToolChange}
        selectedTool={disabled ? undefined : currentTool}
        selectedLabel={disabled ? undefined : currentLabel}
        preAnnotationLabels={preAnnotationConfig}
        preAnnotations={sample.data.state === SampleState.NEW ? preAnnotations : undefined}
      />
    );
  } else if (task?.media_type === MediaType.VIDEO) {
    content = (
      <Annotator
        primaryColor="#0d53de"
        ref={videoAnnotationRef}
        offsetTop={configFromParent ? 100 : 156}
        editingSample={editingSample}
        config={config}
        toolbarRight={topActionContent}
        renderSidebar={renderSidebar}
        disabled={disabled}
        requestEdit={requestEdit}
        onLabelChange={handleLabelChange}
        onToolChange={handleToolChange}
        selectedTool={disabled ? undefined : currentTool}
        selectedLabel={disabled ? undefined : currentLabel}
        preAnnotationLabels={preAnnotationConfig}
        preAnnotations={sample.data.state === SampleState.NEW ? preAnnotations : undefined}
      />
    );
  } else if (task?.media_type === MediaType.AUDIO) {
    content = (
      <AudioAnnotator
        primaryColor="#0d53de"
        ref={audioAnnotationRef}
        offsetTop={configFromParent ? 100 : 156}
        editingSample={editingSample}
        config={config}
        disabled={disabled}
        toolbarRight={topActionContent}
        renderSidebar={renderSidebar}
        requestEdit={requestEdit}
        onLabelChange={handleLabelChange}
        onToolChange={handleToolChange}
        selectedTool={disabled ? undefined : currentTool}
        selectedLabel={disabled ? undefined : currentLabel}
        preAnnotationLabels={preAnnotationConfig}
        preAnnotations={sample.data.state === SampleState.NEW ? preAnnotations : undefined}
      />
    );
  }

  if (_.isEmpty(sample.data.file)) {
    return (
      <FlexLayout.Content items="center" justify="center" flex>
        <Empty description={t('noSample')} />
      </FlexLayout.Content>
    );
  }

  if (_.isEmpty(taskConfig?.tools) && _.isEmpty(configFromParent)) {
    return (
      <FlexLayout.Content items="center" justify="center" flex>
        <Empty description={t('noTool')} />
      </FlexLayout.Content>
    );
  }

  return (
    <AnnotationContext.Provider value={annotationContextValue}>
      {isLoading && (
        <LoadingWrapper items="center" justify="center" flex>
          <Spin spinning />
        </LoadingWrapper>
      )}
      <Wrapper flex="column" full loading={isLoading}>
        {content}
      </Wrapper>
    </AnnotationContext.Provider>
  );
};

export default AnnotationPage;
