import request from '../request';
import type {
  DeleteApiV1TasksTaskIdDeleteParams,
  ListByApiV1TasksTaskIdSamplesGetParams,
  OkRespCommonDataResp,
  OkRespCreateSampleResponse,
  AttachmentListResponse,
  DeletePreAnnotationFileParams,
  PreAnnotationListResponse,
} from '../types';

export async function createPreAnnotations(
  taskId: number,
  data: {
    file_id: number;
  }[],
): Promise<OkRespCreateSampleResponse> {
  return await request.post(`/v1/tasks/${taskId}/pre_annotations`, data);
}

export async function getPreAnnotationFiles({
  task_id,
  ...params
}: ListByApiV1TasksTaskIdSamplesGetParams & {
  sample_name?: string;
}): Promise<AttachmentListResponse> {
  return await request.get(`/v1/tasks/${task_id}/pre_annotations/files`, {
    params: {
      ...params,
      page: typeof params.page === 'undefined' ? 0 : params.page - 1,
    },
  });
}

export async function getPreAnnotations({
  task_id,
  ...params
}: ListByApiV1TasksTaskIdSamplesGetParams & {
  sample_name?: string;
}): Promise<PreAnnotationListResponse> {
  return await request.get(`/v1/tasks/${task_id}/pre_annotations`, {
    params: {
      ...params,
      page: typeof params.page === 'undefined' ? 0 : params.page - 1,
    },
  });
}

export async function deletePreAnnotations(
  { task_id }: DeleteApiV1TasksTaskIdDeleteParams,
  body: {
    pre_annotation_ids: number[];
  },
): Promise<OkRespCommonDataResp> {
  return await request.delete(`/v1/tasks/${task_id}/pre_annotations`, {
    data: body,
  });
}

export async function deletePreAnnotationFile({
  task_id,
  file_id,
}: DeletePreAnnotationFileParams): Promise<OkRespCommonDataResp> {
  return await request.delete(`/v1/tasks/${task_id}/pre_annotations/files/${file_id}`);
}
