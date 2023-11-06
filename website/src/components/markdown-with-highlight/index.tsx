import SyntaxHighlighter from 'react-syntax-highlighter';
import 'react-syntax-highlighter/dist/esm/styles/hljs/night-owl';
import React from 'react';
import type { MDXComponents, MergeComponents } from '@mdx-js/react/lib';

function code({ className, ...props }: React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>) {
  const match = /language-(\w+)/.exec(className || '');

  return match ? (
    <SyntaxHighlighter language={match[1]} PreTag="div" {...props} />
  ) : (
    <code className={className} {...props} />
  );
}

function getAnchor(text: string) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fa5 ]/g, '')
    .replace(/[ ]/g, '-');
}

function h2({ children }: React.PropsWithChildren) {
  const anchor = getAnchor(children as string);
  const link = `#${anchor}`;

  return (
    <h2 id={anchor}>
      <a href={link} className="anchor-link">
        §
      </a>
      &nbsp;
      {children as string}
    </h2>
  );
}

interface ExtraProps {
  components: Readonly<MDXComponents> | MergeComponents | null | undefined;
}

export default function MarkdownWithHighlight({ children }: React.PropsWithChildren) {
  const childrenWithExtraProp = React.Children.map(children, (child) => {
    if (React.isValidElement<ExtraProps>(child)) {
      return React.cloneElement(child, { components: { code, h2 } });
    }

    return child;
  });

  return childrenWithExtraProp;
}
