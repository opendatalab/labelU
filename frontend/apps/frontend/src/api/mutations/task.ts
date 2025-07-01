import { useMutation } from '@tanstack/react-query';

import {
  addCollaborator,
  batchAddCollaborators,
  batchRemoveCollaborators,
  createTaskWithBasicConfig,
  removeCollaborator,
  updateTaskConfig,
} from '@/api/services/task';

import type { UpdateCommand } from '../types';

export function useAddTaskMutation() {
  return useMutation({
    mutationFn: createTaskWithBasicConfig,
  });
}

export function useUpdateTaskConfigMutation(taskId: number | string) {
  return useMutation({
    mutationFn: (payload: UpdateCommand) => updateTaskConfig(+taskId, payload),
  });
}

export function useAddCollaborator(taskId: number) {
  return useMutation({
    mutationFn: (userId: number) => addCollaborator(taskId, userId),
  });
}

export function useRemoveCollaborator(taskId: number) {
  return useMutation({
    mutationFn: (userId: number) => removeCollaborator(taskId, userId),
  });
}

export function useBatchAddCollaborators(taskId: number) {
  return useMutation({
    mutationFn: (userIds: number[]) => batchAddCollaborators(taskId, userIds),
  });
}

export function useBatchRemoveCollaborators(taskId: number) {
  return useMutation({
    mutationFn: (userIds: number[]) => batchRemoveCollaborators(taskId, userIds),
  });
}
