import { Outlet, type NonIndexRouteObject } from 'react-router';
import { MDXProvider } from '@mdx-js/react';

import Layout from './layouts/main';
import NoMatch from './pages/no-match';
import AudioGuide from './pages/guide.audio';
import VideoGuide from './pages/guide.video';
import i18n from './locale';
import GettingStarted from './pages/getting-started';
import Schema from './pages/schema';
import RectSchema from './pages/schema.image.rect';
import LineSchema from './pages/schema.image.line';

export interface RouteWithName extends NonIndexRouteObject {
  name?: string;
}

const routes = [
  {
    path: '/',
    id: 'root',
    element: <Layout />,
    children: [
      {
        path: 'guide',
        element: (
          <MDXProvider>
            <Outlet />
          </MDXProvider>
        ),
        handle: {
          crumb: () => {
            return i18n.t('guide');
          },
        },
        children: [
          {
            name: '开始',
            index: true,
            element: <GettingStarted />,
            handle: {
              crumb: () => {
                return i18n.t('getting started');
              },
            },
          },
          {
            name: '安装',
            path: 'install',
            element: <Outlet />,
            handle: {
              crumb: () => {
                return i18n.t('install');
              },
            },
            children: [
              {
                path: 'windows',
                name: 'Windows',
                handle: {
                  crumb: () => {
                    return i18n.t('windows');
                  },
                },
                element: <div>Windows</div>,
              },
              {
                name: 'MacOS',
                path: 'macos',
                handle: {
                  crumb: () => {
                    return i18n.t('macos');
                  },
                },
                element: <div>MacOS</div>,
              },
              {
                name: 'Linux',
                path: 'linux',
                handle: {
                  crumb: () => {
                    return i18n.t('linux');
                  },
                },
                element: <div>Linux</div>,
              },
            ],
          },
        ],
      },
      {
        path: 'schema',
        handle: {
          crumb: () => {
            return i18n.t('schema');
          },
        },
        element: (
          <MDXProvider>
            <Schema />
          </MDXProvider>
        ),
        children: [
          {
            path: 'image',
            element: <Outlet />,
            handle: {
              crumb: () => {
                return i18n.t('image');
              },
            },
            children: [
              {
                path: 'point',
                element: <Outlet />,
                handle: {
                  crumb: () => {
                    return i18n.t('image.point');
                  },
                },
              },
              {
                path: 'line',
                element: <LineSchema />,
                handle: {
                  crumb: () => {
                    return i18n.t('image.line');
                  },
                },
              },
              {
                path: 'rect',
                element: <RectSchema />,
                handle: {
                  crumb: () => {
                    return i18n.t('image.rect');
                  },
                },
              },
              {
                path: 'polygon',
                element: <div>多边形</div>,
                handle: {
                  crumb: () => {
                    return i18n.t('image.polygon');
                  },
                },
              },
            ],
          },
          {
            path: 'audio',
            element: <AudioGuide />,
            handle: {
              crumb: () => {
                return i18n.t('audio');
              },
            },
            children: [
              {
                path: 'segment',
                handle: {
                  crumb: () => {
                    return i18n.t('audio.segment');
                  },
                },
                element: <div>片断截取</div>,
              },
              {
                path: 'frame',
                handle: {
                  crumb: () => {
                    return i18n.t('audio.frame');
                  },
                },
                element: <div>片断截取</div>,
              },
            ],
          },
          {
            path: 'video',
            element: <VideoGuide />,
            handle: {
              crumb: () => {
                return i18n.t('video');
              },
            },
            children: [
              {
                path: 'segment',
                handle: {
                  crumb: () => {
                    return i18n.t('video.segment');
                  },
                },
                element: <div>片断截取</div>,
              },
              {
                path: 'frame',
                handle: {
                  crumb: () => {
                    return i18n.t('video.frame');
                  },
                },
                element: <div>片断截取</div>,
              },
            ],
          },
        ],
      },
    ],
  },

  {
    path: '*',
    element: <NoMatch />,
  },
] as RouteWithName[];

export default routes;
