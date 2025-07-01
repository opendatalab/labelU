import { Modal, Select } from 'antd';
import React, { useCallback, useMemo, useState } from 'react';
import { FlexLayout } from '@labelu/components-react';
import { i18n, useTranslation } from '@labelu/i18n';

import { ExportType, MediaType } from '@/api/types';
import { outputSample, outputSamples } from '@/api/services/samples';
import { EGlobalToolName, ImageToolName } from '@/enums';

export interface ExportPortalProps {
  children: React.ReactChild;
  taskId: number;
  mediaType: MediaType | undefined;
  sampleIds?: number[];
  tools?: any[];
}

export const exportDescriptionMapping = {
  [ExportType.JSON]: i18n.t('formatJsonDescription'),
  [ExportType.CSV]: i18n.t('formatCsvDescription'),
  [ExportType.XML]: i18n.t('formatXmlDescription'),
  [ExportType.COCO]: i18n.t('formatCocoDescription'),
  [ExportType.MASK]: i18n.t('formatMaskDescription'),
  [ExportType.YOLO]: i18n.t('formatYoloDescription'),
  [ExportType.LABEL_ME]: i18n.t('formatLabelmeDescription'),
  [ExportType.TF_RECORD]: i18n.t('formatTFRecordDescription'),
  [ExportType.PASCAL_VOC]: i18n.t('formatPascalVocDescription'),
};

const optionMapping = {
  [ExportType.JSON]: {
    label: ExportType.JSON,
    value: ExportType.JSON,
  },
  [ExportType.XML]: {
    label: ExportType.XML,
    value: ExportType.XML,
  },
  [ExportType.CSV]: {
    label: ExportType.CSV,
    value: ExportType.CSV,
  },
  [ExportType.YOLO]: {
    label: ExportType.YOLO,
    value: ExportType.YOLO,
  },
  [ExportType.COCO]: {
    label: ExportType.COCO,
    value: ExportType.COCO,
  },
  [ExportType.PASCAL_VOC]: {
    label: ExportType.PASCAL_VOC,
    value: ExportType.PASCAL_VOC,
  },
  [ExportType.MASK]: {
    label: ExportType.MASK,
    value: ExportType.MASK,
  },
  [ExportType.LABEL_ME]: {
    label: 'Labelme' as any,
    value: ExportType.LABEL_ME,
  },
  [ExportType.TF_RECORD]: {
    label: 'TF Record' as any,
    value: ExportType.TF_RECORD,
  },
};

function isIncludeCoco(tools?: any[]) {
  if (!tools) {
    return false;
  }

  // coco 包含 rect 和 polygon、point
  return !tools.some((item) => [ImageToolName.Cuboid, ImageToolName.Line, ImageToolName.Point].includes(item.tool));
}

export default function ExportPortal({ taskId, sampleIds, mediaType, tools, children }: ExportPortalProps) {
  const [modalVisible, setModalVisible] = useState(false);
  const [exportType, setExportType] = useState<ExportType>(ExportType.JSON);
  const { t } = useTranslation();

  const handleOpenModal = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setModalVisible(true);
  }, []);

  const handleCloseModal = useCallback(() => {
    setModalVisible(false);
  }, []);

  const handleOptionChange = (value: ExportType) => {
    setExportType(value);
  };

  const handleExport = useCallback(async () => {
    if (!sampleIds) {
      await outputSamples(taskId, exportType);
    } else {
      await outputSample(taskId, sampleIds, exportType);
    }

    setTimeout(() => {
      setModalVisible(false);
    });
  }, [exportType, sampleIds, taskId]);

  const plainChild = useMemo(() => {
    if (
      children === null ||
      children === undefined ||
      typeof children === 'boolean' ||
      !React.isValidElement(children)
    ) {
      return null;
    }

    if (typeof children === 'string' || typeof children === 'number') {
      return <span onClick={handleOpenModal}>{children}</span>;
    }

    return React.cloneElement(React.Children.only(children), {
      // @ts-ignore
      onClick: handleOpenModal,
    });
  }, [children, handleOpenModal]);

  const options = useMemo(() => {
    const toolsWithoutTagAndText = tools?.filter(
      (item) => ![EGlobalToolName.Text, EGlobalToolName.Tag].includes(item.tool),
    );
    const result = [optionMapping[ExportType.JSON], optionMapping[ExportType.XML]];

    if (!mediaType) {
      return result;
    }

    const onlyPolygonTool = toolsWithoutTagAndText?.length === 1 && toolsWithoutTagAndText[0].tool === 'polygonTool';
    const onlyRectTool = toolsWithoutTagAndText?.length === 1 && toolsWithoutTagAndText[0].tool === 'rectTool';
    const onlyPointTool = toolsWithoutTagAndText?.length === 1 && toolsWithoutTagAndText[0].tool === 'pointTool';
    const onlyCuboidTool = toolsWithoutTagAndText?.length === 1 && toolsWithoutTagAndText[0].tool === 'cuboidTool';
    const onlyLineTool = toolsWithoutTagAndText?.length === 1 && toolsWithoutTagAndText[0].tool === 'lineTool';

    if (mediaType === MediaType.IMAGE) {
      result.push(optionMapping[ExportType.TF_RECORD]);

      if (onlyPolygonTool || onlyRectTool || onlyPointTool || onlyCuboidTool || onlyLineTool) {
        result.push(optionMapping[ExportType.CSV]);
      }

      if (isIncludeCoco(toolsWithoutTagAndText)) {
        result.push(optionMapping[ExportType.COCO]);
      }

      if (onlyRectTool) {
        result.push(optionMapping[ExportType.YOLO], optionMapping[ExportType.PASCAL_VOC]);
      }

      // mask: polygon
      if (onlyPolygonTool) {
        result.push(optionMapping[ExportType.MASK]);
      }

      if (!toolsWithoutTagAndText?.find((item) => ['cuboidTool'].includes(item.tool))) {
        result.push(optionMapping[ExportType.LABEL_ME] as any);
      }
    }

    return result;
  }, [mediaType, tools]);

  return (
    <>
      {plainChild}
      <Modal
        title={t('selectExportFormat')}
        okText={t('doExport')}
        onOk={handleExport}
        onCancel={handleCloseModal}
        open={modalVisible}
      >
        <FlexLayout flex="column" gap="1rem">
          <FlexLayout.Header items="center" gap="1rem" flex>
            <span style={{ whiteSpace: 'nowrap' }}>{t('exportFormat')}</span>
            <Select popupMatchSelectWidth={false} options={options} onChange={handleOptionChange} value={exportType} />
          </FlexLayout.Header>
          <div>{exportDescriptionMapping[exportType]}</div>
        </FlexLayout>
      </Modal>
    </>
  );
}
