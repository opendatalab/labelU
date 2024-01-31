import { Outlet, type NonIndexRouteObject, redirect } from 'react-router';
import { MDXProvider } from '@mdx-js/react';

import Layout from './layouts/main';
import NoMatch from './pages/no-match';
import VideoSegmentSchema from './pages/schema.video.segment';
import VideoFrameSchema from './pages/schema.video.frame';
import i18n from './locale';

import Install from './pages/guide.install';
import Introduction from './pages/guide.introduction';
import Account from './pages/guide.account';
import BasicConfig from './pages/guide.task-create.basic';
import DataImport from './pages/guide.task-create.data-import';
import AnnotationConfig from './pages/guide.task-create.annotation-config';
import AnnotationImage from './pages/guide.task-annotation.image';
import AnnotationVideo from './pages/guide.task-annotation.video';
import AnnotationAudio from './pages/guide.task-annotation.audio';
import TaskCheck from './pages/guide.task-check';
import ResultExport from './pages/guide.export';
import Schema from './pages/schema';
import RectSchema from './pages/schema.image.rect';
import PointSchema from './pages/schema.image.point';
import LineSchema from './pages/schema.image.line';
import PolygonSchema from './pages/schema.image.polygon';
import CuboidSchema from './pages/schema.image.cuboid';
import AudioSegmentSchema from './pages/schema.audio.segment';
import AudioFrameSchema from './pages/schema.audio.frame';
import Playground from './pages/playground';
import JustNavigation from './layouts/just-navigation';

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
            path: 'introduction',
            element: <Introduction />,
            handle: {
              crumb: () => {
                return i18n.t('guide.intro');
              },
            },
          },
          {
            name: '安装',
            path: 'install',
            element: <Install />,
            handle: {
              crumb: () => {
                return i18n.t('install');
              },
            },
          },
          {
            path: 'account',
            element: <Account />,
            handle: {
              crumb: () => {
                return i18n.t('guide.account');
              },
            },
          },
          {
            path: 'task-create',
            element: <Outlet />,
            handle: {
              crumb: () => {
                return i18n.t('guide.task-create');
              },
            },
            children: [{
              path: 'basic',
              element: <BasicConfig />,
              handle: {
                crumb: () => {
                  return i18n.t('guide.task-create.basic');
                },
              },
            }, {
              path: 'data-import',
              element: <DataImport />,
              handle: {
                crumb: () => {
                  return i18n.t('guide.task-create.data-import');
                },
              },
            }, {
              path: 'annotation-config',
              element: <AnnotationConfig />,
              handle: {
                crumb: () => {
                  return i18n.t('guide.task-create.annotation-config');
                },
              },
            }]
          },
          {
            path: 'task-annotation',
            element: <Outlet />,
            handle: {
              crumb: () => {
                return i18n.t('guide.task-annotation');
              },
            },
            children: [{
              path: 'image',
              element: <AnnotationImage />,
              handle: {
                crumb: () => {
                  return i18n.t('guide.task-annotation.image');
                },
              },
            }, {
              path: 'video',
              element: <AnnotationVideo />,
              handle: {
                crumb: () => {
                  return i18n.t('guide.task-annotation.video');
                },
              },
            }, {
              path: 'audio',
              element: <AnnotationAudio />,
              handle: {
                crumb: () => {
                  return i18n.t('guide.task-annotation.audio');
                },
              },
            }]
          },
          {
            path: 'task-check',
            element: <TaskCheck />,
            handle: {
              crumb: () => {
                return i18n.t('guide.task-check');
              },
            },
          },
          {
            path: 'export',
            element: <ResultExport />,
            handle: {
              crumb: () => {
                return i18n.t('guide.export');
              },
            },
          }
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
                element: <PointSchema />,
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
                element: <PolygonSchema />,
                handle: {
                  crumb: () => {
                    return i18n.t('image.polygon');
                  },
                },
              },
              {
                path: 'cuboid',
                element: <CuboidSchema />,
                handle: {
                  crumb: () => {
                    return i18n.t('image.cuboid');
                  },
                },
              },
            ],
          },
          {
            path: 'audio',
            element: <Outlet />,
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
                element: <AudioSegmentSchema />,
              },
              {
                path: 'frame',
                handle: {
                  crumb: () => {
                    return i18n.t('audio.frame');
                  },
                },
                element: <AudioFrameSchema />,
              },
            ],
          },
          {
            path: 'video',
            element: <Outlet />,
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
                element: <VideoSegmentSchema />,
              },
              {
                path: 'frame',
                handle: {
                  crumb: () => {
                    return i18n.t('video.frame');
                  },
                },
                element: <VideoFrameSchema />,
              },
            ],
          },
        ],
      },
    ],
  },
  {
    path: '/playground',
    element: <JustNavigation><Playground /></JustNavigation>,
    handle: {
      crumb: () => {
        return i18n.t('playground');
      },
    },
  },
  {
    path: '*',
    element: <NoMatch />,
  },
] as RouteWithName[];

export default routes;
