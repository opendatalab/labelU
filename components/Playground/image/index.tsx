import { CodeOutlined, SettingOutlined } from '@ant-design/icons';
import type { AnnotatorRef } from '@labelu/image-annotator-react';
import { Annotator as ImageAnnotator } from '@labelu/image-annotator-react';
import type { Annotator, ToolName } from '@labelu/image';
import { TOOL_NAMES } from '@labelu/image';
import type { TabsProps } from 'antd';
import CodeMirror from '@uiw/react-codemirror';
import { json } from '@codemirror/lang-json';
import { Button, Drawer, Form, Tabs } from 'antd';
import { useCallback, useMemo, useRef, useState } from 'react';
import Modal from 'antd/es/modal/Modal';
import message from 'antd/es/message';
import { i18n, useTranslation } from '@labelu/i18n';

import lineTemplate from '../../constant/templates/line.template';
import rectTemplate from '../../constant/templates/rect.template';
import polygonTemplate from '../../constant/templates/polygon.template';
import pointTemplate from '../../constant/templates/point.template';
import cuboidTemplate from '../../constant/templates/cuboid.template';
import tagTemplate from '../../constant/templates/tag.template';
import textTemplate from '../../constant/templates/text.template';
import FancyForm from '../../FancyForm';
import _ from 'lodash';
import LocaleWrapper from '../../LocaleWrapper';
import { copy } from '../../utils';

const isBrowser = () => typeof window !== 'undefined';

const templateMapping: Record<ToolName | 'tag' | 'text', any> = {
  line: lineTemplate,
  rect: rectTemplate,
  polygon: polygonTemplate,
  point: pointTemplate,
  cuboid: cuboidTemplate,
  tag: tagTemplate,
  text: textTemplate,
};

const toolNameMapping = {
  line: i18n.t('line'),
  rect: i18n.t('rect'),
  polygon: i18n.t('polygon'),
  point: i18n.t('point'),
  cuboid: i18n.t('cuboid'),
  tag: i18n.t('tag'),
  text: i18n.t('textDescription'),
};

