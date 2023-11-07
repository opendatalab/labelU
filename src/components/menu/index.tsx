import clsx from 'clsx';
import { useMemo } from 'react';
import { Link, useMatch } from 'react-router-dom';

import allRoutes from '@/routes';
import type { RouteWithName } from '@/routes';

export function MenuItem({
  title = '',
  children,
  path,
}: React.PropsWithChildren<{
  path: string;
  title?: string;
}>) {
  const match = useMatch(path);

  if (children) {
    return (
      <li>
        <details open>
          <summary className="rounded-full pl-6">{title}</summary>
          {children}
        </details>
      </li>
    );
  }

  return (
    <li>
      <Link
        className={clsx('rounded-full pl-6', {
          'bg-base-200': match,
        })}
        to={path}
      >
        {title}
      </Link>
    </li>
  );
}

export function Menu({ path, top, routes = allRoutes }: { path: string; top?: string; routes?: typeof allRoutes }) {
  const menu = useMemo(() => {
    let route;
    let submenu = routes ?? [];

    if (!path) {
      return [];
    }

    for (const item of path.split('/')) {
      const _path = item === '' ? '/' : item;

      route = submenu.find((_route) => _route.path === _path);
      submenu = (route?.children as RouteWithName[]) ?? [];
    }

    return submenu;
  }, [path, routes]);

  // 子菜单
  if (top) {
    return (
      <ul>
        {menu.map(({ name, path: routePath, index }) => (
          <MenuItem
            key={`${index ? top : `${top}/${routePath}`}`}
            path={`${index ? top : `${top}/${routePath}`}`}
            title={name}
          />
        ))}
      </ul>
    );
  }

  return (
    <ul className="menu flex-nowrap text-base h-full rounded-r-lg">
      {menu.map(({ name, children, path: routePath, index }) => {
        const topPath = index ? path : `${path}/${routePath}`;

        if (children) {
          return (
            <MenuItem key={routePath} path={routePath!} title={name}>
              <Menu path={routePath!} top={topPath} routes={menu} />
            </MenuItem>
          );
        }

        return <MenuItem key={topPath} path={topPath} title={name} />;
      })}
    </ul>
  );
}
