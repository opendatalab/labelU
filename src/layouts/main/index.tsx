import { Link, Outlet, useLocation, useMatch, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { BiLinkExternal } from '@react-icons/all-files/bi/BiLinkExternal';
import { BiBookBookmark } from '@react-icons/all-files/bi/BiBookBookmark';
import { BiCodeBlock } from '@react-icons/all-files/bi/BiCodeBlock';
import { AiOutlineGithub } from '@react-icons/all-files/ai/AiOutlineGithub';
import { HiTranslate } from '@react-icons/all-files/hi/HiTranslate';
import clsx from 'clsx';
import { BiMenu } from '@react-icons/all-files/bi/BiMenu';
import { useTranslation } from 'react-i18next';

import { ReactComponent as Logo } from '@/assets/logo.svg';
import { Drawer } from '@/components/drawer';
import { Menu } from '@/components/menu';
import i18nLocale from '@/locale';

const links = [
  {
    title: i18nLocale.t('guide'),
    path: 'guide',
    icon: <BiBookBookmark />,
  },
  {
    title: i18nLocale.t('schema'),
    path: 'schema',
    icon: <BiCodeBlock />,
  },
  {
    title: 'LabelU-kit',
    path: 'https://github.com/opendatalab/labelU-kit#readme',
    icon: null,
    type: 'external',
  },
];

const langs = [
  {
    title: '中文',
    path: 'zh-CN',
  },
  {
    title: 'English',
    path: 'en-US',
  },
];

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const match = useMatch('/:path/*');
  const secondPath = match?.pathname.split('/')[1];
  const { i18n } = useTranslation();

  useEffect(() => {
    if (location.pathname === '/' || location.pathname === '/guide') {
      navigate(`/guide/introduction`, {
        replace: true,
      });
    }
  }, [i18n.language, location.pathname, navigate]);

  const handleLangChange = (lang: string) => () => {
    i18n.changeLanguage(lang);
    window.location.reload();
  };

  return (
    <div className="flex flex-col items-stretch">
      <header className="flex justify-between items-center gap-4 h-[64px] px-2 sm:px-6 shadow-sm">
        <div className="flex gap-2 items-center">
          <div className="block sm:hidden">
            <Drawer
              content={
                <div className="flex flex-col">
                  <div className="flex my-2 text-sm justify-around">
                    {links.map(({ title, path, icon, type }) => (
                      <Link
                        key={path}
                        to={path}
                        target={type === 'external' ? '_blank' : undefined}
                        className={clsx('items-center gap-1 p-2 flex', {
                          'text-[var(--color-primary)': location.pathname.startsWith(`/${path}`),
                        })}
                      >
                        {icon} {title}
                      </Link>
                    ))}
                  </div>
                  <Menu path={`/${secondPath}`} />
                </div>
              }
              width="calc(100vw - 72px)"
            >
              <button className="btn btn-ghost text-xl">
                <BiMenu />
              </button>
            </Drawer>
          </div>
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
          <div className="flex items-center gap-2">
            <div className="hidden sm:flex">
              {links.map(({ title, path, icon, type }) => (
                <Link
                  key={path}
                  to={path}
                  target={type === 'external' ? '_blank' : undefined}
                  className={clsx('hidden items-center gap-1 px-4 py-2 rounded-full hover:text-[var(--color-primary)', {
                    'text-[var(--color-primary)]': location.pathname.startsWith(`/${path}`),
                    'xs:flex': type !== 'external',
                    'sm:flex': type === 'external',
                  })}
                >
                  <span className="text-xl">{icon}</span> {title}
                  {type === 'external' && <BiLinkExternal />}
                </Link>
              ))}
            </div>
            <details className="dropdown dropdown-bottom dropdown-end">
              <summary className="m-1 btn btn-ghost">
                <HiTranslate className="text-lg" />
                <svg
                  width="12px"
                  height="12px"
                  className="hidden h-2 w-2 fill-current opacity-60 sm:inline-block"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 2048 2048"
                >
                  <path d="M1799 349l242 241-1017 1017L7 590l242-241 775 775 775-775z" />
                </svg>
              </summary>
              <ul className="p-2 shadow menu dropdown-content z-[1] bg-base-100 rounded-box w-52">
                {langs.map(({ title, path }) => (
                  <li
                    key={path}
                    onClick={handleLangChange(path)}
                    className={clsx('hover:text-[var(--color-primary)', {
                      'text-[var(--color-primary)]': i18n.language === path,
                      'cursor-pointer': i18n.language !== path,
                    })}
                  >
                    <a>{title}</a>
                  </li>
                ))}
              </ul>
            </details>
            <Link
              to="https://github.com/opendatalab/labelU"
              target="_blank"
              className={clsx('items-center gap-1 px-2 py-2 rounded-full')}
            >
              <span className="text-2xl">
                <AiOutlineGithub />
              </span>
            </Link>
          </div>
        </div>
      </header>
      <div className="flex min-h-0 overflow-auto">
        <div className="hidden sm:block py-2 px-2 sm:w-[280px] max-h-[calc(100vh-64px)] overflow-auto">
          <Menu path={`/${secondPath}`} />
        </div>
        <div className="flex min-h-0 overflow-auto justify-center flex-auto max-h-[calc(100vh-64px)]  py-16 px-6">
          <div className="prose">
            <Outlet />
          </div>
        </div>
      </div>
    </div>
  );
}
