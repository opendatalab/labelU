import { InfoCircleOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router';
import { Button } from 'antd';
import { FlexLayout } from '@labelu/components-react';
import { useTranslation } from '@labelu/i18n';

import { TaskStatus } from '@/api/types';

const GoToEditTask = (props: any) => {
  const { t } = useTranslation();
  const { taskStatus } = props;
  const navigate = useNavigate();
  const routeParams = useParams();
  const taskId = +routeParams.taskId!;

  const handleConfigClick = () => {
    if (taskId > 0) {
      let tail = 'basic';
      switch (taskStatus) {
        case TaskStatus.DRAFT:
          tail = 'basic';
          break;
        case TaskStatus.IMPORTED:
        case TaskStatus.CONFIGURED:
          tail = 'config';
          break;
      }
      navigate('/tasks/' + taskId + '/edit#' + tail);
    }
  };

  return (
    <FlexLayout items="center" gap=".5rem">
      <InfoCircleOutlined style={{ color: '#F5483B' }} />
      <div>{t('configBeforeStart')}</div>
      <Button type="primary" ghost onClick={handleConfigClick}>
        {t('configTask')}
      </Button>
    </FlexLayout>
  );
};
export default GoToEditTask;
