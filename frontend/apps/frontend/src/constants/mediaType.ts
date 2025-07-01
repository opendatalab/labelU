import { i18n } from '@labelu/i18n';

import { MediaType } from '@/api/types';

export const MediaTypeText = {
  [MediaType.IMAGE]: i18n.t('image'),
  [MediaType.VIDEO]: i18n.t('video'),
  [MediaType.AUDIO]: i18n.t('audio'),
};

export const FileExtensionText = {
  [MediaType.IMAGE]: 'jpg、jpeg、png、bmp、gif',
  [MediaType.VIDEO]: 'mp4(h.264)',
  [MediaType.AUDIO]: 'mp3、wav、ogg、m4a',
};

export const FileExtension = {
  [MediaType.IMAGE]: ['jpg', 'png', 'bmp', 'gif', 'jpeg'],
  [MediaType.VIDEO]: ['mp4'],
  [MediaType.AUDIO]: ['mp3', 'wav', 'ogg', 'm4a'],
};

export const MediaRouterPrefix = {
  [MediaType.IMAGE]: 'image',
  [MediaType.VIDEO]: 'video',
  [MediaType.AUDIO]: 'audio',
};

export const FileMimeType = {
  [MediaType.IMAGE]: 'image/png,image/jpeg,image/bmp,image/gif',
  [MediaType.VIDEO]: 'video/mp4',
  [MediaType.AUDIO]: 'audio/mpeg,audio/x-wav,audio/vnd.wav,audio/ogg,audio/x-m4a',
};
