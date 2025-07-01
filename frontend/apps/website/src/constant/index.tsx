import { i18n } from '@labelu/i18n';

import { ReactComponent as VideoIcon } from '@/assets/video.svg';
import { ReactComponent as AudioIcon } from '@/assets/audio.svg';
import { ReactComponent as ImageIcon } from '@/assets/image.svg';

export const MENU = [
  {
    name: i18n.t('image'),
    path: '/image',
    icon: <ImageIcon className="text-lg" />,
  },
  {
    name: i18n.t('audio'),
    path: '/audio',
    icon: <AudioIcon className="text-lg" />,
  },
  {
    name: i18n.t('video'),
    path: '/video',
    icon: <VideoIcon className="text-lg" />,
  },
];
