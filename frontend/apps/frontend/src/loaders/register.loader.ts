import { redirect } from 'react-router';

import { goRegister } from '@/utils/sso';
import * as storage from '@/utils/storage';

export async function registerLoader() {
  if (storage.get('token')) {
    return redirect('/tasks');
  }

  if (window.IS_ONLINE) {
    goRegister();

    return Promise.resolve();
  }

  return null;
}
