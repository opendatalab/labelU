import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import enUS from './resources/en-US.json';
import zhCN from './resources/zh-CN.json';

const resources = {
  'en-US': {
    translation: enUS,
  },
  'zh-CN': {
    translation: zhCN,
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next) // passes i18n down to react-i18next
  .init({
    resources,
    lng: localStorage.getItem('i18nextLng') || navigator.language || 'zh-CN',
    interpolation: {
      escapeValue: false, // react already safes from xss
    },
  });

export default i18n;
