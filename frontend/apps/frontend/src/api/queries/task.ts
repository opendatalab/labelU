import { useQuery } from '@tanstack/react-query';

import { getTaskCollaborators } from '../services/task';
import { taskKey } from '../queryKeyFactories';

export function useCollaborators(taskId: number, enabled: boolean) {
  return useQuery({
    queryKey: taskKey.collaborators(),
    queryFn: () => getTaskCollaborators(taskId),
    enabled: enabled && taskId > 0,
    select: (data) => data?.data,
  });
}
