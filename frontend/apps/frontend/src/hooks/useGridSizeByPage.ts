import { usePageSize } from './usePageSize';

export function useGridSizeByPage() {
  const pageSize = usePageSize();

  switch (pageSize) {
    case 10:
      return 2;
    case 12:
      return 3;
    case 16:
      return 4;
    case 20:
      return 5;
    case 36:
      return 6;
    default:
      return 4;
  }
}
