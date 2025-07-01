import { notification } from 'antd';
import { get } from 'lodash-es';
import type { AxiosError, AxiosResponse } from 'axios';
import axios from 'axios';

import commonController from '@/utils/common';
import { goLogin } from '@/utils/sso';

/**
 * 后端返回的结构由 { data, meta_data } 包裹
 * @param response
 * @returns
 */
export function successHandler(response: AxiosResponse<any>) {
  return response.data;
}

async function errorHandler(error: AxiosError) {
  let data = get(error, 'response.data');
  let errMsgFromServer = get(error, 'response.data.msg');
  let errCode = get(error, 'response.data.err_code');

  if (data instanceof Blob) {
    data = await new Response(data).json();
    errMsgFromServer = get(data, 'msg');
    errCode = get(data, 'err_code');
  }

  // 开发环境和开发自测环境显示报错信息
  if (window.DEV) {
    notification.error({
      message: `${errMsgFromServer || get(error, 'code')}【${get(error, 'response.status', '无状态码')}】`,
      description: (
        <>
          <p>{errCode}</p>
          <p>{error.message}</p>
          <p>{error.request.responseURL}</p>
        </>
      ),
    });
  } else {
    commonController.notificationErrorMessage(data ?? error, 5);
  }

  return Promise.reject(error);
}

const authorizationBearerSuccess = (config: any) => {
  const token = localStorage.token;
  if (token) {
    config.headers.Authorization = localStorage.token;
  }
  return config;
};

const authorizationBearerFailed = (error: any) => {
  // 401一秒后跳转到登录页
  if (error?.response?.status === 401) {
    localStorage.removeItem('token');
    setTimeout(() => {
      if (window.IS_ONLINE) {
        goLogin();
      } else if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }, 1000);
  }

  return Promise.reject(error);
};

const requestConfig = {
  timeout: 60 * 1000,
  baseURL: '/api',
};

const request = axios.create(requestConfig);

export const requestWithHeaders = axios.create(requestConfig);

requestWithHeaders.interceptors.request.use(authorizationBearerSuccess, authorizationBearerFailed);
requestWithHeaders.interceptors.response.use(undefined, authorizationBearerFailed);
requestWithHeaders.interceptors.response.use(undefined, errorHandler);

request.interceptors.request.use(authorizationBearerSuccess, authorizationBearerFailed);
request.interceptors.response.use(successHandler, errorHandler);
request.interceptors.response.use(undefined, authorizationBearerFailed);

export default request;
