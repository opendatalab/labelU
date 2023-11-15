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
          <summary className="pl-6 rounded">{title}</summary>
          {children}
        </details>
      </li>
    );
  }

  return (
    <li>
      <Link
        className={clsx('pl-6 rounded active:bg-[#F7F7F7]', {
          'bg-[#F7F7F7] text-[var(--color-primary)]': match,
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
        {menu.map(({ handle, path: routePath, index }) => (
          <MenuItem
            key={`${index ? top : `${top}/${routePath}`}`}
            path={`${index ? top : `${top}/${routePath}`}`}
            title={handle ? handle.crumb() : 'unknown'}
          />
        ))}
      </ul>
    );
  }

  return (
    <ul className="menu flex-nowrap text-base h-full">
      {menu.map(({ handle, children, path: routePath, index }) => {
        const topPath = index ? path : `${path}/${routePath}`;
        const title = handle?.crumb() ?? 'unknown';

        if (children) {
          return (
            <MenuItem key={routePath} path={routePath!} title={title}>
              <Menu path={routePath!} top={topPath} routes={menu} />
            </MenuItem>
          );
        }

        return <MenuItem key={topPath} path={topPath} title={title} />;
      })}
    </ul>
  );
}
