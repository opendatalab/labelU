import { FlexLayout } from '@labelu/components-react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { BiLinkExternal } from '@react-icons/all-files/bi/BiLinkExternal';
import { AiOutlineGithub } from '@react-icons/all-files/ai/AiOutlineGithub';
import clsx from 'clsx';

import { ReactComponent as Logo } from '@/assets/logo.svg';

const links = [
  {
    title: '使用指南',
    path: 'guide',
    icon: null,
  },
  {
    title: '标注结果格式',
    path: 'schema',
    icon: null,
  },
  {
    title: 'API',
    path: 'api',
    icon: <BiLinkExternal />,
    type: 'external',
  },
  {
    title: 'LabelU-kit',
    path: 'https://github.com/opendatalab/labelU-kit#readme',
    icon: <BiLinkExternal />,
    type: 'external',
  },
  {
    title: (
      <span className="text-2xl">
        <AiOutlineGithub />
      </span>
    ),
    path: 'https://github.com/opendatalab/labelU',
    icon: null,
    type: 'external',
  },
];

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (location.pathname === '/') {
      navigate('/guide');
    }
  }, [location.pathname, navigate]);

  return (
    <FlexLayout flex="column" full items="stretch">
      <FlexLayout.Header flex justify="space-between" items="center" gap="1rem" className="h-[56px] px-6">
        <FlexLayout.Item flex gap="4rem">
          <Link to="/">
            <FlexLayout gap=".5rem" items="center">
              <div className="text-3xl">
                <Logo />
              </div>
              <span className="font-bold">LabelU</span>
            </FlexLayout>
          </Link>
        </FlexLayout.Item>
        <FlexLayout.Item flex gap="4rem">
          <FlexLayout.Item flex items="center" gap="1rem">
            {links.map(({ title, path, icon, type }) => (
              <Link
                key={path}
                to={path}
                target={type === 'external' ? '_blank' : undefined}
                className={clsx('flex items-center gap-1 px-4 py-2 rounded-full', {
                  'bg-primary text-white': location.pathname.startsWith(`/${path}`),
                })}
              >
                {title} {icon}
              </Link>
            ))}
          </FlexLayout.Item>
        </FlexLayout.Item>
      </FlexLayout.Header>
      <FlexLayout.Content flex="column">
        <Outlet />
      </FlexLayout.Content>
    </FlexLayout>
  );
}
