import { useOutlet } from 'react-router-dom';
import type { PropsWithChildren } from 'react';
import React from 'react';

import Main from '@/layouts/Main';

const CheckChildRoute: React.FC<PropsWithChildren<any>> = ({ children }) => {
  const outlet = useOutlet();

  // 如果有子路由，不渲染当前组件
  if (outlet) {
    return <Main>{outlet}</Main>;
  }

  return children;
};

export default CheckChildRoute;
