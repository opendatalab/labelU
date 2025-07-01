import _ from 'lodash';
import type { GlobalToolConfig, ImageAnnotatorOptions, ImageSample } from '@labelu/image-annotator-react';
import { omit } from 'lodash/fp';
import type { ToolName } from '@labelu/image';
import { TOOL_NAMES } from '@labelu/image';

import { SampleState, type ParsedResult, type SampleResponse } from '@/api/types';

import { jsonParse } from './index';
import { generateDefaultValues } from './generateGlobalToolDefaultValues';

export function convertImageAnnotations(
  result: ParsedResult,
  config: Pick<ImageAnnotatorOptions, ToolName> & GlobalToolConfig,
  state?: SampleState,
) {
  // annotation
  const pool = [
    ['line', 'lineTool'],
    ['point', 'pointTool'],
    ['rect', 'rectTool'],
    ['polygon', 'polygonTool'],
    ['cuboid', 'cuboidTool'],
    ['text', 'textTool'],
    ['tag', 'tagTool'],
  ] as const;

  return _.chain(pool)
    .map(([type, key]) => {
      if (!result[key] && TOOL_NAMES.includes(type as ToolName)) {
        return;
      }

      const items = _.get(result, [key, 'result']) || _.get(result, [type, 'result'], []);
      if (!items.length && (type === 'tag' || type === 'text') && state !== SampleState.NEW) {
        // 生成全局工具的默认值
        return [type, generateDefaultValues(config?.[type])];
      }

      return [
        type,
        items.map((item: any) => {
          const resultItem = {
            ...omit(['attribute'])(item),
            label: item.attribute ?? item.label,
          } as any;

          if (type === 'line' || type === 'polygon') {
            return {
              ...omit(['pointList'])(resultItem),
              type: resultItem.type ?? 'line',
              points: item.pointList ?? item.points,
            };
          }

          return resultItem;
        }),
      ];
    })
    .compact()
    .fromPairs()
    .value();
}

export function convertImageSample(
  sample: SampleResponse | undefined,
  config: Pick<ImageAnnotatorOptions, ToolName> & GlobalToolConfig,
): ImageSample | undefined {
  if (!sample) {
    return;
  }

  const id = sample.id!;
  const url = sample.file.url;

  let resultParsed: any = {};
  if (sample?.data?.result && !_.isNull(sample?.data?.result)) {
    resultParsed = jsonParse(sample.data.result);
  }

  return {
    id,
    url,
    data: convertImageAnnotations(resultParsed, config, sample.state),
    meta: _.pick(resultParsed, ['width', 'height', 'rotate']),
  };
}
