import type { MockMethod } from 'vite-plugin-mock';

export default [
  {
    url: '/api/v1/auth/me',
    method: 'post',
    timeout: 100,
    response: () => {
      return {
        id: '1',
        name: 'lisi',
      };
    },
  },
] as MockMethod[];
