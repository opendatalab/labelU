import { useRouteLoaderData } from 'react-router-dom';

import { goLogin } from '@/utils/sso';

export default function RequireAuth({ children }: { children: JSX.Element }) {
  const auth = useRouteLoaderData('root');

  if (!auth) {
    goLogin();

    return null;
  }

  return children;
}
