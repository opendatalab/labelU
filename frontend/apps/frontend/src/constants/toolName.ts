import { i18n } from '@labelu/i18n'

import { EAudioToolName, EGlobalToolName, EVideoToolName, ImageToolName } from '@/enums';

export const TOOL_NAME: Record<string, string> = {
  [ImageToolName.Rect]: i18n.t('rect'),
  [EGlobalToolName.Tag]: i18n.t('tag'),
  [EGlobalToolName.Text]: i18n.t('textDescription'),
  [ImageToolName.Point]: i18n.t('point'),
  [ImageToolName.Polygon]: i18n.t('polygon'),
  [ImageToolName.Cuboid]: i18n.t('cuboid'),
  [ImageToolName.Line]: i18n.t('line'),
  [EVideoToolName.VideoSegmentTool]: i18n.t("segment"),
  [EVideoToolName.VideoFrameTool]: i18n.t("timestamp"),
  [EAudioToolName.AudioSegmentTool]: i18n.t("segment"),
  [EAudioToolName.AudioFrameTool]: i18n.t("timestamp"),
};
