import type { Attribute } from '@labelu/interface';

export interface ToolsConfigState {
  tools: any[];
  tagList: any[];
  attributes: Attribute[];
  textConfig: any;
  commonAttributeConfigurable: boolean;
}
