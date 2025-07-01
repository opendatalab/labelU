import type { ImageAnnotatorProps } from '@labelu/image-annotator-react';
import type { ToolName } from '@labelu/image';
import { TOOL_NAMES } from '@labelu/image';

import type { ToolsConfigState } from '@/types/toolConfig';

export function convertImageConfig(taskConfig?: ToolsConfigState) {
  const editorConfig: NonNullable<ImageAnnotatorProps['config']> = {
    showOrder: true,
  } as NonNullable<ImageAnnotatorProps['config']>;
  const commonLabels = taskConfig?.attributes ?? [];

  taskConfig?.tools?.forEach((item) => {
    const toolName = item.tool.replace(/Tool$/, '') as ToolName | 'tag' | 'text';

    if (TOOL_NAMES.includes(toolName as ToolName)) {
      if (!editorConfig[toolName]) {
        editorConfig[toolName] = {} as any;
      }

      // @ts-ignore
      editorConfig[toolName] = {
        labels: [...commonLabels, ...(item.config.attributes ?? [])],
        // @ts-ignore
        outOfImage: Boolean(taskConfig.drawOutsideTarget),
      };

      if (toolName === 'line') {
        editorConfig.line!.edgeAdsorptive = Boolean(item.config.edgeAdsorption);
        editorConfig.line!.lineType = item.config.lineType === 0 ? 'line' : 'spline';
        editorConfig.line!.minPointAmount = item.config.lowerLimitPointNum;
        editorConfig.line!.maxPointAmount = item.config.upperLimitPointNum;
      }

      if (toolName === 'point') {
        editorConfig.point!.maxPointAmount = item.config.upperLimit;
      }

      if (toolName === 'rect') {
        editorConfig.rect!.minWidth = item.config.minWidth;
        editorConfig.rect!.minHeight = item.config.minHeight;
      }

      if (toolName === 'polygon') {
        editorConfig.polygon!.edgeAdsorptive = Boolean(item.config.edgeAdsorption);
        editorConfig.polygon!.lineType = item.config.lineType === 0 ? 'line' : 'spline';

        editorConfig.polygon!.minPointAmount = item.config.lowerLimitPointNum;
        editorConfig.polygon!.maxPointAmount = item.config.upperLimitPointNum;
      }
    }

    if (toolName === 'tag') {
      editorConfig.tag = item.config.attributes;
    }

    if (toolName === 'text') {
      editorConfig.text = item.config.attributes;
    }
  });

  return editorConfig;
}
