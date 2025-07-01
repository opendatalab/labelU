import type { PropsWithChildren } from 'react';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// 创建一个 client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});

export const QueryProvider: React.FC<PropsWithChildren> = (props) => {
  return <QueryClientProvider client={queryClient}>{props.children}</QueryClientProvider>;
};

export default queryClient;
