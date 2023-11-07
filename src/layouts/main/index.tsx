import { Link, Outlet, useLocation, useMatch, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { BiLinkExternal } from '@react-icons/all-files/bi/BiLinkExternal';
import { AiOutlineGithub } from '@react-icons/all-files/ai/AiOutlineGithub';
import clsx from 'clsx';
import { BiMenu } from '@react-icons/all-files/bi/BiMenu';

import { ReactComponent as Logo } from '@/assets/logo.svg';
import { Drawer } from '@/components/drawer';
import { Menu } from '@/components/menu';

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
  const match = useMatch('/:path/*');
  const secondPath = match?.pathname.split('/')[1];

  useEffect(() => {
    if (location.pathname === '/') {
      navigate('/guide');
    }
  }, [location.pathname, navigate]);

  return (
    <div className="flex flex-col items-stretch">
      <header className="flex justify-between items-center gap-4 h-[56px] px-6">
        <div className="flex gap-2 items-center">
          <Link to="/">
            <div className="flex items-center gap-2">
              <div className="text-3xl">
                <Logo />
              </div>
              <span className="font-bold">LabelU</span>
            </div>
          </Link>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-4">
            {links.map(({ title, path, icon, type }) => (
              <Link
                key={path}
                to={path}
                target={type === 'external' ? '_blank' : undefined}
                className={clsx('hidden items-center gap-1 px-4 py-2 rounded-full', {
                  'bg-primary text-white': location.pathname.startsWith(`/${path}`),
                  'xs:flex': type !== 'external',
                  'sm:flex': type === 'external',
                })}
              >
                {title} {icon}
              </Link>
            ))}
            <div className="block sm:hidden">
              <Drawer content={<Menu path={`/${secondPath}`} />}>
                <button className="btn btn-ghost text-lg">
                  <BiMenu />
                </button>
              </Drawer>
            </div>
          </div>
        </div>
      </header>
      <div className="flex min-h-0 overflow-auto flex-col">
        <div className="hidden sm:block lg:w-[280px] sm:w-[180px] max-h-[calc(100vh-56px)] overflow-auto">
          <Menu path="/guide" />
        </div>
        <div className="flex min-h-0 overflow-auto flex-auto max-h-[calc(100vh-56px)]">
          <div className="flex min-h-0 overflow-auto flex-auto prose prose-slate py-2 px-6">
            <Outlet />
          </div>
        </div>
      </div>
    </div>
  );
}
