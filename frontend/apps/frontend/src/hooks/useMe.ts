import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { getUserInfo } from '@/api/services/user';
import { userKey } from '@/api/queryKeyFactories/user';
import type { UserResponse } from '@/api/types';
import * as storage from '@/utils/storage';

export default function useMe() {
  return useQuery({
    queryKey: userKey.me(),
    queryFn: () => getUserInfo(),
    gcTime: Infinity,
    staleTime: Infinity,
    select: (data) => data.data,
    enabled: !!storage.get('token'),
  }) as UseQueryResult<UserResponse>;
}
