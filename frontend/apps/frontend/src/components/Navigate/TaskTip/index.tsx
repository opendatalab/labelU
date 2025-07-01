import { BulbOutlined } from '@ant-design/icons';
import { Button, Popover } from 'antd';
import { useRouteLoaderData } from 'react-router';
import { useTranslation } from '@labelu/i18n';

import type { TaskLoaderResult } from '@/loaders/task.loader';

export default function TaskTip({ visible }: { visible: boolean }) {
  const { task } = (useRouteLoaderData('task') ?? {}) as TaskLoaderResult;
  const { t } = useTranslation();

  if (!visible) {
    return null;
  }

  return (
    <Popover content={<div style={{ maxWidth: 420 }}>{task?.tips ?? t('noneTaskTip')}</div>}>
      <Button type="link" style={{ color: 'rgba(0, 0, 0, 0.85)' }} icon={<BulbOutlined />}>
        {t('taskTip')}
      </Button>
    </Popover>
  );
}
