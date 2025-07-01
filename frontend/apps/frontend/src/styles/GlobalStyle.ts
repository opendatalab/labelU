import { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
html,
body,
#root,
#root > * {
  margin: 0;
}

:root {
  --header-height: 3.5rem;
}

body {
  font-size: 14px;
  color: #333 !important;
}

#root, .ant-app {
  min-height: 100vh;
}

.sensebee-input-wrap .deleteIcon {
  color: #ccc;
}

/* ant-design */

.ant-list-item {
  padding: 12px !important;
}

.ant-table-cell .ant-btn.ant-btn-link {
  padding: 0 4px !important;
}

.ant-tabs-tab + .ant-tabs-tab {
  margin: 0 0 0 3px;
}

.ant-dropdown-menu {
  padding: 12px 0 0;
  overflow: hidden;
}

.ant-dropdown-menu-item {
  margin-bottom: 12px;
}

.ant-collapse-header {
  height: 32px;
  align-items: center !important;
}

.ant-btn-primary {
  box-shadow: none !important;
  text-shadow: none;
}

.ant-input:focus,
.ant-input-number:focus,
.ant-input-number-focused {
  box-shadow: none !important;
}

.ant-select-focused .ant-select-selector {
  box-shadow: none !important;
}

.ant-btn-default {
  border: 0;
  background-color: #f4f5f9;
}

.ant-btn-link {
  padding: 0;
  height: initial;
}

.ant-form-item:last-child {
  margin-bottom: 0;
}

.ant-form-item .ant-form-item-label > label .ant-form-item-tooltip {
  font-size: 1rem;
}
`;

export default GlobalStyle;