const presetSamples = [
  {
    url: '/labelU/assets/object-detect-1.jpg',
    name: 'rect',
    id: 'rect',
    meta: {
      rotate: 0,
    },
    data: {
      line: [],
      point: [],
      rect: [
        {
          "id": "7kj19v4gsju",
          "x": 114.6652719665272,
          "y": 245.16684100418414,
          "label": "human",
          "width": 31.942468619246863,
          "height": 176.09309623430963,
          "order": 1
        },
        {
          "id": "o56uojwkuxr",
          "x": 152.34100418410043,
          "y": 324.6134937238494,
          "label": "human",
          "width": 34.39958158995816,
          "height": 97.46548117154812,
          "order": 2
        },
        {
          "id": "7cewte1zxkv",
          "x": 171.17887029288704,
          "y": 259.9095188284519,
          "label": "human",
          "width": 45.04707112970711,
          "height": 108.11297071129708,
          "order": 3
        },
        {
          "id": "5379oak59hm",
          "x": 304.68200836820085,
          "y": 253.3572175732218,
          "label": "human",
          "width": 23.752092050209207,
          "height": 75.35146443514645,
          "order": 4
        },
        {
          "id": "to8lggihozs",
          "x": 330.0721757322176,
          "y": 290.21391213389126,
          "label": "human",
          "width": 31.123430962343097,
          "height": 101.56066945606695,
          "order": 5
        },
        {
          "id": "f20pd8jmqo",
          "x": 369.38598326359835,
          "y": 295.9471757322176,
          "label": "human",
          "width": 31.942468619246863,
          "height": 98.2845188284519,
          "order": 6
        },
        {
          "id": "yj4q0zug48",
          "x": 371.02405857740587,
          "y": 234.51935146443518,
          "label": "human",
          "width": 45.04707112970711,
          "height": 137.59832635983264,
          "order": 7
        },
        {
          "id": "45978c2ptgb",
          "x": 410.3378661087866,
          "y": 290.21391213389126,
          "label": "human",
          "width": 27.847280334728033,
          "height": 91.73221757322176,
          "order": 8
        },
        {
          "id": "prtoymdf3gj",
          "x": 453.74686192468624,
          "y": 251.71914225941427,
          "label": "human",
          "width": 27.02824267782427,
          "height": 94.18933054393305,
          "order": 9
        },
        {
          "id": "vk1wx5y6j3",
          "x": 497.1558577405858,
          "y": 333.62290794979083,
          "label": "bicycle",
          "width": 122.85564853556485,
          "height": 89.27510460251047,
          "order": 10
        }
      ],
      polygon: [],
      cuboid: [],
      text: [],
      tag: [],
    },
  },
  {
    url: '/labelU/assets/object-detect-3.jpg',
    name: 'cuboid',
    id: 'cuboid',
    meta: {
      width: 1280,
      height: 800,
      rotate: 0,
    },
    data: {
      line: [
        {
          "id": "njs5jfpdtt",
          "type": "line",
          "points": [
            {
              "id": "fq00ken2vg8",
              "x": 303.36401673640165,
              "y": 913.1924686192469
            },
            {
              "id": "jymr9d1g88h",
              "x": 483.6652719665272,
              "y": 697.1171548117155
            },
            {
              "id": "qa54p5ra60l",
              "x": 603.8661087866109,
              "y": 608.397489539749
            }
          ],
          "label": "lane",
          "order": 8
        },
        {
          "id": "3or3yxs7vnt",
          "type": "line",
          "points": [
            {
              "id": "hp7x2z4ntkn",
              "x": 4.292887029288703,
              "y": 684.2384937238494
            },
            {
              "id": "xuxp6xzk8m",
              "x": 220.36820083682008,
              "y": 639.8786610878661
            },
            {
              "id": "fxvwfehr3g4",
              "x": 475.0794979079498,
              "y": 599.8117154811716
            }
          ],
          "label": "lane",
          "order": 9
        },
        {
          "id": "yh49rs55v7i",
          "type": "line",
          "points": [
            {
              "id": "6g3gvpf0tq",
              "x": 749.8242677824268,
              "y": 677.0836820083682
            },
            {
              "id": "or5giko1fy8",
              "x": 922.9707112970711,
              "y": 827.334728033473
            },
            {
              "id": "p2t8sfcu1v",
              "x": 1024.5690376569037,
              "y": 914.6234309623433
            }
          ],
          "label": "lane",
          "order": 10
        },
        {
          "id": "d4hb1su1ke4",
          "type": "line",
          "points": [
            {
              "id": "vnzttg1auy8",
              "x": 1.4309623430962344,
              "y": 762.9414225941424
            },
            {
              "id": "1xi4xo7n3x8",
              "x": 210.35146443514645,
              "y": 691.3933054393306
            }
          ],
          "label": "lane",
          "order": 11
        }
      ],
      point: [],
      rect: [{
        "id": "3ji0whs65ay",
        "x": 460.76987447698747,
        "y": 389.4602510460251,
        "label": "traffic_sign",
        "width": 111.61506276150628,
        "height": 82.99581589958159,
        "order": 5
      },
      {
        "id": "oj3ahgdnvs8",
        "x": 708.326359832636,
        "y": 493.92050209205024,
        "label": "traffic_sign",
        "width": 58.66945606694561,
        "height": 35.77405857740586,
        "order": 6
      },
      {
        "id": "nfmd9ooe9ei",
        "x": 788.4602510460251,
        "y": 489.62761506276155,
        "label": "traffic_sign",
        "width": 70.11715481171548,
        "height": 35.77405857740586,
        "order": 7
      }],
      polygon: [],
      cuboid: [
        {
          "id": "jlw4a94flim",
          "direction": "back",
          "front": {
            "tl": {
              "x": 216.0753138075314,
              "y": 548.2970711297071
            },
            "tr": {
              "x": 366.326359832636,
              "y": 548.2970711297071
            },
            "br": {
              "x": 366.326359832636,
              "y": 715.7196652719666
            },
            "bl": {
              "x": 216.0753138075314,
              "y": 715.7196652719666
            }
          },
          "back": {
            "tl": {
              "x": 291.4026392018024,
              "y": 564.0376569037658
            },
            "tr": {
              "x": 412.11715481171547,
              "y": 564.0376569037658
            },
            "br": {
              "x": 412.11715481171547,
              "y": 698.5481171548117
            },
            "bl": {
              "x": 291.4026392018024,
              "y": 698.5481171548117
            }
          },
          "label": "car",
          "order": 1
        },
        {
          "id": "p63acg1pu0j",
          "direction": "back",
          "front": {
            "tl": {
              "x": 603.8661087866109,
              "y": 554.020920502092
            },
            "tr": {
              "x": 744.1004184100418,
              "y": 554.020920502092
            },
            "br": {
              "x": 744.1004184100418,
              "y": 675.652719665272
            },
            "bl": {
              "x": 603.8661087866109,
              "y": 675.652719665272
            }
          },
          "back": {
            "tl": {
              "x": 611.020920502092,
              "y": 565.468619246862
            },
            "tr": {
              "x": 723.2083682008368,
              "y": 565.468619246862
            },
            "br": {
              "x": 723.2083682008368,
              "y": 662.7740585774059
            },
            "bl": {
              "x": 611.020920502092,
              "y": 662.7740585774059
            }
          },
          "label": "car",
          "order": 2
        },
        {
          "id": "5pvle4wtefp",
          "direction": "back",
          "front": {
            "tl": {
              "x": 944.4351464435147,
              "y": 565.468619246862
            },
            "tr": {
              "x": 1110.4267782426778,
              "y": 565.468619246862
            },
            "br": {
              "x": 1110.4267782426778,
              "y": 721.4435146443515
            },
            "bl": {
              "x": 944.4351464435147,
              "y": 721.4435146443515
            }
          },
          "back": {
            "tl": {
              "x": 905.7991631799164,
              "y": 576.9163179916318
            },
            "tr": {
              "x": 1041.333614832444,
              "y": 576.9163179916318
            },
            "br": {
              "x": 1041.333614832444,
              "y": 704.2719665271967
            },
            "bl": {
              "x": 905.7991631799164,
              "y": 704.2719665271967
            }
          },
          "label": "car",
          "order": 3
        },
        {
          "id": "2m5vo69kbbc",
          "direction": "back",
          "front": {
            "tl": {
              "x": 422.1338912133891,
              "y": 568.3305439330544
            },
            "tr": {
              "x": 500.836820083682,
              "y": 568.3305439330544
            },
            "br": {
              "x": 500.836820083682,
              "y": 641.3096234309623
            },
            "bl": {
              "x": 422.1338912133891,
              "y": 641.3096234309623
            }
          },
          "back": {
            "tl": {
              "x": 450.33226679793256,
              "y": 574.0543933054394
            },
            "tr": {
              "x": 515.1464435146444,
              "y": 574.0543933054394
            },
            "br": {
              "x": 515.1464435146444,
              "y": 634.1548117154812
            },
            "bl": {
              "x": 450.33226679793256,
              "y": 634.1548117154812
            }
          },
          "label": "car",
          "order": 4
        },
      ],
      text: [],
      tag: [],
    },
  },
  {
    url: '/labelU/assets/segmentation.jpg',
    name: 'segmentation',
    id: 'segmentation',
    meta: {
      width: 1280,
      height: 800,
      rotate: 0,
    },
    data: {
      line: [],
      point: [],
      rect: [],
      polygon: [
        {
          "id": "0g7hofosgjmv",
          "type": "line",
          "points": [
            {
              "id": "rvx0pc79fa",
              "x": 332.94652807597754,
              "y": 297.43340203705515
            },
            {
              "id": "feeeqnl18t",
              "x": 332.7283708025357,
              "y": 314.2315120920781
            },
            {
              "id": "adx2y04zi7",
              "x": 336.00072990416356,
              "y": 314.01335481863623
            },
            {
              "id": "4xw18dalv06",
              "x": 336.43704445104726,
              "y": 336.4835539831475
            },
            {
              "id": "2eryc97br8f",
              "x": 447.04278208606866,
              "y": 345.64615946770544
            },
            {
              "id": "ohkur1vy80p",
              "x": 446.17015299230115,
              "y": 300.2694465917993
            },
            {
              "id": "wxxos6ao7c",
              "x": 450.9696130080221,
              "y": 299.39681749803185
            },
            {
              "id": "2kxowx22cpy",
              "x": 417.15523562453427,
              "y": 270.3819001302649
            },
            {
              "id": "rd7x8zindps",
              "x": 416.3654691908407,
              "y": 262.67845911563865
            },
            {
              "id": "ivokcs4vcv",
              "x": 412.1084005539947,
              "y": 252.17224187941412
            },
            {
              "id": "zh8ik0o2hsn",
              "x": 409.3071527016374,
              "y": 263.0611294408904
            },
            {
              "id": "526wx698ytv",
              "x": 409.53564232995984,
              "y": 270.7842528684304
            },
            {
              "id": "bigfrevxpr",
              "x": 407.51941731575266,
              "y": 271.2142667890905
            },
            {
              "id": "a281kv13xu",
              "x": 407.39319990040804,
              "y": 279.32826172194035
            },
            {
              "id": "zqlkv3habu",
              "x": 386.8313746161162,
              "y": 296.99708749017145
            }
          ],
          "label": "house",
          "order": 1
        },
        {
          "id": "ai6i00gl04v",
          "type": "line",
          "points": [
            {
              "id": "nae5db73qbp",
              "x": 508.472517990939,
              "y": 306.0409355580832
            },
            {
              "id": "qjbhmb7ehki",
              "x": 507.8765005783528,
              "y": 343.14301949157283
            },
            {
              "id": "kukynop4v3",
              "x": 509.51554846296483,
              "y": 343.14301949157283
            },
            {
              "id": "ny67kb5ckt",
              "x": 509.51554846296483,
              "y": 348.50717620484846
            },
            {
              "id": "e581f0dzfgd",
              "x": 574.0344333754186,
              "y": 354.16934162441714
            },
            {
              "id": "aqk2y03b8qu",
              "x": 574.1834377285653,
              "y": 342.3979977258401
            },
            {
              "id": "xpl8w80rn3",
              "x": 572.3953854908068,
              "y": 342.5470020789867
            },
            {
              "id": "nhcxw1e3msh",
              "x": 571.948372431367,
              "y": 306.1899399112297
            }
          ],
          "label": "house",
          "order": 2
        }
      ],
      cuboid: [],
      text: [],
      tag: [],
    },
  }, {
    url: '/labelU/assets/keypoints.jpg',
    name: 'keypoints',
    id: 'keypoints',
    meta: {
      rotate: 0,
    },
    data: {
      line: [],
      point: [
        {
          "order": 1,
          "id": "y8swn8rujmq",
          "label": "knee",
          "x": 611.1084243369736,
          "y": 1961.3104524180967
        },
        {
          "order": 2,
          "id": "27ddjwd2pk7",
          "label": "knee",
          "x": 929.8213728549142,
          "y": 1976.0202808112324
        },
        {
          "order": 3,
          "id": "i7otlw3b3ej",
          "label": "head",
          "x": 1204.4048361934479,
          "y": 799.2340093603744
        },
        {
          "order": 4,
          "id": "krjq69hoe9k",
          "label": "elbow",
          "x": 532.6560062402497,
          "y": 1024.7847113884554
        },
        {
          "order": 5,
          "id": "d368o0qel2",
          "label": "elbow",
          "x": 1385.8260530421217,
          "y": 1279.7550702028082
        },
        {
          "order": 6,
          "id": "b55hvy4w5ej",
          "label": "foot",
          "x": 895.4984399375976,
          "y": 2427.121684867395
        },
        {
          "order": 7,
          "id": "bcnjku16ru8",
          "label": "foot",
          "x": 1287.760530421217,
          "y": 2407.508580343214
        },
        {
          "order": 8,
          "id": "qzff2ge3i9",
          "label": "hand",
          "x": 601.301872074883,
          "y": 877.6864274570983
        },
        {
          "order": 9,
          "id": "1fsna2totm",
          "label": "hand",
          "x": 1537.8276131045243,
          "y": 1495.4992199687988
        }
      ],
      rect: [],
      polygon: [],
      cuboid: [],
      text: [],
      tag: [],
    },
  },
];

