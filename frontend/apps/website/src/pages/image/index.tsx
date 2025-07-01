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

import lineTemplate from '@/constant/templates/line.template';
import rectTemplate from '@/constant/templates/rect.template';
import polygonTemplate from '@/constant/templates/polygon.template';
import pointTemplate from '@/constant/templates/point.template';
import cuboidTemplate from '@/constant/templates/cuboid.template';
import tagTemplate from '@/constant/templates/tag.template';
import textTemplate from '@/constant/templates/text.template';
import FancyForm from '@/components/FancyForm';
import { add } from '@/components/FancyInput';
import { FancyAttributeList } from '@/components/CustomFancy/ListAttribute.fancy';
import { FancyCategoryAttribute } from '@/components/CustomFancy/CategoryAttribute.fancy';

add('list-attribute', FancyAttributeList);
add('category-attribute', FancyCategoryAttribute);

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
    url: import.meta.env.BASE_URL + 'cuboid.jpg',
    name: 'cuboid',
    id: 'cuboid',
    meta: {
      width: 1280,
      height: 800,
      rotate: 0,
    },
    data: {
      line: [],
      point: [],
      rect: [],
      polygon: [],
      cuboid: [
        {
          id: '8wtj5rpk9vs',
          direction: 'front',
          front: {
            tl: {
              x: 93.6936936936937,
              y: 283.8243243243243,
            },
            tr: {
              x: 573.6936936936937,
              y: 283.8243243243243,
            },
            br: {
              x: 573.6936936936937,
              y: 667.2477477477478,
            },
            bl: {
              x: 93.6936936936937,
              y: 667.2477477477478,
            },
          },
          back: {
            tl: {
              x: 768.7488992752151,
              y: 204.54504504504504,
            },
            tr: {
              x: 1181.981981981982,
              y: 204.54504504504504,
            },
            br: {
              x: 1181.981981981982,
              y: 534.6351351351351,
            },
            bl: {
              x: 768.7488992752151,
              y: 534.6351351351351,
            },
          },
          label: 'car',
          order: 1,
        },
      ],
      text: [],
      tag: [],
    },
  },
  {
    url: import.meta.env.BASE_URL + 'polygon-spline.jpg',
    name: 'polygon-spline',
    id: 'polygon-spline',
    meta: {
      width: 1700,
      height: 957,
      rotate: 0,
    },
    data: {
      line: [],
      point: [],
      rect: [],
      polygon: [
        {
          id: 'b2c7aeff-750c-47aa-ad25-fffefd77bc9f',
          type: 'spline',
          points: [
            {
              id: '27f04d0c-9d00-4ee0-859f-a5738c4c2483',
              x: 568.5025472472379,
              y: 237.5099467962562,
            },
            {
              id: 'a83b2c22-0857-4f04-b7a3-c0f2a6c9ac6e',
              x: 625.8424809655583,
              y: 279.6572485037396,
            },
            {
              id: '7872ce10-633e-4d67-94de-397b9cd5e728',
              x: 575.3637358972933,
              y: 363.95185191870627,
            },
            {
              id: 'e774af8e-3a2b-4744-ad18-b3450f1cb558',
              x: 578.3042453187456,
              y: 383.0651631581465,
            },
            {
              id: '391c3d53-d038-4398-a98f-da0d933bf1c5',
              x: 564.0917831150593,
              y: 381.5949084474202,
            },
            {
              id: 'a044e475-70b3-40fc-849a-771a5be3eadd',
              x: 565.5620378257856,
              y: 363.95185191870627,
            },
            {
              id: '0e057d7a-df32-436d-b727-a082cd66ca38',
              x: 558.2107642721547,
              y: 350.2294746185955,
            },
            {
              id: '65d1cc5d-70d1-4456-bc21-6fc880b10040',
              x: 515.0832927575207,
              y: 278.67707869658875,
            },
          ],
          controlPoints: [
            {
              x: 591.0464528117058,
              y: 237.5099467962562,
            },
            {
              x: 624.3722262548322,
              y: 256.62325803569644,
            },
            {
              x: 625.8424809655583,
              y: 320.82438040407214,
            },
            {
              x: 575.3637358972933,
              y: 363.95185191870627,
            },
            {
              x: 575.3637358972933,
              y: 363.95185191870627,
            },
            {
              x: 578.3042453187456,
              y: 383.0651631581465,
            },
            {
              x: 578.3042453187456,
              y: 383.0651631581465,
            },
            {
              x: 564.0917831150593,
              y: 381.5949084474202,
            },
            {
              x: 564.0917831150593,
              y: 381.5949084474202,
            },
            {
              x: 565.5620378257856,
              y: 363.95185191870627,
            },
            {
              x: 565.5620378257856,
              y: 363.95185191870627,
            },
            {
              x: 562.1314435007578,
              y: 353.66006894362323,
            },
            {
              x: 554.2900850435517,
              y: 346.79888029356766,
            },
            {
              x: 515.0832927575207,
              y: 311.02268233256433,
            },
            {
              x: 513.6130380467944,
              y: 260.0538523607241,
            },
            {
              x: 545.9586416827701,
              y: 237.5099467962562,
            },
          ],
          label: 'balloon',
          order: 5,
          visible: true,
          tool: 'polygon',
        },
        {
          id: '3d243337-cd33-4d09-a072-9fbe9d5f3158',
          type: 'spline',
          points: [
            {
              id: 'edcef7c5-c592-404b-9435-d30df7473dfd',
              x: 283.92070471593144,
              y: 237.6935217759191,
            },
            {
              id: '67c9996f-cbcf-4302-bc8d-ff5935d46189',
              x: 292.69642243743016,
              y: 244.79152875654304,
            },
            {
              id: '95de3b5d-6e26-4a0f-b6f4-a5a56d36101f',
              x: 285.59841545680615,
              y: 255.63212123604148,
            },
            {
              id: '438c37da-9f67-46b0-b61c-4d6fa0075077',
              x: 285.4693607844312,
              y: 258.987542717791,
            },
            {
              id: '06a3d45d-d571-4001-9219-69d57e02faf2',
              x: 281.85582995793175,
              y: 258.987542717791,
            },
            {
              id: 'fb43c266-b080-47f6-95a3-9ab0c8fd7056',
              x: 280.56528323418195,
              y: 254.47062918466665,
            },
            {
              id: 'aeae86d8-0cf7-473d-b9e5-98cc35d56bee',
              x: 275.2740416668077,
              y: 245.5658567907929,
            },
          ],
          controlPoints: [
            {
              x: 288.3085635766808,
              y: 237.82257644829403,
            },
            {
              x: 292.69642243743016,
              y: 240.53272456816867,
            },
            {
              x: 292.69642243743016,
              y: 249.05033294491741,
            },
            {
              x: 285.72747012918114,
              y: 253.18008246091688,
            },
            {
              x: 285.4693607844312,
              y: 258.0841600111661,
            },
            {
              x: 285.4693607844312,
              y: 258.987542717791,
            },
            {
              x: 285.4693607844312,
              y: 258.987542717791,
            },
            {
              x: 281.85582995793175,
              y: 258.987542717791,
            },
            {
              x: 281.85582995793175,
              y: 258.987542717791,
            },
            {
              x: 280.56528323418195,
              y: 254.47062918466665,
            },
            {
              x: 280.56528323418195,
              y: 254.47062918466665,
            },
            {
              x: 275.14498699443266,
              y: 250.21182499629217,
            },
            {
              x: 275.6612056839327,
              y: 240.91988858529365,
            },
            {
              x: 279.5328458551821,
              y: 237.56446710354416,
            },
          ],
          label: 'balloon',
          order: 6,
          visible: true,
          tool: 'polygon',
        },
        {
          id: 'b0f5a766-1365-4959-af84-0162778e1125',
          type: 'spline',
          points: [
            {
              id: '2d7486d5-0c78-4d48-b6ce-dc928dad67eb',
              x: 320.0295011345161,
              y: 141.45330569548014,
            },
            {
              id: '6793b0c2-4867-41d3-9056-d25618dd2277',
              x: 368.0578216849042,
              y: 176.73941875290805,
            },
            {
              id: 'a8f62edd-9b46-40a5-b09d-ec1ffafb75b7',
              x: 335.71221804892855,
              y: 242.90088073558547,
            },
            {
              id: '0eaf481e-849a-438f-b662-629af10c81c3',
              x: 322.9700105559685,
              y: 256.6232580356964,
            },
            {
              id: 'bda51d34-19ab-413a-aa3e-426eda365d08',
              x: 323.9501803631193,
              y: 272.30597495010875,
            },
            {
              id: '02f802ab-87e8-451b-b547-e0433325de47',
              x: 314.14848229161146,
              y: 271.81589004653335,
            },
            {
              id: '176d6c1c-8680-4497-ba59-76591b7c57b0',
              x: 312.18814267730994,
              y: 254.1728335178194,
            },
            {
              id: 'f8817f5c-43a2-478f-94e2-956c7886af52',
              x: 273.47143529485425,
              y: 180.6600979815112,
            },
          ],
          controlPoints: [
            {
              x: 334.7320482417778,
              y: 141.45330569548014,
            },
            {
              x: 368.0578216849042,
              y: 151.25500376698787,
            },
            {
              x: 368.0578216849042,
              y: 215.45612613536372,
            },
            {
              x: 342.57340669898394,
              y: 233.58926756765314,
            },
            {
              x: 328.85102939887315,
              y: 252.21249390351784,
            },
            {
              x: 322.9700105559685,
              y: 253.19266371066865,
            },
            {
              x: 322.9700105559685,
              y: 260.0538523607241,
            },
            {
              x: 323.9501803631193,
              y: 271.81589004653335,
            },
            {
              x: 323.9501803631193,
              y: 271.81589004653335,
            },
            {
              x: 314.14848229161146,
              y: 271.81589004653335,
            },
            {
              x: 314.14848229161146,
              y: 271.81589004653335,
            },
            {
              x: 313.1683124844607,
              y: 256.6232580356964,
            },
            {
              x: 311.20797287015915,
              y: 252.7025788070932,
            },
            {
              x: 272.98135039127885,
              y: 206.63459787100666,
            },
            {
              x: 271.5110956805527,
              y: 152.2351735741387,
            },
            {
              x: 305.3269540272545,
              y: 141.45330569548014,
            },
          ],
          label: 'balloon',
          order: 2,
          visible: true,
          tool: 'polygon',
        },
      ],
      cuboid: [],
      text: [],
      tag: [],
    },
  },
  {
    url: import.meta.env.BASE_URL + 'point.jpg',
    name: 'point',
    id: 'point',
    meta: {
      width: 1280,
      height: 800,
      rotate: 0,
    },
    data: {
      line: [],
      point: [
        {
          order: 1,
          id: '85fff0c3-085f-4b08-9dc9-ccdec5557cb5',
          label: 'eye',
          x: 472.63796223724546,
          y: 327.0824921433627,
          tool: 'point',
        },
      ],
      rect: [],
      polygon: [],
      cuboid: [],
      text: [],
      tag: [],
    },
  },
  {
    url: import.meta.env.BASE_URL + 'rect.jpg',
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
          id: '30425dfe-6665-4129-bbb2-53792cdec083',
          x: 1164.5470886095477,
          y: 267.0205130562299,
          label: 'helmet',
          width: 110.1435772833186,
          height: 90.20379174064887,
          order: 1,
          tool: 'rect',
        },
        {
          id: '57168c96-e75e-4248-9d41-2dea4d3e2a0d',
          x: 503.68562490963666,
          y: 191.05942527463094,
          label: 'helmet',
          width: 37.98054389079948,
          height: 26.586380723559724,
          order: 5,
          tool: 'rect',
        },
        {
          id: 'cb13af2a-74e2-4ce3-8ad4-5f876a601847',
          x: 416.33037396079783,
          y: 179.6652621073912,
          label: 'helmet',
          width: 27.53589432082965,
          height: 21.83881273720971,
          order: 6,
          tool: 'rect',
        },
        {
          id: 'f59b2867-b555-4902-8492-6cb03e81ff44',
          x: 535.9690872168162,
          y: 170.1701261346913,
          label: 'helmet',
          width: 30.384435112639686,
          height: 35.13200309898944,
          order: 7,
          tool: 'rect',
        },
      ],
      polygon: [],
      cuboid: [],
      text: [],
      tag: [],
    },
  },
  {
    url: import.meta.env.BASE_URL + 'line.jpg',
    name: 'line',
    id: 'line',
    meta: {
      rotate: 0,
    },
    data: {
      line: [
        {
          id: '72987253-b05d-4e72-b599-077ad12e6f7a',
          type: 'line',
          points: [
            {
              id: '6d45f79a-2bfa-4cb4-a9b6-242671b1cb06',
              x: 579.3083757026459,
              y: 351.49643431684234,
            },
            {
              id: '5ce523df-7cfc-40a8-a943-b97beb742910',
              x: 438.4471653202616,
              y: 534.7180811547987,
            },
          ],
          label: 'lane',
          order: 1,
          visible: true,
          tool: 'line',
        },
        {
          id: 'a3236966-3627-4867-a972-23cb7b53293f',
          type: 'line',
          points: [
            {
              id: 'a808b5bf-d41c-4cd6-bae6-c4d311caa53c',
              x: 125.95275080625302,
              y: 563.5605187039135,
            },
            {
              id: 'cc8bf9c4-3915-477a-b782-352a113cdb48',
              x: 427.3045289506425,
              y: 418.35471141321773,
            },
            {
              id: '6d79a0b2-cd5e-46d4-b847-4126d26b95ea',
              x: 511.84215648289705,
              y: 368.6266952177739,
            },
            {
              id: '1c6e7e0b-5ffb-4ede-9e4a-3ea8d00b7277',
              x: 541.6789662001634,
              y: 357.68653165477616,
            },
          ],
          label: 'lane',
          order: 2,
          visible: true,
          tool: 'line',
        },
      ],
      point: [],
      rect: [],
      polygon: [],
      cuboid: [],
      text: [],
      tag: [],
    },
  },
];

