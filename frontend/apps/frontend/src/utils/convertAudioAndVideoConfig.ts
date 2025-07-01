import type { MediaAnnotatorConfig } from '@labelu/audio-annotator-react';

import type { ToolsConfigState } from '@/types/toolConfig';

export function convertAudioAndVideoConfig(taskConfig?: ToolsConfigState) {
  const editorConfig: MediaAnnotatorConfig = {} as MediaAnnotatorConfig;

  taskConfig?.tools?.forEach((item) => {
    if (['videoSegmentTool', 'audioSegmentTool'].includes(item.tool)) {
      editorConfig.segment = [...(editorConfig.segment ?? []), ...(item.config.attributes ?? [])];

      if (taskConfig.attributes) {
        editorConfig.segment = [...editorConfig.segment, ...taskConfig.attributes];
      }
    }

    if (['videoFrameTool', 'audioFrameTool'].includes(item.tool)) {
      editorConfig.frame = [...(editorConfig.frame ?? []), ...(item.config.attributes ?? [])];

      if (taskConfig.attributes) {
        editorConfig.frame = [...editorConfig.frame, ...taskConfig.attributes];
      }
    }

    if (item.tool === 'tagTool') {
      editorConfig.tag = item.config.attributes;
    }

    if (item.tool === 'textTool') {
      editorConfig.text = item.config.attributes;
    }
  });

  return editorConfig;
}
