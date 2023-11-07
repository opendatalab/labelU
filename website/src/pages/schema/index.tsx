import { FlexLayout } from '@labelu/components-react';
import { Outlet } from 'react-router-dom';
import { MDXProvider } from '@mdx-js/react';
import { Menu } from '@/components/menu';

export default function Schema() {
  return (
    <FlexLayout full>
      <FlexLayout.Item className='lg:w-[280px] max-h-[calc(100vh-56px)] overflow-auto'>
        <Menu path='/schema' />
      </FlexLayout.Item>
      <FlexLayout.Content className="max-h-[calc(100vh-56px)] overflow-auto">
        <FlexLayout.Content className="prose prose-slate py-2 px-6">
          <MDXProvider>
            <Outlet />
          </MDXProvider>
        </FlexLayout.Content>
      </FlexLayout.Content>
    </FlexLayout>
  );
}