const defaultConfig = {
  point: { maxPointAmount: 100, labels: [{ color: '#1899fb', key: 'Knee', value: 'knee' }, { color: '#6b18fb', key: 'Head', value: 'head' }, { color: '#5cfb18', key: 'Hand', value: 'hand' }, { color: '#fb8d18', key: 'Elbow', value: 'elbow' }, { color: '#fb187e', key: 'Foot', value: 'foot' }] },
  line: {
    lineType: 'line',
    minPointAmount: 2,
    maxPointAmount: 100,
    edgeAdsorptive: false,
    labels: [{ color: '#ff0000', key: 'Lane', value: 'lane' }],
  },
  rect: { minWidth: 1, minHeight: 1, labels: [{ color: '#00ff1e', key: 'Human', value: 'human' }, { color: '#ff00ff', key: 'Bicycle', value: 'bicycle' }, { color: '#2e5fff', key: 'Traffic-sign', value: 'traffic_sign' }] },
  polygon: {
    lineType: 'line',
    minPointAmount: 2,
    maxPointAmount: 100,
    edgeAdsorptive: false,
    labels: [{ color: '#8400ff', key: 'House', value: 'house' }],
  },
  cuboid: {
    labels: [{ color: '#ff6d2e', key: 'Car', value: 'car' }],
  },
};

