import React from 'react';
import type { FormInstance } from 'antd';

import type { TaskInLoader } from '@/loaders/task.loader';

import type { QueuedFile } from './partials/InputData';

export interface TaskCreationContextValue {
  task: NonNullable<TaskInLoader>;
  uploadFileList: QueuedFile[];
  setUploadFileList: React.Dispatch<React.SetStateAction<QueuedFile[]>>;
  annotationFormInstance: FormInstance;
  basicFormInstance: FormInstance;
  onAnnotationFormChange: () => void;
  selectedTemplate: unknown;
  onTemplateSelect: (template: unknown) => void;
}

export const TaskCreationContext = React.createContext<TaskCreationContextValue>({} as TaskCreationContextValue);