const defaultConfig = {
  point: { maxPointAmount: 100, labels: [{ color: '#1899fb', key: '眼睛', value: 'eye' }] },
  line: {
    lineType: 'line',
    minPointAmount: 2,
    maxPointAmount: 100,
    edgeAdsorptive: false,
    labels: [{ color: '#ff0000', key: '车道线', value: 'lane' }],
  },
  rect: { minWidth: 1, minHeight: 1, labels: [{ color: '#00ff1e', key: '头盔', value: 'helmet' }] },
  polygon: {
    lineType: 'line',
    minPointAmount: 2,
    maxPointAmount: 100,
    edgeAdsorptive: false,
    labels: [{ color: '#8400ff', key: '热气球', value: 'balloon' }],
  },
  cuboid: {
    labels: [{ color: '#ff6d2e', key: '汽车', value: 'car' }],
  },
};

export default function ImagePage() {
  const annotatorRef = useRef<AnnotatorRef>(null);
  const [configOpen, setConfigOpen] = useState(false);
  const [resultOpen, setResultOpen] = useState(false);
  const [config, setConfig] = useState(defaultConfig);
  const [currentSample, updateSample] = useState(presetSamples[0]);
  const { t } = useTranslation();
  const [result, setResult] = useState<any>({});
  const [form] = Form.useForm();

  const showDrawer = useCallback(() => {
    setConfigOpen(true);
  }, []);

  const onClose = () => {
    form.validateFields().then(() => {
      setConfigOpen(false);
      form.submit();
    });
  };

  const onFinish = (values: any) => {
    setConfig(values.tools);
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

  const initialValues = useMemo(() => {
    return {
      tools: defaultConfig,
    };
  }, []);

  return (
    <>
      <ImageAnnotator
        toolbarRight={toolbarRight}
        primaryColor={'#0d53de'}
        samples={presetSamples}
        ref={annotatorRef}
        offsetTop={148}
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
    </>
  );
}
