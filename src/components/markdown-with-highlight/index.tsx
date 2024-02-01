// import SyntaxHighlighter from 'react-syntax-highlighter';
// import { githubGist } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import React from 'react';
import type { MDXComponents, MergeComponents } from '@mdx-js/react/lib';

// function code({ className, ...props }: React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>) {
//   const match = /language-(\w+)/.exec(className || '');

//   return match ? (
//     <SyntaxHighlighter
//       lineNumberStyle={{
//         color: '#999',
//       }}
//       showLineNumbers={match[1] !== 'bash'}
//       language={match[1]}
//       PreTag="div"
//       // @ts-ignore
//       style={githubGist}
//       {...props}
//     />
//   ) : (
//     <code className={className} {...props} />
//   );
// }

interface ExtraProps {
  components: Readonly<MDXComponents> | MergeComponents | null | undefined;
}

export default function MarkdownWithHighlight({ children }: React.PropsWithChildren) {
  // const childrenWithExtraProp = React.Children.map(children, (child) => {
  //   if (React.isValidElement<ExtraProps>(child)) {
  //     return React.cloneElement(child, { components: { code } });
  //   }

  //   return child;
  // });

  return children;
}
