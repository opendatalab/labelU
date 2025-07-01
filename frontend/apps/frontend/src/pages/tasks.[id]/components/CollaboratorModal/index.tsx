import { useMemo, useState } from 'react';
import { useParams, useRouteLoaderData } from 'react-router-dom';
import { Alert, Button, Checkbox, Modal, Pagination } from 'antd';
import { FlexLayout } from '@labelu/components-react';
import { CopyOutlined, ReloadOutlined, TeamOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import type { CheckboxChangeEvent } from 'antd/es/checkbox';
import { useTranslation } from '@labelu/i18n';

import { useCollaborators } from '@/api/queries/task';
import { UserAvatar } from '@/components/UserAvatar';
import { useUsers } from '@/api/queries/user';
import {
  useAddCollaborator,
  useBatchAddCollaborators,
  useBatchRemoveCollaborators,
  useRemoveCollaborator,
} from '@/api/mutations/task';
import type { TaskLoaderResult } from '@/loaders/task.loader';
import { message } from '@/StaticAnt';

const StyledFlexLayout = styled(FlexLayout)`
  > div:nth-child(odd) {
    background-color: var(--color-fill-quaternary);
  }
`;

const FlexLayoutItem = styled(FlexLayout.Item)`
  padding: 0.5rem;
`;

export default function CollaboratorPortal() {
  const [open, setOpen] = useState(false);
  const routeParams = useParams();
  const routerData = useRouteLoaderData('task') as TaskLoaderResult;
  const task = routerData.task;
  const taskId = routeParams.taskId;
  const [params, setParams] = useState({
    page: 0,
    size: 10,
    username: '',
  });
  const { t } = useTranslation();
  const inputTaskId = taskId ? parseInt(taskId) : 0;
  const collaborators = useCollaborators(inputTaskId, open);
  const users = useUsers(params);
  const addCollaborator = useAddCollaborator(inputTaskId);
  const removeCollaborator = useRemoveCollaborator(inputTaskId);
  const batchAddCollaborators = useBatchAddCollaborators(inputTaskId);
  const batchRemoveCollaborators = useBatchRemoveCollaborators(inputTaskId);
  const collaboratorIds = useMemo(() => {
    return collaborators?.data?.map((item) => item.id) || [];
  }, [collaborators]);
  const usersExceptCreator = useMemo(() => {
    return users.data?.data?.filter((item) => item.id !== task?.created_by?.id) ?? [];
  }, [task?.created_by?.id, users.data?.data]);
  const isAllChecked = useMemo(() => {
    return usersExceptCreator.every((item) => collaboratorIds.includes(item.id!));
  }, [collaboratorIds, usersExceptCreator]);
  const isSomeChecked = useMemo(() => {
    return usersExceptCreator.some((item) => collaboratorIds.includes(item.id!));
  }, [collaboratorIds, usersExceptCreator]);
  const handleOpen = () => {
    setOpen(true);
  };
  const handlePaginationChange = (page: number) => {
    setParams({
      ...params,
      page: page - 1,
    });
  };
  const handleCollaboratorChange = async (e: CheckboxChangeEvent) => {
    if (e.target.checked) {
      await addCollaborator.mutateAsync(parseInt(e.target.value));
    } else {
      await removeCollaborator.mutateAsync(parseInt(e.target.value));
    }

    collaborators.refetch();
  };
  const handleCheckAllChange = async (e: CheckboxChangeEvent) => {
    if (e.target.checked) {
      const ids = usersExceptCreator
        ?.map((item) => item.id!)
        .filter((id) => !collaboratorIds.includes(id) && task?.created_by?.id !== id);

      if (ids) {
        await batchAddCollaborators.mutateAsync(ids);
      }
    } else {
      const ids = usersExceptCreator
        ?.map((item) => item.id!)
        .filter((id) => collaboratorIds.includes(id) && task?.created_by?.id !== id);

      if (ids) {
        await batchRemoveCollaborators.mutateAsync(ids);
      }
    }

    collaborators.refetch();
  };

  return (
    <>
      <Button type="text" icon={<TeamOutlined />} onClick={handleOpen}>
        {t('collaborators')}
      </Button>
      <Modal title={t('collaborators')} open={open} onCancel={() => setOpen(false)} footer={null}>
        <FlexLayout flex="column" gap="1rem" items="stretch">
          <Alert
            type="info"
            message={
              <div>
                {t('shareTaskLink')}
                <Button
                  type="link"
                  size="small"
                  icon={<CopyOutlined />}
                  onClick={() => {
                    navigator.clipboard.writeText(window.location.href);
                    message.success(t('copied'));
                  }}
                />
                {t('inviteRegister')}
                {t('invitationTips')}
                {t('afterInvitation')}
              </div>
            }
          />
          <FlexLayout flex="row" justify="space-between">
            <FlexLayout.Item flex="row" gap=".5rem" items="center">
              {t('users')}
              <Button
                type="text"
                size="small"
                icon={<ReloadOutlined />}
                onClick={() => users.refetch()}
                loading={users.isFetching}
              />
            </FlexLayout.Item>
            <FlexLayout.Item>
              <Checkbox
                onChange={handleCheckAllChange}
                checked={isAllChecked}
                indeterminate={!isAllChecked && isSomeChecked}
              >
                {t('selectAll')}
              </Checkbox>
            </FlexLayout.Item>
          </FlexLayout>
          <StyledFlexLayout flex="column">
            <FlexLayoutItem flex="row" items="center" justify="space-between">
              <UserAvatar
                shortName={false}
                showTooltip={false}
                user={task?.created_by}
                style={{ backgroundColor: 'var(--color-primary)', color: '#fff' }}
              />
              {t('creator')}
            </FlexLayoutItem>
            {users.data?.data
              ?.filter((item) => item.id !== task?.created_by?.id)
              ?.map((item) => (
                <FlexLayoutItem flex="row" key={item.id} items="center" justify="space-between">
                  <UserAvatar
                    shortName={false}
                    showTooltip={false}
                    user={item}
                    style={{ backgroundColor: 'var(--color-primary)', color: '#fff' }}
                  />
                  <Checkbox
                    checked={collaboratorIds.includes(item.id)}
                    value={item.id}
                    onChange={handleCollaboratorChange}
                  >
                    {collaboratorIds.includes(item.id) ? t('joined') : t('join')}
                  </Checkbox>
                </FlexLayoutItem>
              ))}
          </StyledFlexLayout>
          <FlexLayout.Item flex="row" justify="center">
            <Pagination
              size="small"
              defaultCurrent={1}
              total={users.data?.meta_data?.total}
              onChange={handlePaginationChange}
            />
          </FlexLayout.Item>
        </FlexLayout>
      </Modal>
    </>
  );
}
