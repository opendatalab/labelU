import { useEffect } from 'react';

import RouterContainer from '@/components/router-container';

import routes from './routes';

export default function App() {
  useEffect(() => {
    document.dispatchEvent(new Event('custom-render-trigger'));
  }, []);

  return <RouterContainer routes={routes} />;
}
