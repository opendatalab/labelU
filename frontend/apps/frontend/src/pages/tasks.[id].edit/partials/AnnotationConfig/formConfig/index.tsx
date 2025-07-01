// import { ImageToolName, TOOL_NAME, EVideoToolName, EAudioToolName } from '@labelu/annotation';
import type { FormProps, SelectProps, TabsProps } from 'antd';
import { Popconfirm, Button, Form, Tabs, Select } from 'antd';
import React, { useContext, useEffect, useCallback, useMemo, useState } from 'react';
import _, { cloneDeep, find } from 'lodash-es';
import { PlusOutlined } from '@ant-design/icons';
import { FlexLayout } from '@labelu/components-react';
import { createGlobalStyle } from 'styled-components';
import { useTranslation } from '@labelu/i18n';

import { MediaType, TaskStatus } from '@/api/types';
import FancyForm from '@/components/FancyForm';
import FancyInput, { add } from '@/components/FancyInput';
import { EAudioToolName, EGlobalToolName, EVideoToolName, ImageToolName } from '@/enums';
import { TOOL_NAME } from '@/constants/toolName';

import { TaskCreationContext } from '../../../taskCreation.context';
import { FancyAttributeList } from './customFancy/ListAttribute.fancy';
import { FancyCategoryAttribute } from './customFancy/CategoryAttribute.fancy';
import lineTemplate from './templates/line.template';
import rectTemplate from './templates/rect.template';
import polygonTemplate from './templates/polygon.template';
import cuboidTemplate from './templates/cuboid.template';
import pointTemplate from './templates/point.template';
import tagTemplate from './templates/tag.template';
import textTemplate from './templates/text.template';
import videoSegmentTemplate from './templates/videoSegment.template';
import videoFrameTemplate from './templates/videoFrame.template';
import audioSegmentTemplate from './templates/audioSegment.template';
import audioFrameTemplate from './templates/audioFrame.template';
import { AttributeBox, AttributeFormItem, ConfigForm, TabForm } from './style';

const GlobalStyle = createGlobalStyle`
  .labelu-tool-select-popup .rc-virtual-list-holder {
    max-height: none !important;
  }
`;

// 注册fancyInput自定义输入组件
add('list-attribute', FancyAttributeList);
add('category-attribute', FancyCategoryAttribute);

const globalTools = [EGlobalToolName.Tag, EGlobalToolName.Text];
const graphicTools = [
  ImageToolName.Rect,
  ImageToolName.Point,
  ImageToolName.Polygon,
  ImageToolName.Line,
  ImageToolName.Cuboid,
];
const videoAnnotationTools = [EVideoToolName.VideoSegmentTool, EVideoToolName.VideoFrameTool];
const audioAnnotationTools = [EAudioToolName.AudioSegmentTool, EAudioToolName.AudioFrameTool];

const toolMapping = {
  [MediaType.IMAGE]: graphicTools.map((item) => {
    return {
      label: TOOL_NAME[item],
      value: item,
    };
  }),
  [MediaType.VIDEO]: videoAnnotationTools.map((item) => {
    return {
      label: TOOL_NAME[item],
      value: item,
    };
  }),
  [MediaType.AUDIO]: audioAnnotationTools.map((item) => {
    return {
      label: TOOL_NAME[item],
      value: item,
    };
  }),
};

const getDefaultActiveTool = (mediaType?: MediaType) => {
  switch (mediaType) {
    case MediaType.IMAGE:
      return ImageToolName.Rect;
    case MediaType.VIDEO:
      return EVideoToolName.VideoSegmentTool;
    case MediaType.AUDIO:
      return EAudioToolName.AudioSegmentTool;
    default:
      return undefined;
  }
};

const templateMapping: Record<string, any> = {
  [ImageToolName.Line]: lineTemplate,
  [ImageToolName.Rect]: rectTemplate,
  [ImageToolName.Polygon]: polygonTemplate,
  [ImageToolName.Point]: pointTemplate,
  [ImageToolName.Cuboid]: cuboidTemplate,
  [EGlobalToolName.Tag]: tagTemplate,
  [EGlobalToolName.Text]: textTemplate,
  [EVideoToolName.VideoSegmentTool]: videoSegmentTemplate,
  [EVideoToolName.VideoFrameTool]: videoFrameTemplate,
  [EAudioToolName.AudioSegmentTool]: audioSegmentTemplate,
  [EAudioToolName.AudioFrameTool]: audioFrameTemplate,
};

