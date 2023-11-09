import { useTranslation } from 'react-i18next';
import loadable from '@loadable/component';

const Markdown_zh_CN = loadable(() => import('./getting-started-zh-CN.mdx'));
const Markdown_en_US = loadable(() => import('./getting-started-en-US.mdx'));

const fileMap: Record<string, React.ElementType> = {
  'zh-CN': Markdown_zh_CN,
  'en-US': Markdown_en_US,
};

export default function GettingStarted() {
  const { i18n } = useTranslation();

  const Markdown = fileMap[i18n.language] || null;

  return <Markdown />;
}
