import commonController from '@/utils/common';

import request from '../request';
import { getTask } from './task';
import {
  ExportType,
  type DeleteApiV1TasksTaskIdDeleteParams,
  type DeleteSampleCommand,
  type GetApiV1TasksTaskIdSamplesSampleIdGetParams,
  type GetPreApiV1TasksTaskIdSamplesSampleIdPreGetParams,
  type ListByApiV1TasksTaskIdSamplesGetParams,
  type OkRespCommonDataResp,
  type OkRespCreateSampleResponse,
  type OkRespSampleResponse,
  type PatchSampleCommand,
  type SampleData,
  type SampleListResponse,
  type SampleResponse,
  type UpdateApiV1TasksTaskIdSamplesSampleIdPatchParams,
} from '../types';

export async function createSamples(
  taskId: number,
  data: {
    file_id: number;
    data: SampleData;
  }[],
): Promise<OkRespCreateSampleResponse> {
  return await request.post(`/v1/tasks/${taskId}/samples`, data);
}

export async function getSamples({
  task_id,
  ...params
}: ListByApiV1TasksTaskIdSamplesGetParams): Promise<SampleListResponse> {
  return await request.get(`/v1/tasks/${task_id}/samples`, {
    params: {
      ...params,
      page: typeof params.page === 'undefined' ? 0 : params.page - 1,
    },
  });
}

export async function getSample({
  task_id,
  sample_id,
}: GetApiV1TasksTaskIdSamplesSampleIdGetParams): Promise<OkRespSampleResponse> {
  return await request.get(`/v1/tasks/${task_id}/samples/${sample_id}`);
}

export async function updateSampleState(
  { task_id, sample_id, ...params }: UpdateApiV1TasksTaskIdSamplesSampleIdPatchParams,
  body: PatchSampleCommand,
): Promise<SampleResponse> {
  return await request.patch(`/v1/tasks/${task_id}/samples/${sample_id}`, body, {
    params: {
      sample_id,
      ...params,
    },
  });
}

export async function updateSampleAnnotationResult(
  taskId: number,
  sampleId: number,
  data: SampleResponse,
): Promise<SampleResponse> {
  return await request.patch(
    `/v1/tasks/${taskId}/samples/${sampleId}`,
    {
      data: data.data,
      state: data.state,
      annotated_count: data.annotated_count,
    },
    {
      params: {
        sample_id: sampleId,
      },
    },
  );
}

export async function outputSample(taskId: number, sampleIds: number[], activeTxt: ExportType) {
  const headers = {} as any;

  if (
    [
      ExportType.MASK,
      ExportType.LABEL_ME,
      ExportType.YOLO,
      ExportType.CSV,
      ExportType.XML,
      ExportType.TF_RECORD,
      ExportType.PASCAL_VOC,
    ].includes(activeTxt)
  ) {
    headers.responseType = 'blob';
  }

  const data = await request.post(
    `/v1/tasks/${taskId}/samples/export`,
    {
      sample_ids: sampleIds,
    },
    {
      params: {
        task_id: taskId,
        export_type: activeTxt,
      },
      ...headers,
    },
  );
  const taskRes = await getTask(taskId);

  const blobData = new Blob([JSON.stringify(data)]);
  let url = window.URL.createObjectURL(blobData);
  const a = document.createElement('a');
  let filename = taskRes.data.name;

  switch (activeTxt) {
    case ExportType.JSON:
    case ExportType.COCO:
      filename = filename + '.json';
      break;
    case ExportType.MASK:
    case ExportType.CSV:
    case ExportType.XML:
    case ExportType.LABEL_ME:
    case ExportType.YOLO:
    case ExportType.TF_RECORD:
    case ExportType.PASCAL_VOC:
      url = window.URL.createObjectURL(data as any);
      break;
  }
  a.download = filename!;
  a.href = url;
  a.click();
}

export async function outputSamples(taskId: number, activeTxt: ExportType) {
  const samplesRes = await getSamples({ task_id: taskId, page: 1, size: 100000 });
  const sampleIdArrays = samplesRes.data;
  const sampleIds = [];

  for (const sample of sampleIdArrays) {
    sampleIds.push(sample.id!);
  }

  if (sampleIds.length === 0) {
    commonController.notificationErrorMessage({ message: '后端返回数据出现问题' }, 1);
    return;
  }

  await outputSample(taskId, sampleIds, activeTxt);

  return true;
}

export async function deleteSamples(
  { task_id }: DeleteApiV1TasksTaskIdDeleteParams,
  body: DeleteSampleCommand,
): Promise<OkRespCommonDataResp> {
  return await request.delete(`/v1/tasks/${task_id}/samples`, {
    data: body,
  });
}

export async function getPreSample({
  sample_id,
  task_id,
}: GetPreApiV1TasksTaskIdSamplesSampleIdPreGetParams): Promise<OkRespSampleResponse> {
  return await request.get(`/v1/tasks/${task_id}/samples/${sample_id}/pre`);
}
