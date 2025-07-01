import React, { useContext, useMemo } from 'react';
import styled from 'styled-components';

import type { SampleResponse } from '@/api/types';
import type { TaskInLoader } from '@/loaders/task.loader';
import type { TaskCollaboratorInWs } from '@/hooks/useTaskWs';

import SliderCard from '../sliderCard';
import { SAMPLE_CHANGED } from '../annotationRightCorner';
import AnnotationContext from '../../annotation.context';

const LeftWrapper = styled.div`
  overflow-y: auto;
  overflow-x: hidden;
  height: calc(100vh - var(--offset-top));
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-sizing: border-box;
  padding: 1rem 0;
  align-items: center;
`;

const SlideLoader = () => {
  const handleSampleClick = (sample: SampleResponse) => {
    document.dispatchEvent(
      new CustomEvent(SAMPLE_CHANGED, {
        detail: {
          sampleId: sample.id,
        },
      }),
    );
  };

  /**
   * 切换文件时
   * 1. 下一张或者上一张时，需要将当前的标注结果更新到当前文件后，再进行切换
   *    1.1 如果当前文件是「跳过」的状态，那么不需要更新标注结果
   *    1.2 如果当前文件是「完成」的状态，那么需要更新标注结果，并且将当前文件的状态改为「完成」
   * 2. 将当前文件标记为「跳过」，更新文件状态为「跳过」，然后跳到下一张
   * 3. 将当前文件标记为「取消跳过」，更新文件状态为「新」
   */
  // context中的samples会随着「跳过」、「取消跳过」、「完成」的操作而更新，但上面的useScrollFetch只有滚动的时候才会触发更新
  const {
    samples: samplesFromContext,
    task = {} as NonNullable<TaskInLoader>,
    taskConnections,
  } = useContext(AnnotationContext);
  const userSampleMapping = useMemo(() => {
    const mapping: Record<string, TaskCollaboratorInWs[]> = {};
    taskConnections.forEach((collaborator) => {
      if (!mapping[collaborator.sample_id]) {
        mapping[collaborator.sample_id] = [];
      }

      mapping[collaborator.sample_id].push(collaborator);
    });

    return mapping;
  }, [taskConnections]);

  return (
    <LeftWrapper>
      {samplesFromContext?.map((item: SampleResponse, index) => {
        return (
          <SliderCard
            editingUser={userSampleMapping?.[item.id!]?.[0]}
            cardInfo={item}
            type={task.media_type}
            key={item.id}
            onClick={handleSampleClick}
            index={index}
          />
        );
      })}
    </LeftWrapper>
  );
};

export default SlideLoader;
