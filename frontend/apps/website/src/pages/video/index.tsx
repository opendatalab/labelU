import { Annotator } from '@labelu/video-annotator-react';
import type { VideoAnnotationType } from '@labelu/video-react';
import type { AudioAndVideoAnnotatorRef } from '@labelu/audio-annotator-react';
import CodeMirror from '@uiw/react-codemirror';
import { json } from '@codemirror/lang-json';
import type { TabsProps } from 'antd';
import { Button, Drawer, Form, Modal, Tabs } from 'antd';
import { useCallback, useMemo, useRef, useState } from 'react';
import { CodeOutlined, SettingOutlined } from '@ant-design/icons';
import message from 'antd/es/message';
import { useTranslation } from '@labelu/i18n';

import FancyForm from '@/components/FancyForm';
import videoSegmentTemplate from '@/constant/templates/videoSegment.template';
import videoFrameTemplate from '@/constant/templates/videoFrame.template';

const defaultConfig = {
  segment: [
    {
      color: '#a600ff',
      key: '游艇行驶',
      value: 'ship',
    },
  ],
  frame: [
    {
      color: '#ff6600',
      key: '汽车出现',
      value: 'car',
    },
  ],
};

const defaultSamples = [
  {
    id: 1,
    name: 'video-segment',
    url: import.meta.env.BASE_URL + 'video-segment.mp4',
    data: {
      segment: [{ id: 'b2tk865g3w', type: 'segment', start: 7.457498, end: 11.625751, order: 1, label: 'ship' }],
    },
  },
  {
    id: 2,
    name: 'video-frame',
    url: import.meta.env.BASE_URL + 'video-frame.mp4',
    data: { frame: [{ id: 'eb7wjsga4ei', type: 'frame', time: 12.00722, label: 'car', order: 1 }] },
  },
];

export default function VideoPage() {
  const annotatorRef = useRef<AudioAndVideoAnnotatorRef>(null);
  const [editingType, setEditingType] = useState<VideoAnnotationType>('segment');
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
      segment: values.tools.segment?.labels ?? [],
      frame: values.tools.frame?.labels ?? [],
    });
  };

  const onOk = () => {
    setResultOpen(false);
    // 复制到剪切板
    navigator.clipboard.writeText(JSON.stringify(currentSample.data, null, 2));
    message.success(t('copied'));
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
    <>
      <Annotator
        toolbarRight={toolbarRight}
        primaryColor={'#1890ff'}
        samples={defaultSamples}
        offsetTop={156}
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
                labels: [
                  {
                    color: '#a600ff',
                    key: '游艇行驶',
                    value: 'ship',
                  },
                ],
              },
              frame: {
                labels: [
                  {
                    color: '#ff6600',
                    key: '汽车出现',
                    value: 'car',
                  },
                ],
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
    </>
  );
}
