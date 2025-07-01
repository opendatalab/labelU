import { useMutation } from '@tanstack/react-query';

import { uploadFile } from '@/api/services/task';

export function useUploadFileMutation() {
  return useMutation({
    mutationFn: uploadFile,
  });
}
