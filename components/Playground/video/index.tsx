import { Annotator } from '@labelu/video-annotator-react';
import type { AudioAndVideoAnnotatorRef } from '@labelu/audio-annotator-react';
import CodeMirror from '@uiw/react-codemirror';
import { json } from '@codemirror/lang-json';
import type { TabsProps } from 'antd';
import { Button, Drawer, Form, Modal, Tabs } from 'antd';
import { useCallback, useMemo, useRef, useState } from 'react';
import { CodeOutlined, SettingOutlined } from '@ant-design/icons';
import message from 'antd/es/message';
import { useTranslation } from '@labelu/i18n';
import '@labelu/video-react/dist/style.css';

import './index.css'
import FancyForm from '../../FancyForm';
import videoSegmentTemplate from '../../constant/templates/videoSegment.template';
import videoFrameTemplate from '../../constant/templates/videoFrame.template';
import LocaleWrapper from '../../LocaleWrapper';
import { copy } from '../../utils';

const isBrowser = () => typeof window !== 'undefined';

const defaultConfig = {
  segment: [
    {
      color: '#a600ff',
      key: 'Ship Appears',
      value: 'ship',
    },
  ],
  frame: [
    {
      color: '#ff6600',
      key: 'Car Appears',
      value: 'car',
    },
  ],
};

const defaultSamples = [
  {
    id: 1,
    name: 'video-segment',
    url: '/labelU/assets/video-segment.mp4',
    data: {
      segment: [{ id: 'b2tk865g3w', type: 'segment', start: 7.457498, end: 11.625751, order: 1, label: 'ship' }],
    },
  },
  {
    id: 2,
    name: 'video-frame',
    url: '/labelU/assets/video-frame.mp4',
    data: { frame: [{ id: 'eb7wjsga4ei', type: 'frame', time: 12.00722, label: 'car', order: 1 }] },
  },
];

export default function VideoPage() {
  const annotatorRef = useRef<AudioAndVideoAnnotatorRef>(null);
  const [editingType, setEditingType] = useState<any>('segment');
  const { t } = useTranslation();

  const [configOpen, setConfigOpen] = useState(false);
  const [resultOpen, setResultOpen] = useState(false);
  const [config, setConfig] = useState(defaultConfig);
  const [currentSample, updateSample] = useState(defaultSamples[0]);
  const [form] = Form.useForm();
  const [result, setResult] = useState<any>({});
  const showDrawer = useCallback(() => {
    setConfigOpen(true);
  }, []);

  const items: TabsProps['items'] = [
    {
      key: 'segment',
      label: t('segment'),
      forceRender: true,
      children: <FancyForm template={videoSegmentTemplate} name={['tools', 'segment']} />,
    },
    {
      key: 'frame',
      label: t('timestamp'),
      forceRender: true,
      children: <FancyForm template={videoFrameTemplate} name={['tools', 'frame']} />,
    },
  ];

  const showResult = useCallback(() => {
    const annotations = annotatorRef.current?.getAnnotations();

    setResult(() => ({
      ...annotations,
    }));

    setResultOpen(true);
  }, []);

  const onClose = () => {
    form.validateFields().then(() => {
      setConfigOpen(false);
      form.submit();
    });
  };

  const onFinish = (values: any) => {
    setConfig({
      segment: values.tools.segment?.config.attributes ?? [],
      frame: values.tools.frame?.config.attributes ?? [],
    });
  };

  const onOk = () => {
    setResultOpen(false);
    // 复制到剪切板
    copy(currentSample.data, t('copied'));
  };

  const toolbarRight = useMemo(() => {
    return (
      <div className="flex items-center gap-2">
        <Button type="primary" icon={<CodeOutlined rev={undefined} />} onClick={showResult}>
          {t('annotationResult')}
        </Button>
        <Button icon={<SettingOutlined rev={undefined} />} onClick={showDrawer} />
      </div>
    );
  }, [t, showDrawer, showResult]);

  return (
    <LocaleWrapper>
      <div className="video-wrapper">
        <Annotator
          toolbarRight={toolbarRight}
          primaryColor={'#1890ff'}
          samples={defaultSamples}
          offsetTop={180}
          ref={annotatorRef}
          type={editingType}
          config={config}
        />
        <Drawer width={480} title={t('annotationConfig')} onClose={onClose} open={configOpen}>
          <Form
            form={form}
            layout="vertical"
            onFinish={onFinish}
            initialValues={{
              tools: {
                segment: {
                  config: {
                    attributes: [
                      {
                        color: '#a600ff',
                        key: 'Ship Appears',
                        value: 'ship',
                      },
                    ],
                  }
                },
                frame: {
                  config: {
                    attributes: [
                      {
                        color: '#ff6600',
                        key: 'Car Appears',
                        value: 'car',
                      },
                    ],
                  }
                },
              },
            }}
          >
            <Tabs items={items} />
          </Form>
        </Drawer>
        <Modal
          title={t('annotationResult')}
          open={resultOpen}
          onOk={onOk}
          width={800}
          okText={t('copy')}
          onCancel={() => setResultOpen(false)}
        >
          <CodeMirror value={JSON.stringify(result, null, 2)} extensions={[json()]} />
        </Modal>
      </div>
    </LocaleWrapper>
  );
}
