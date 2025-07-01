import type { ListByApiV1TasksGetParams } from '../types';

// 标注任务
export const taskKey = {
  all: ['taskKey'] as const,
  lists: () => [...taskKey.all, 'list'] as const,
  list: (filter: ListByApiV1TasksGetParams) => [...taskKey.lists(), filter] as const,
  details: () => [...taskKey.all, 'details'] as const,
  detail: (id: string | number) => [...taskKey.details(), id] as const,
  collaborators: () => [...taskKey.all, 'collaborators'] as const,
};
