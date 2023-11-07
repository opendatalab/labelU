import { Outlet, type NonIndexRouteObject } from 'react-router';
import { MDXProvider } from '@mdx-js/react';

import Layout from './layouts/main';
import NoMatch from './pages/no-match';
import AudioGuide from './pages/guide.audio';
import VideoGuide from './pages/guide.video';

export interface RouteWithName extends NonIndexRouteObject {
  name?: string;
}

const routes = [
  {
    path: '/',
    id: 'root',
    element: <Layout />,
    name: '使用指南',
    children: [
      {
        path: 'guide',
        element: (
          <MDXProvider>
            <Outlet />
          </MDXProvider>
        ),
        id: 'guide',
        handle: {
          crumb: () => {
            return 'Guide';
          },
        },
        children: [
          {
            name: '开始',
            index: true,
            element: <div>概览介绍</div>,
          },
          {
            name: '安装',
            path: 'installation',
            element: <Outlet />,
            children: [
              {
                path: 'windows',
                name: 'Windows',
                element: <div>Windows</div>,
              },
              {
                name: 'MacOS',
                path: 'macos',
                element: <div>MacOS</div>,
              },
              {
                name: 'Linux',
                path: 'linux',
                element: <div>Linux</div>,
              },
            ],
          },
          {
            name: '图片',
            path: 'image',
            element: <Outlet />,
            children: [
              {
                name: '概览',
                index: true,
                element: <div>标点</div>,
              },
              {
                name: '标点',
                path: 'point',
                element: <div>标点</div>,
              },
              {
                name: '标线',
                path: 'line',
                element: <div>标线</div>,
              },
              {
                name: '拉框',
                path: 'rect',
                element: <div>拉框</div>,
              },
              {
                name: '多边形',
                path: 'polygon',
                element: <div>多边形</div>,
              },
            ],
          },
          {
            name: '音频',
            path: 'audio',
            element: <AudioGuide />,
            children: [
              {
                name: '概览',
                index: true,
                element: <div>音频概览</div>,
              },
              {
                name: '片断截取',
                path: 'segment',
                element: <div>片断截取</div>,
              },
              {
                name: '时间戳',
                path: 'frame',
                element: <div>片断截取</div>,
              },
            ],
          },
          {
            name: '视频',
            path: 'video',
            element: <VideoGuide />,
            children: [
              {
                name: '概览',
                index: true,
                element: <div>视频概览</div>,
              },
              {
                name: '片断截取',
                path: 'segment',
                element: <div>片断截取</div>,
              },
              {
                name: '时间戳',
                path: 'frame',
                element: <div>片断截取</div>,
              },
            ],
          },
        ],
      },
      {
        name: '标注结果格式',
        path: 'schema',
        element: (
          <MDXProvider>
            <Outlet />
          </MDXProvider>
        ),
        children: [
          {
            name: '图片',
            path: 'image',
            element: <Outlet />,
            children: [
              {
                name: '标点',
                path: 'point',
                element: <div>标点</div>,
              },
              {
                name: '标线',
                path: 'line',
                element: <div>标线</div>,
              },
              {
                name: '拉框',
                path: 'rect',
                element: <div>拉框</div>,
              },
              {
                name: '多边形',
                path: 'polygon',
                element: <div>多边形</div>,
              },
            ],
          },
          {
            name: '音频',
            path: 'audio',
            element: <AudioGuide />,
            children: [
              {
                name: '片断截取',
                path: 'segment',
                element: <div>片断截取</div>,
              },
              {
                name: '时间戳',
                path: 'frame',
                element: <div>片断截取</div>,
              },
            ],
          },
          {
            name: '视频',
            path: 'video',
            element: <VideoGuide />,
            children: [
              {
                name: '片断截取',
                path: 'segment',
                element: <div>片断截取</div>,
              },
              {
                name: '时间戳',
                path: 'frame',
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
