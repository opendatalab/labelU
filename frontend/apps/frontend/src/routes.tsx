import type { RouteObject } from 'react-router';
import { Outlet, useLocation, useNavigate } from 'react-router';
import { useEffect } from 'react';
import { i18n } from '@labelu/i18n';

import Register from '@/pages/register';
import Tasks from '@/pages/tasks';
import TaskEdit from '@/pages/tasks.[id].edit';
import TaskAnnotation from '@/pages/tasks.[id].samples.[id]';
import Samples from '@/pages/tasks.[id]';
import TaskSamplesFinished from '@/pages/tasks.[id].samples.finished';
import Page404 from '@/pages/404';
import MainLayout from '@/layouts/MainLayoutWithNavigation';

import type { TaskLoaderResult } from './loaders/task.loader';
import { taskLoader, tasksLoader } from './loaders/task.loader';
import { rootLoader } from './loaders/root.loader';
import { sampleLoader } from './loaders/sample.loader';
import RequireAuth from './components/RequireSSO';
import { registerLoader } from './loaders/register.loader';
import { loginLoader } from './loaders/login.loader';
import LoginPage from './pages/login';

function Root() {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // 如果是根路径，跳转到任务管理（以任务管理为首页）
    if (location.pathname === '/' || location.pathname === '') {
      navigate('/tasks');
    }
  }, [location.pathname, navigate]);

  if (!window.IS_ONLINE) {
    return <Outlet />;
  }

  return (
    <RequireAuth>
      <Outlet />
    </RequireAuth>
  );
}

const routes: RouteObject[] = [
  {
    path: '/',
    id: 'root',
    element: <Root />,
    loader: rootLoader,
    children: [
      {
        path: 'tasks',
        element: <MainLayout />,
        errorElement: <Page404 />,
        id: 'tasks',
        loader: tasksLoader,
        handle: {
          crumb: () => {
            return i18n.t('taskList');
          },
        },
        children: [
          {
            index: true,
            element: <Tasks />,
          },
          {
            path: ':taskId',
            id: 'task',
            element: <Outlet />,
            loader: taskLoader,
            handle: {
              crumb: (data: TaskLoaderResult) => {
                return data?.task?.name;
              },
            },
            children: [
              {
                index: true,
                element: <Samples />,
              },
              {
                path: 'edit',
                element: <TaskEdit />,
                loader: async ({ params }) => {
                  return params.taskId !== '0' ? i18n.t('taskEdit') : i18n.t('createTask');
                },
                handle: {
                  crumb: (data: string) => {
                    return data;
                  },
                },
              },
              {
                path: 'samples',
                id: 'samples',
                element: <Outlet />,
                children: [
                  {
                    path: ':sampleId',
                    element: <TaskAnnotation />,
                    loader: sampleLoader,
                    id: 'annotation',
                    handle: {
                      crumb: () => {
                        return i18n.t('start');
                      },
                    },
                  },
                  {
                    path: 'finished',
                    element: <TaskSamplesFinished />,
                    loader: taskLoader,
                    handle: {
                      crumb: () => {
                        return i18n.t('finished');
                      },
                    },
                  },
                ],
              },
            ],
          },
        ],
      },
    ],
  },
  {
    path: 'login',
    loader: loginLoader,
    element: <LoginPage />,
  },
  {
    path: 'register',
    loader: registerLoader,
    element: <Register />,
    handle: {
      crumb: () => {
        return i18n.t('signUp');
      },
    },
  },
  {
    path: '*',
    element: <Page404 />,
  },
];

export default routes;
