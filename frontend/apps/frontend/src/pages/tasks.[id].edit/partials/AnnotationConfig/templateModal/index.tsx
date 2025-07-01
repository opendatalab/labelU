import { useCallback, useContext, useMemo, useState } from 'react';
import { Button, Card, Col, Empty, Menu, Modal, Row } from 'antd';
import _ from 'lodash-es';
import styled from 'styled-components';

import { MediaType, TaskStatus } from '@/api/types';

import { TaskCreationContext } from '../../../taskCreation.context';
import * as presetConfigs from './presetConfigs';
import * as covers from './covers';

const StyledWrapper = styled.div`
  display: flex;
  align-items: stretch;

  .left {
    width: 8.625rem;
    flex-shrink: 0;
  }

  .ant-menu-item-selected {
    position: relative;
    &:before {
      position: absolute;
      display: block;
      width: 3px;
      border-radius: 0 var(--border-radius) var(--border-radius) 0;
      height: 1rem;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      content: ' ';
      background-color: var(--color-primary);
    }
  }

  .menu {
    height: 100%;
    padding: 0.625rem 0.5rem;
    background-color: #fbfbfb;
    border-inline-end: 0 !important;
    border-radius: var(--border-radius-lg);
  }

  .right {
    flex-grow: 1;
    margin-left: 1.5rem;
  }

  .title {
    .ant-card-meta-title {
      font-weight: normal;
    }
  }

  .empty {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .ant-card {
    position: relative;
    overflow: hidden;
  }

  .overlay {
    opacity: 0;
    transition: opacity var(--motion-duration-mid);
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.7);
    display: flex;
    justify-content: center;

    button {
      margin-top: 4rem;
    }

    &:hover {
      opacity: 1;
    }
  }

  .card {
    .ant-card-cover {
      height: 10rem;
    }
  }
`;

interface TemplateItem {
  label: string;
  type: MediaType;
  name: string;
  presetConfig: any;
  cover?: string;
}

const templates: TemplateItem[] = [
  {
    label: '目标检测（矩形框）',
    type: MediaType.IMAGE,
    presetConfig: {},
    name: 'rect',
  },
  {
    label: '语义分割(多边形)',
    type: MediaType.IMAGE,
    presetConfig: {},
    name: 'polygon',
  },
  {
    label: '线标注',
    type: MediaType.IMAGE,
    presetConfig: {},
    name: 'line',
  },
  {
    label: '点标注',
    type: MediaType.IMAGE,
    presetConfig: {},
    name: 'point',
  },
  {
    label: '目标分类(标签分类)',
    type: MediaType.IMAGE,
    presetConfig: {},
    name: 'tag',
  },
  {
    label: '文本描述',
    type: MediaType.IMAGE,
    presetConfig: {},
    name: 'text',
  },
];

(async () => {
  for (const item of templates) {
    item.cover = _.get(covers, item.name);
    item.presetConfig = _.get(presetConfigs, item.name);
  }
})();

interface TemplateModalProps {
  onSelect: (template: any) => void;
}

export default function TemplateModal({ onSelect }: TemplateModalProps) {
  const { task } = useContext(TaskCreationContext);
  const [visible, toggleVisible] = useState(false);
  const [activeType, setActiveType] = useState(MediaType.IMAGE);

  const shouldShowTemplate = useMemo(() => {
    return [TaskStatus.CONFIGURED, TaskStatus.DRAFT, TaskStatus.IMPORTED].includes(task.status as TaskStatus);
  }, [task.status]);

  const handleOpenModal = () => {
    toggleVisible(true);
  };

  const handleCloseModal = () => {
    toggleVisible(false);
  };

  const handleMenuClick = useCallback(({ key }: { key: string }) => {
    setActiveType(key as MediaType);
  }, []);

  const handleSelect = useCallback(
    (basicConfig: any) => {
      onSelect?.(basicConfig);
      toggleVisible(false);
    },
    [onSelect],
  );

  const menuItems = useMemo(() => {
    return [
      {
        key: MediaType.IMAGE,
        label: '图片',
      },
      // TODO：暂时不支持
      // {
      //   key: MediaType.POINT_CLOUD,
      //   label: '点云',
      // },
      // {
      //   key: MediaType.VIDEO,
      //   label: '视频',
      // },
    ];
  }, []);

  const templateFiltered = useMemo(() => {
    return templates.filter((item) => item.type === activeType);
  }, [activeType]);

  const templateNodes = useMemo(() => {
    return _.map(templateFiltered, ({ label, name, cover, presetConfig }) => {
      return (
        <Col span={8} key={name}>
          <Card
            className="card"
            cover={
              <>
                <img src={cover} />

                <div className="overlay">
                  <Button type="primary" onClick={() => handleSelect(presetConfig)}>
                    使用
                  </Button>
                </div>
              </>
            }
          >
            <Card.Meta title={label} className="title" />
          </Card>
        </Col>
      );
    });
  }, [handleSelect, templateFiltered]);

  return (
    <>
      {shouldShowTemplate && (
        <Button type="default" style={{ color: 'var(--color-primary)' }} onClick={handleOpenModal}>
          选择模板
        </Button>
      )}
      <Modal
        title="模板选择"
        width={980}
        open={visible}
        onCancel={handleCloseModal}
        bodyStyle={{ padding: '1rem 0' }}
        footer={null}
      >
        <StyledWrapper className="wrapper">
          <div className="left">
            <Menu
              className="menu"
              defaultSelectedKeys={[activeType]}
              mode="vertical"
              onClick={handleMenuClick}
              items={menuItems}
            />
          </div>
          <div className="right">
            {_.isEmpty(templateFiltered) ? (
              <div className="empty">
                <Empty description="暂无此类别模板" image={Empty.PRESENTED_IMAGE_SIMPLE} />
              </div>
            ) : (
              <Row gutter={[24, 24]}>{templateNodes}</Row>
            )}
          </div>
        </StyledWrapper>
      </Modal>
    </>
  );
}
