import * as storage from '@/utils/storage';

import request from '../request';
import type {
  GetUsersApiV1UsersGetParams,
  ListResponseWithMeta,
  LoginCommand,
  OkRespLoginResponse,
  OkRespLogoutResponse,
  OkRespSignupResponse,
  OkRespUserInfo,
  SignupCommand,
  UserResponse,
} from '../types';

export async function login(params: LoginCommand): Promise<OkRespLoginResponse> {
  const result = await request.post('/v1/users/login', params);

  storage.set('token', result.data.token);

  return result;
}

export async function ssoLogin(code: string) {
  const result = await request.post(`/v1/users/token?code=${code}`);

  storage.set('token', result.data.token);

  return result;
}

export async function getUserInfo(): Promise<OkRespUserInfo> {
  return await request.get('/v1/users/me');
}

export async function getUsers(params: GetUsersApiV1UsersGetParams): Promise<ListResponseWithMeta<UserResponse>> {
  return await request.get('/v1/users', {
    params,
  });
}

export async function logout(): Promise<OkRespLogoutResponse> {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  localStorage.removeItem('userid');

  return await request.post('/v1/users/logout');
}

export async function signUp(params: SignupCommand): Promise<OkRespSignupResponse> {
  return await request.post('/v1/users/signup', params);
}
