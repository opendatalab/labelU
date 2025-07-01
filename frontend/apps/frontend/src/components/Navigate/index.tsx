import Icon, { BellOutlined, PoweroffOutlined } from '@ant-design/icons';
import { FlexLayout } from '@labelu/components-react';
import { Button, Divider, Dropdown, Popover, Tag } from 'antd';
import { Link, useMatch, useNavigate } from 'react-router-dom';
import { useTranslation } from '@labelu/i18n';

import { ReactComponent as LocalDeploy } from '@/assets/svg/local-deploy.svg';
import { ReactComponent as ToolboxSvg } from '@/assets/svg/toolbox.svg';
import { goAuth } from '@/utils/sso';
import useMe from '@/hooks/useMe';

import AppPanel from '../AppPanel';
import Breadcrumb from '../Breadcrumb';
import { LabeluLogo, NavigationWrapper } from './style';
import TaskTip from './TaskTip';
import LanguageSwitcher from '../LangSwitcher';
import { UserAvatar } from '../UserAvatar';

const Homepage = () => {
  const me = useMe();
  const navigate = useNavigate();
  const isSampleDetail = useMatch('/tasks/:taskId/samples/:sampleId');
  const { t, i18n } = useTranslation();

  const logout = async (e: any) => {
    e.stopPropagation();
    e.nativeEvent.stopPropagation();
    e.preventDefault();

    localStorage.setItem('token', '');

    if (window.IS_ONLINE) {
      await goAuth();
    } else {
      navigate('/login');
    }
  };

  return (
    <NavigationWrapper className="navigation" items="center" justify="space-between" padding="0 1.5rem">
      <FlexLayout.Item flex items="center" gap={window.IS_ONLINE ? '.5rem' : '3rem'}>
        <Link to="/">
          <FlexLayout.Item flex items="center">
            <LabeluLogo />

            {window.IS_ONLINE && (
              <Tag bordered={false} color="var(--color-fill-secondary)" style={{ color: 'var(--color-text)' }}>
                Beta
              </Tag>
            )}
          </FlexLayout.Item>
        </Link>
        {window.IS_ONLINE && <Divider type="vertical" />}
        <Breadcrumb hideHome={window.IS_ONLINE} />
      </FlexLayout.Item>
      <FlexLayout.Item flex gap="1rem">
        <TaskTip visible={Boolean(isSampleDetail)} />
        {window.IS_ONLINE && (
          <Popover title={null} content={<AppPanel />}>
            <Button
              type="link"
              icon={<ToolboxSvg />}
              style={{ color: 'rgba(0, 0, 0, 0.85)', display: 'flex', alignItems: 'center' }}
            >
              {t('openSourceToolbox')}
            </Button>
          </Popover>
        )}
        {window.IS_ONLINE && (
          <a
            data-wiz="local-deploy-top-right"
            href={`https://opendatalab.github.io/labelU/${i18n.language.startsWith('en') ? 'en/' : ''}guide/install`}
          >
            <Button type="link" style={{ color: 'rgba(0, 0, 0, 0.85)' }} icon={<Icon component={LocalDeploy} />}>
              {t('localDeploy')}
            </Button>
          </a>
        )}
        <Button
          type="link"
          data-wiz="documentation"
          icon={<BellOutlined />}
          href={`https://opendatalab.github.io/labelU/${i18n.language.startsWith('en') ? 'en/' : ''}guide/introduction`}
          style={{ color: 'rgba(0, 0, 0, 0.85)' }}
          target="_blank"
          rel="noreferrer"
        >
          {t('documentation')}
        </Button>
        <LanguageSwitcher />
        <Dropdown
          trigger={['click']}
          menu={{
            items: [
              {
                label: (
                  <FlexLayout.Item onClick={logout} flex gap=".5rem" padding=".25rem 0">
                    <PoweroffOutlined />
                    <span>{t('logout')}</span>
                  </FlexLayout.Item>
                ),
                key: 'logout',
                title: t('logout'),
              },
            ],
          }}
        >
          <UserAvatar
            user={me?.data}
            shortName={false}
            showTooltip={false}
            placement="bottomRight"
            style={{ backgroundColor: 'var(--color-primary)', color: '#fff' }}
          />
        </Dropdown>
      </FlexLayout.Item>
    </NavigationWrapper>
  );
};
export default Homepage;
