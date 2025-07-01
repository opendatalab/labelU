import { goLogin } from '@/utils/sso';

export async function loginLoader() {
  if (window.IS_ONLINE) {
    goLogin();

    return Promise.resolve();
  }

  return null;
}
