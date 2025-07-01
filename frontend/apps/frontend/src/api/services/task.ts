import request, { requestWithHeaders } from '../request';
import type {
  BasicConfigCommand,
  OkRespCommonDataResp,
  OkRespTaskResponse,
  TaskListResponseWithStatics,
  OkRespTaskResponseWithStatics,
  UpdateCommand,
  ListByApiV1TasksGetParams,
  OkRespAttachmentResponse,
  CreateApiV1TasksTaskIdAttachmentsPostParams,
  DeleteApiV1TasksTaskIdAttachmentsDeleteParams,
  AttachmentDeleteCommand,
  ListResponseWithMeta,
  UserResponse,
  OkResponse,
} from '../types';

export async function getTask(taskId: number): Promise<OkRespTaskResponseWithStatics> {
  return await request.get(`/v1/tasks/${taskId}`, {
    params: {
      task_id: taskId,
    },
  });
}

export async function getTaskCollaborators(taskId: number): Promise<ListResponseWithMeta<UserResponse>> {
  return await request.get(`/v1/tasks/${taskId}/collaborators`);
}

export async function removeCollaborator(taskId: number, userId: number) {
  return await request.delete(`/v1/tasks/${taskId}/collaborators/${userId}`);
}

export async function addCollaborator(taskId: number, userId: number) {
  return await request.post(`/v1/tasks/${taskId}/collaborators`, {
    user_id: userId,
  });
}

export async function batchAddCollaborators(taskId: number, userIds: number[]): Promise<OkResponse<UserResponse>> {
  return await request.post(`/v1/tasks/${taskId}/collaborators/batch_add`, {
    user_ids: userIds,
  });
}

export async function batchRemoveCollaborators(taskId: number, userIds: number[]): Promise<OkRespCommonDataResp> {
  return await request.post(`/v1/tasks/${taskId}/collaborators/batch_remove`, {
    user_ids: userIds,
  });
}

export async function createTaskWithBasicConfig(data: BasicConfigCommand): Promise<OkRespTaskResponse> {
  return await request.post('/v1/tasks', data);
}

export async function uploadFile(
  params: CreateApiV1TasksTaskIdAttachmentsPostParams & {
    file: File;
  },
): Promise<OkRespAttachmentResponse> {
  const data = new FormData();

  if (params.file) {
    data.append('file', params.file);
  }

  return await request.post(`/v1/tasks/${params.task_id}/attachments`, data, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
}

export async function deleteFile(
  { task_id, ...restParams }: DeleteApiV1TasksTaskIdAttachmentsDeleteParams,
  body: AttachmentDeleteCommand,
): Promise<OkRespCommonDataResp> {
  return await request.delete(`/v1/tasks/${task_id}/attachments`, {
    params: restParams,
    data: body,
  });
}

export async function updateTaskConfig(taskId: number, taskConfig: UpdateCommand): Promise<OkRespTaskResponse> {
  return await request.patch(`/v1/tasks/${taskId}`, taskConfig);
}

export async function getTaskList({
  page,
  ...params
}: ListByApiV1TasksGetParams): Promise<TaskListResponseWithStatics> {
  return await requestWithHeaders.get('/v1/tasks', {
    timeout: 0,
    params: {
      size: 16,
      page: page ? page - 1 : 0,
      ...params,
    },
  });
}

export async function deleteTask(taskId: number): Promise<OkRespCommonDataResp> {
  return await request.delete(`/v1/tasks/${taskId}`, {
    params: {
      task_id: taskId,
    },
  });
}
