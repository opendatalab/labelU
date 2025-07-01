import type { GetUsersApiV1UsersGetParams } from '../types';

export const userKey = {
  all: ['user'] as const,
  me: () => [...userKey.all, 'me'] as const,
  lists: () => [...userKey.all, 'list'] as const,
  list: (filter: GetUsersApiV1UsersGetParams) => [...userKey.lists(), filter] as const,
};
