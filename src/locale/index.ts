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

const validEnLangs = ['en-US', 'en', 'en-GB', 'en-AU', 'en-CA', 'en-NZ'];
const validZhLangs = ['zh-CN', 'zh', 'zh-TW', 'zh-HK'];

let initialLang = localStorage.getItem('i18nextLng') || navigator.language;

if (validEnLangs.includes(initialLang)) {
  initialLang = 'en-US';
} else if (validZhLangs.includes(initialLang)) {
  initialLang = 'zh-CN';
} else {
  initialLang = 'en-US';
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next) // passes i18n down to react-i18next
  .init({
    resources,
    lng: initialLang,
    interpolation: {
      escapeValue: false, // react already safes from xss
    },
  });

export default i18n;
