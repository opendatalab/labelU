import { useQuery } from '@tanstack/react-query';

import { userKey } from '../queryKeyFactories/user';
import { getUsers } from '../services/user';
import type { GetUsersApiV1UsersGetParams } from '../types';

export function useUsers(params: GetUsersApiV1UsersGetParams) {
  return useQuery({
    queryKey: userKey.list(params),
    queryFn: () => getUsers(params),
  });
}
