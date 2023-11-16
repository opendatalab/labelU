import MarkdownWithHighlight from '@/components/markdown-with-highlight';
import loadable from '@loadable/component';
import { useTranslation } from 'react-i18next';

const Markdown_zh_CN = loadable(() => import('./markdown_zh-CN.mdx'));
const Markdown_en_US = loadable(() => import('./markdown_en-US.mdx'));

const fileMap: Record<string, React.ElementType> = {
  'zh-CN': Markdown_zh_CN,
  'en-US': Markdown_en_US,
};

export default function Account() {
  const { i18n } = useTranslation();

  const Markdown = fileMap[i18n.language] || null;

  return (
    <MarkdownWithHighlight>
      <Markdown />
    </MarkdownWithHighlight>
  );
}
