/**
 * 此组件可用于react-router>=6.4.0的特性，比如loader等Data API
 * 见：https://reactrouter.com/en/main/routers/picking-a-router
 */
import React, { useEffect, useMemo } from 'react';
import type { RouteObject, UIMatch } from 'react-router-dom';
import { createHashRouter, createHashRouter, createRoutesFromElements, Route, RouterProvider, useMatches } from 'react-router-dom';

export type RouteWithParent = RouteObject & {
  parent: RouteWithParent | null;
};

export type Match = UIMatch<any, {crumb: (data: any) => string}>

// 将对应的面包屑信息添加到页面标题中
function RouteWithTitle({ children }: { children: React.ReactNode }) {
  const matches = useMatches() as Match[];
  const titles = useMemo(() => matches.filter((match) => Boolean(match.handle?.crumb))
    .map((match) => match.handle.crumb!(match.data)), [matches]);

  const title = titles.length > 0 ? titles[titles.length - 1] : null;

  useEffect(() => {
    document.title = title || 'LabelU';
  }, [title]);

  return <>{children}</>;
}

function mapRoutes(
  inputRoutes: RouteObject[],
  parentPath: string = '',
  parentRoute: RouteWithParent | null = null,
): React.ReactNode {
  return inputRoutes.map((route) => {
    const { path, element, children, index, ...restProps } = route;
    const routeWithParent: RouteWithParent = { ...route, parent: parentRoute };
    const comp = <RouteWithTitle key={`${parentPath}-${path}`}>{element}</RouteWithTitle>;

    if (index) {
      return (
        // @ts-ignore
        <Route
          index={Boolean(index)}
          key={`${parentPath}-${path}`}
          path={undefined}
          element={comp as React.ReactElement}
          {...restProps}
        />
      );
    }

    return (
      // @ts-ignore
      <Route key={`${parentPath}-${path}`} path={path} element={comp as React.ReactElement} {...restProps}>
        {Array.isArray(children) ? mapRoutes(children, path, routeWithParent) : null}
      </Route>
    );
  });
}

export interface RouterProps {
  routes: RouteObject[];
  basename?: string;
}

export default function RouterContainer({ routes, basename }: RouterProps) {
  const router = useMemo(
    () =>
      createHashRouter(createRoutesFromElements(mapRoutes(routes)), {
        basename,
      }),
    [basename, routes],
  );
  const fallback = <div style={{ width: '100vw', marginTop: '40vh' }}> loading </div>;

  return <RouterProvider router={router} fallbackElement={fallback} />;
}
