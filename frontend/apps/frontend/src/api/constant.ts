import { i18n } from '@labelu/i18n';

const COMMON_INIT_CODE = 30000;
const USER_INIT_CODE = 40000;
const TASK_INIT_CODE = 50000;
const EXPORT_INIT_CODE = 60000;

export const ErrorMessages = {
  400: i18n.t('queryParamsError'),
  [COMMON_INIT_CODE]: i18n.t('sqlError'),
  [COMMON_INIT_CODE + 1]: i18n.t('forbidden'),
  [COMMON_INIT_CODE + 2]: i18n.t('validationFailed'),
  [COMMON_INIT_CODE + 3]: i18n.t('badRequest'),
  [USER_INIT_CODE]: i18n.t('invalidUserOrPassword'),
  [USER_INIT_CODE + 1]: i18n.t('userExists'),
  [USER_INIT_CODE + 2]: i18n.t('userNotExists'),
  [USER_INIT_CODE + 3]: i18n.t('certError'),
  [USER_INIT_CODE + 4]: i18n.t('unauthorized'),
  [TASK_INIT_CODE]: i18n.t('serverError'),
  [TASK_INIT_CODE + 1]: i18n.t('taskIsDone'),
  [TASK_INIT_CODE + 2]: i18n.t('taskNotFound'),
  [TASK_INIT_CODE + 1000]: i18n.t('fileUploadFailed'),
  [TASK_INIT_CODE + 1001]: i18n.t('fileNotFound'),
  [TASK_INIT_CODE + 1002]: i18n.t('duplicatedFile'),
  [TASK_INIT_CODE + 5001]: i18n.t('noSample'),
  [TASK_INIT_CODE + 5003]: i18n.t('sampleNameExists'),
  [EXPORT_INIT_CODE + 1000]: i18n.t('noDataExport'),
} as const;
