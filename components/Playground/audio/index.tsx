import { Annotator } from '@labelu/audio-annotator-react';
import type { AudioAndVideoAnnotatorRef } from '@labelu/audio-annotator-react';
import CodeMirror from '@uiw/react-codemirror';
import { json } from '@codemirror/lang-json';
import type { TabsProps } from 'antd';
import { Button, Drawer, Form, Modal, Tabs } from 'antd';
import { useCallback, useMemo, useRef, useState } from 'react';
import { CodeOutlined, SettingOutlined } from '@ant-design/icons';
import message from 'antd/es/message';
import { useTranslation } from '@labelu/i18n';

import './index.css'
import FancyForm from '../../FancyForm';
import videoSegmentTemplate from '../../constant/templates/audioSegment.template';
import videoFrameTemplate from '../../constant/templates/audioFrame.template';
import LocaleWrapper from '../../LocaleWrapper';
import { copy } from '../../utils';

const isBrowser = () => typeof window !== 'undefined';

const defaultConfig = {
  segment: [
    {
      color: '#e600ff',
      key: '老人说话',
      value: 'the_old_man_is_taking',
    },
  ],
  frame: [
    {
      color: '#40ff00',
      key: '妈妈开始生气',
      value: 'mon_is_getting_upset',
    },
  ],
};

const defaultSamples = [
  {
    id: 'audio-segment',
    url: '/assets/audio-segment.mp3',
    name: 'audio-segment',
    data: {
      segment: [
        { id: '1', start: 5.496299, end: 8.477484, label: 'the_old_man_is_taking', type: 'segment', order: 1 },
        {
          id: '4rsakqmt9zt',
          type: 'segment',
          start: 9.952124,
          end: 19.653833,
          order: 2,
          label: 'the_old_man_is_taking',
        },
        {
          id: 'go8t24wjfbe',
          type: 'segment',
          start: 27.304808,
          end: 36.858098,
          order: 3,
          label: 'the_old_man_is_taking',
        },
      ],
    },
  },
  {
    id: 'audio-frame',
    url: '/assets/audio-frame.m4a',
    name: 'audio-frame',
    data: {
      frame: [{ id: 'wo2tiebj64e', type: 'frame', time: 5.2, label: 'mon_is_getting_upset', order: 3 }],
    },
  },
];

export default function AudioPage() {
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
      <div className="audio-wrapper">
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
                        color: '#e600ff',
                        key: '老人说话',
                        value: 'the_old_man_is_taking',
                      },
                    ]
                  },
                },
                frame: {
                  config: {
                    attributes: [
                      {
                        color: '#40ff00',
                        key: '妈妈开始生气',
                        value: 'mon_is_getting_upset',
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
          okText={t('copied')}
          onCancel={() => setResultOpen(false)}
        >
          <CodeMirror value={JSON.stringify(result, null, 2)} extensions={[json()]} />
        </Modal>
      </div>
    </LocaleWrapper>
  );
}