const FormConfig = () => {
  const { annotationFormInstance, onAnnotationFormChange, task } = useContext(TaskCreationContext);
  // const routerLoaderData = useRouteLoaderData('task') as TaskLoaderResult;
  const [activeTool, setActiveTool] = useState<string | undefined>(getDefaultActiveTool(task?.media_type));
  const [activeGlobalTool, setActiveGlobalTool] = useState<string | undefined>(globalTools[0]);
  // 选中的所有工具
  const [selectedTools, setSelectedTools] = useState<any[]>([]);
  // 选中的标记工具
  const [selectedAnnotationTools, setSelectedAnnotationTools] = useState<any[]>([]);
  // 选中的全局工具
  const [selectedGlobalTools, setSelectedGlobalTools] = useState<string[]>([]);
  const [hasAttributes, setHasAttributes] = useState(false);
  const { t } = useTranslation();

  const config = _.get(task, 'config');
  const taskStatus = _.get(task, 'status');
  const taskDoneAmount = _.get(task, 'stats.done');
  const { tools } = config || {};

  // 进行中和已完成的任务不允许删除工具
  const isGlobalToolDeletable = useMemo(() => {
    const isNew = !find(tools, { tool: activeGlobalTool });

    if (isNew) {
      return true;
    }

    if ([TaskStatus.INPROGRESS, TaskStatus.FINISHED].includes(taskStatus as TaskStatus) || taskDoneAmount) {
      return false;
    }

    return true;
  }, [tools, activeGlobalTool, taskStatus, taskDoneAmount]);

  const isToolDeletable = useMemo(() => {
    const isNew = !find(tools, { tool: activeTool });

    if (isNew) {
      return true;
    }

    if ([TaskStatus.INPROGRESS, TaskStatus.FINISHED].includes(taskStatus as TaskStatus) || taskDoneAmount) {
      return false;
    }

    return true;
  }, [tools, activeTool, taskStatus, taskDoneAmount]);

  useEffect(() => {
    const toolNames = _.chain(tools).compact().map('tool').value();
    setSelectedTools(toolNames);

    const annotationToolNames = _.filter(toolNames, (item) => !globalTools.includes(item));
    setSelectedAnnotationTools(annotationToolNames);
    setActiveTool(annotationToolNames[0]);

    const globalToolNames = _.filter(toolNames, (item) => globalTools.includes(item));
    setSelectedGlobalTools(globalToolNames);
    setActiveGlobalTool(globalToolNames[0]);
    setHasAttributes(config?.commonAttributeConfigurable ?? false);
  }, [config, tools]);

  // ======================== 以下为新增代码 ========================
  const handleToolItemClick: SelectProps['onChange'] = (key) => {
    setSelectedTools((pre) => [...pre, key]);

    if (globalTools.includes(key as EGlobalToolName)) {
      setSelectedGlobalTools((pre) => [...pre, key]);
      setActiveGlobalTool(key);
    } else {
      setActiveTool(key);
      setSelectedAnnotationTools((pre) => [...pre, key]);
    }

    if (typeof onAnnotationFormChange === 'function') {
      setTimeout(onAnnotationFormChange);
    }
  };

  const handleRemoveTool = useCallback(
    (toolName: ImageToolName | EGlobalToolName) => () => {
      const newTools = selectedTools.filter((item) => item !== toolName);
      setSelectedTools(newTools);

      if (globalTools.includes(toolName as EGlobalToolName)) {
        const newGlobalTools = newTools.filter((item) => globalTools.includes(item));
        setSelectedGlobalTools(newGlobalTools);
        setActiveGlobalTool(newGlobalTools[0]);
      } else {
        const newAnnotationTools = newTools.filter((item) => !globalTools.includes(item));
        setSelectedAnnotationTools(newAnnotationTools);
        setActiveTool(newAnnotationTools[0]);
      }

      // 因为antd的form的特殊性，删除数组元素时，需要手动调用setFieldsValue
      const prevValues = cloneDeep(annotationFormInstance.getFieldsValue());

      setTimeout(() => {
        annotationFormInstance.setFieldsValue({
          ...prevValues,
          tools: prevValues.tools.filter((item: any) => item.tool !== toolName),
        });

        if (typeof onAnnotationFormChange === 'function') {
          setTimeout(onAnnotationFormChange);
        }
      });
    },
    [annotationFormInstance, onAnnotationFormChange, selectedTools],
  );

  const toolsMenu = useMemo(() => {
    if (!task?.media_type) {
      return [];
    }

    const toolOptions = toolMapping[task.media_type!];

    return [
      {
        label: t('global'),
        options: _.map(globalTools, (toolName) => ({
          disabled: selectedTools.includes(toolName),
          value: toolName,
          label: <span>{TOOL_NAME[toolName]}</span>,
        })),
      },
      {
        label: t('tools'),
        options: _.map(toolOptions, ({ value, label }) => ({
          disabled: selectedTools.includes(value),
          value: value,
          label: <span>{label}</span>,
        })),
      },
    ];
  }, [selectedTools, task?.media_type, t]);

  const tabItems: TabsProps['items'] = useMemo(() => {
    return _.chain(selectedTools)
      .filter((tool) => {
        return !globalTools.includes(tool);
      })
      .map((tool) => {
        const fancyFormTemplate = templateMapping[tool] || null;
        const index = _.findIndex(selectedTools, (item) => item === tool);
        return {
          key: tool,
          label: TOOL_NAME[tool],
          forceRender: true,
          children: (
            <TabForm flex="column" gap=".5rem">
              {isToolDeletable && (
                <FlexLayout.Header flex justify="flex-end">
                  <Popconfirm title={t('deleteToolConfirm')} onConfirm={handleRemoveTool(tool as ImageToolName)}>
                    <Button type="link" danger>
                      {t('deleteTool')}
                    </Button>
                  </Popconfirm>
                </FlexLayout.Header>
              )}
              <FancyForm template={fancyFormTemplate} name={['tools', index]} />
            </TabForm>
          ),
        };
      })
      .value();
  }, [isToolDeletable, handleRemoveTool, selectedTools, t]);

  const tabGlobalItems: TabsProps['items'] = useMemo(() => {
    return _.chain(selectedTools)
      .filter((tool) => {
        return globalTools.includes(tool);
      })
      .map((tool) => {
        const fancyFormTemplate = templateMapping[tool] || null;
        const index = _.findIndex(selectedTools, (item) => item === tool);
        return {
          key: tool,
          label: TOOL_NAME[tool],
          forceRender: true,
          children: (
            <TabForm flex="column" gap=".5rem">
              {isGlobalToolDeletable && (
                <FlexLayout.Header flex justify="flex-end">
                  <Popconfirm title={t('deleteToolConfirm')} onConfirm={handleRemoveTool(tool as ImageToolName)}>
                    <Button type="link" danger>
                      {t('deleteTool')}
                    </Button>
                  </Popconfirm>
                </FlexLayout.Header>
              )}
              <FancyForm template={fancyFormTemplate} name={['tools', index]} />
            </TabForm>
          ),
        };
      })
      .value();
  }, [isGlobalToolDeletable, handleRemoveTool, selectedTools, t]);

  // TODO: 增加表单数据类型
  const handleFormValuesChange: FormProps['onValuesChange'] = useCallback(
    (changedValue: any) => {
      if ('commonAttributeConfigurable' in changedValue) {
        if (!changedValue.commonAttributeConfigurable) {
          annotationFormInstance.setFieldValue('attributes', []);
        }
        setHasAttributes(changedValue.commonAttributeConfigurable);
      }
    },
    [annotationFormInstance],
  );

  // ========================= end ==============================

  return (
    <ConfigForm
      form={annotationFormInstance}
      labelCol={{ span: 6 }}
      wrapperCol={{ span: 18 }}
      colon={false}
      initialValues={config}
      onValuesChange={handleFormValuesChange}
      validateTrigger="onBlur"
    >
      <GlobalStyle />
      <Form.Item label={t('annotationTool')}>
        <Select
          placeholder={t('addTool')}
          popupClassName="labelu-tool-select-popup"
          options={toolsMenu}
          onSelect={handleToolItemClick}
        >
          <PlusOutlined />
        </Select>
      </Form.Item>
      {selectedGlobalTools.length > 0 && (
        <Form.Item label={t('global')} tooltip={t('globalTooltip')}>
          <div className="formTabBox">
            <Tabs
              type="card"
              size="small"
              activeKey={activeGlobalTool}
              destroyInactiveTabPane={false}
              onTabClick={(tabKey) => {
                setActiveGlobalTool(tabKey);
              }}
              items={tabGlobalItems}
            />
          </div>
        </Form.Item>
      )}
      {selectedAnnotationTools.length > 0 && (
        <Form.Item label={t('labelTools')} tooltip={t('labelTooltip')}>
          <div className="formTabBox">
            <Tabs
              type="card"
              size="small"
              activeKey={activeTool}
              destroyInactiveTabPane={false}
              onTabClick={(tabKey) => {
                setActiveTool(tabKey);
              }}
              items={tabItems}
            />
          </div>
        </Form.Item>
      )}
      {selectedAnnotationTools.length > 0 && (
        <Form.Item
          label={<span className="formTitle">{t('genericLabels')}</span>}
          name="commonAttributeConfigurable"
          tooltip={t('genericLabelTooltip')}
          hidden={globalTools.includes(activeTool as EGlobalToolName)}
        >
          <FancyInput type="boolean" />
        </Form.Item>
      )}

      {hasAttributes && !globalTools.includes(activeTool as EGlobalToolName) && (
        <Form.Item wrapperCol={{ offset: 4 }}>
          <AttributeBox>
            <AttributeFormItem name="attributes">
              <FancyInput type="list-attribute" fullField={['attributes']} />
            </AttributeFormItem>
          </AttributeBox>
        </Form.Item>
      )}

      {task?.media_type === MediaType.IMAGE && (
        <Form.Item
          label={t('DrawingOutCanvas')}
          name="drawOutsideTarget"
          tooltip={t('DrawingOutCanvasTooltip')}
          hidden={!graphicTools.includes(activeTool as ImageToolName)}
        >
          <FancyInput type="boolean" />
        </Form.Item>
      )}
    </ConfigForm>
  );
};

export default React.memo(FormConfig);
