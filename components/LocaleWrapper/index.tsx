import { I18nProvider, useTranslation } from '@labelu/i18n';
import React, { useMemo } from 'react';

export default function LocaleWrapper({ children }: any) {
  const { i18n } = useTranslation();

  const locale = useMemo(() => {
    if (location.pathname.includes('/en')) {
      return 'en-US';
    }

    return 'zh-CN';
  }, [i18n.language]);

  return (
    <I18nProvider locale={locale}>
      {children}
    </I18nProvider>
  )
}