export default function ImagePage({
  lang
}: { lang: string }) {
  const annotatorRef = useRef<AnnotatorRef>(null);
  const [configOpen, setConfigOpen] = useState(false);
  const [resultOpen, setResultOpen] = useState(false);
  const [config, setConfig] = useState(defaultConfig);
  const [currentSample, updateSample] = useState(presetSamples[0]);
  const { t, i18n } = useTranslation();
  const [result, setResult] = useState<any>({});
  const [form] = Form.useForm();

  const showDrawer = useCallback(() => {
    setConfigOpen(true);
  }, [config, form]);

  const onClose = () => {
    form.validateFields().then(() => {
      setConfigOpen(false);
      form.submit();
    });
  };

  const onFinish = (values: any) => {
    setConfig(_.chain(values.tools).toPairs().map(([toolName, value]) => {
      const { config, tool } = value;
      return [toolName, {
        ...config,
        labels: config.attributes
      }]
    }).fromPairs().value());
  };

  const items: TabsProps['items'] = TOOL_NAMES.map((item) => ({
    key: item,
    label: toolNameMapping[item],
    forceRender: true,
    children: <FancyForm template={templateMapping[item]} name={['tools', item]} />,
  }));

  const onError = useCallback((err: any) => {
    message.error(err.message);
  }, []);

  const onLoad = useCallback((engine: Annotator) => {
    const updateSampleData = () => {
      setResult(() => ({
        ...annotatorRef.current?.getAnnotations(),
      }));
    };
    engine.on('add', updateSampleData);

    engine.on('change', updateSampleData);

    engine.on('labelChange', updateSampleData);
  }, []);

  const showResult = useCallback(() => {
    const imageAnnotations = annotatorRef.current?.getAnnotations();

    setResult(() => ({
      ...imageAnnotations,
    }));

    setResultOpen(true);
  }, []);

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

  const initialValues = useMemo(() => {
    // return undefined
    return {
      tools: _.chain(defaultConfig).toPairs().map(([toolName, value]) => {
        const { labels, ...values } = value
        return [toolName, {
          tool:toolName,
          config: {
            ...values,
            attributes: value.labels
          }
        }]
      }).fromPairs().value(),
    };
  }, []);

  return (
    <LocaleWrapper>
      <ImageAnnotator
        toolbarRight={toolbarRight}
        primaryColor={'#0d53de'}
        samples={presetSamples}
        ref={annotatorRef}
        offsetTop={180}
        editingSample={currentSample}
        config={config}
        onLoad={onLoad}
        onError={onError}
      />
      <Drawer width={480} title={t('annotationConfig')} onClose={onClose} open={configOpen}>
        <Form form={form} layout="vertical" onFinish={onFinish} initialValues={initialValues}>
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
    </LocaleWrapper>
  );
}
