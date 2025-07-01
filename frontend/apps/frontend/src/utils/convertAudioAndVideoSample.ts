import _ from 'lodash';
import type { AnnotationsWithGlobal, MediaAnnotatorConfig, MediaSample } from '@labelu/audio-annotator-react';

import type { ParsedResult, SampleResponse } from '@/api/types';
import { MediaType, SampleState } from '@/api/types';

import { jsonParse } from './index';
import { generateDefaultValues } from './generateGlobalToolDefaultValues';

export function convertMediaAnnotations(
  mediaType: MediaType,
  result: ParsedResult,
  config: MediaAnnotatorConfig,
  state?: SampleState,
) {
  // annotation
  const pool = [
    ['segment', MediaType.VIDEO === mediaType ? 'videoSegmentTool' : 'audioSegmentTool'],
    ['frame', MediaType.VIDEO === mediaType ? 'videoFrameTool' : 'audioFrameTool'],
    ['text', 'textTool'],
    ['tag', 'tagTool'],
  ] as const;

  return _.chain(pool)
    .map(([type, key]) => {
      const items = _.get(result, [key, 'result'], []);

      if (!items.length && (type === 'tag' || type === 'text') && state !== SampleState.NEW) {
        // 生成全局工具的默认值
        return [type, generateDefaultValues(config?.[type])];
      }

      return [
        type,
        _.map(items, (item) => {
          return {
            ...item,
            type,
          };
        }),
      ];
    })
    .fromPairs()
    .value() as AnnotationsWithGlobal;
}

export function convertAudioAndVideoSample(
  sample: SampleResponse,
  config: MediaAnnotatorConfig,
  mediaType?: MediaType,
): MediaSample | undefined {
  if (!sample) {
    return;
  }

  const id = sample.id!;

  let resultParsed: any = {};
  if (sample?.data?.result && !_.isNull(sample?.data?.result)) {
    resultParsed = jsonParse(sample.data.result);
  }

  return {
    id,
    url: [MediaType.VIDEO, MediaType.AUDIO].includes(mediaType as MediaType)
      ? sample.file.url.replace('attachment', 'partial')
      : sample.file.url,
    data: convertMediaAnnotations(mediaType!, resultParsed, config, sample.state),
  };
}
