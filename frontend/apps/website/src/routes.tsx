import loadable from '@loadable/component';
import Spin from 'antd/es/spin';

import AudioPage from './pages/audio';
import ImagePage from './pages/image';
import VideoPage from './pages/video';
import CheckChildRoute from './wrappers/CheckChildRoute';

const moduleSpin = {
  fallback: <Spin className="w-full mt-[30vh]" />,
};

const Home = loadable(() => import('./pages/home'), moduleSpin);

export default [
  {
    path: '/',
    element: (
      <CheckChildRoute>
        <Home />
      </CheckChildRoute>
    ),
    // 此ID可以用于在路由中获取loader中的数据
    id: 'root',
    handle: {
      crumb: () => {
        return 'LabelU Kit';
      },
    },
    children: [
      {
        path: 'image',
        element: <ImagePage />,
        handle: {
          crumb: () => {
            return 'Image Annotating';
          },
        },
      },
      {
        path: 'audio',
        element: <AudioPage />,
        handle: {
          crumb: () => {
            return 'Audio Annotating';
          },
        },
      },
      {
        path: 'video',
        element: <VideoPage />,
        handle: {
          crumb: () => {
            return 'Video Annotating';
          },
        },
      },
    ],
  },
  {
    path: '*',
    element: (
      <div>
        <h1>404</h1>
      </div>
    ),
  },
];
