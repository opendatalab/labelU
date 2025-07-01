import { Button, Dropdown } from 'antd';
import { useTranslation } from '@labelu/i18n';
import { useMemo } from 'react';
import Icon from '@ant-design/icons';

import { ReactComponent as I18nSvg } from '@/assets/i18n.svg';

const langOptions = [
  {
    key: 'zh-CN',
    label: '简体中文',
    value: 'zh-CN',
  },
  {
    key: 'en-US',
    label: 'English',
    value: 'en-US',
  },
];

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const lang = useMemo(() => {
    return ['zh', 'zh_CN', 'zh-CN'].includes(i18n.language) ? 'zh-CN' : 'en-US';
  }, [i18n.language]);

  const langLabel = useMemo(() => {
    return langOptions.find((item) => item.key === lang)?.label;
  }, [lang]);

  const changeLocale = (e: any) => {
    i18n.changeLanguage(e.key);
    window.location.reload();
  };

  return (
    <Dropdown
      menu={{
        items: langOptions,
        onClick: changeLocale,
        defaultSelectedKeys: [lang],
      }}
    >
      <Button icon={<Icon component={I18nSvg} />} type="link" style={{ color: 'rgba(0, 0, 0, 0.85)' }}>
        {langLabel}
      </Button>
    </Dropdown>
  );
}
