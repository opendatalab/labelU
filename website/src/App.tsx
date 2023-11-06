import { Routes, Route } from 'react-router-dom';

import Layout from '@/layouts/main';
import RouterContainer from '@/components/router-container';

import Guide from './pages/guide';
import Api from './pages/api';
import NoMatch from './pages/no-match';
import ImageGuide from './pages/guide.image';
import TextGuide from './pages/guide.text';
import GettingStarted from './pages/getting-started';
import AudioGuide from './pages/guide.audio';
import PointCloudGuide from './pages/guide.point-cloud';
import VideoGuide from './pages/guide.video';
import Schema from './pages/schema';
import routes from './routes';

export default function App() {
  return (
    <RouterContainer routes={routes} />
    // <Routes>
    //   <Route path="/" element={<Layout />}>
    //     <Route path="guide" element={<Guide />}>
    //       <Route index element={<GettingStarted />} />
    //       <Route path="image" element={<ImageGuide />} />
    //       <Route path="point-cloud" element={<PointCloudGuide />} />
    //       <Route path="text" element={<TextGuide />} />
    //       <Route path="audio" element={<AudioGuide />} />
    //       <Route path="video" element={<VideoGuide />} />
    //     </Route>
    //     <Route path="schema" element={<Schema />} />
    //     <Route path="*" element={<NoMatch />} />
    //   </Route>
    // </Routes>
  );
}
