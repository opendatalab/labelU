import { App as AntApp, ConfigProvider } from 'antd';
import enUS from 'antd/es/locale/en_US';
import zhCN from 'antd/es/locale/zh_CN';
import { I18nProvider, useTranslation } from '@labelu/i18n';
import { useMemo } from 'react';

import RouterContainer from './components/RouterContainer';
import themeToken from './styles/theme.json';
import StaticAnt from './StaticAnt';
import routes from './routes';
import { QueryProvider } from './api/queryClient';
import GlobalStyle from './styles/GlobalStyle';

const App: React.FC = () => {
  const { i18n } = useTranslation();
  const locale = useMemo(() => {
    if (['zh', 'zh_CN', 'zh-CN', 'zh-TW', 'zh-HK'].includes(i18n.language)) {
      return 'zh-CN';
    }

    return 'en-US';
  }, [i18n.language]);
  const getAntdLocale = () => {
    if (locale === 'zh-CN') {
      return zhCN;
    } else {
      return enUS;
    }
  };

  return (
    <ConfigProvider locale={getAntdLocale()} componentSize="middle" theme={{ token: themeToken.token }}>
      <I18nProvider locale={locale}>
        <AntApp>
          <StaticAnt />
          <GlobalStyle />
          {/* @ts-ignore */}
          <QueryProvider>
            <RouterContainer routes={routes} />
          </QueryProvider>
        </AntApp>
      </I18nProvider>
    </ConfigProvider>
  );
};

export default App;
