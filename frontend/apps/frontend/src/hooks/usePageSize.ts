import { useResponse } from './useResponsive';

/**
 * 相应布局的分页大小配置，XXSmall, XSmall, Small, Regular, Large, XLarge
 */
export interface PageSizeConfig {
  /**
   * page size in XXSmall screen
   */
  xxsmall: number;
  /**
   * page size in XSmall screen
   */
  xsmall: number;
  /**
   * page size in Regular screen
   */
  small: number;
  /**
   * page size in Regular screen
   */
  regular: number;
  /**
   * page size in Large screen
   */
  large: number;
  /**
   * page size in XLarge screen
   */
  xlarge: number;
}

const defaultPageSizeMapping = {
  xxsmall: 16,
  xsmall: 16,
  small: 16,
  regular: 16,
  large: 20,
  xlarge: 36,
};

export function usePageSize(pageSizeConfig: PageSizeConfig = defaultPageSizeMapping) {
  const screenType = useResponse();

  return pageSizeConfig[screenType] || defaultPageSizeMapping.regular;
}
