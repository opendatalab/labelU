import { ArrowRightOutlined } from '@ant-design/icons';
import { Avatar } from 'antd';
import _ from 'lodash';
import { useTranslation } from '@labelu/i18n';
import { useMemo } from 'react';

import { ReactComponent as LabelLLM } from '@/assets/svg/labelllm.svg';
import { ReactComponent as MinerU } from '@/assets/svg/mineru.svg';
import { ReactComponent as OpenDataLab } from '@/assets/svg/opendatalab.svg';

import styles from './index.module.css';

interface AppLink {
  name: string;
  title: string;
  links: {
    name: string;
    link: string;
  }[];
  icon: JSX.Element;
  description: string;
}

export default function AppPanel() {
  const { t } = useTranslation();
  const handleGoApp = (app: AppLink) => {
    window.open(app.links[0].link, '_blank');
  };

  const apps = useMemo(
    () => [
      {
        name: 'OpenDataLab',
        links: [{ name: t('goTo'), link: 'https://opendatalab.com' }],
        icon: <OpenDataLab />,
        description: t('opendatalabDescription'),
      },
      {
        name: 'LabelLLM',
        links: [
          {
            name: 'Github',
            link: 'https://github.com/opendatalab/LabelLLM?tab=readme-ov-file#labelllm-the-open-source-data-annotation-platform',
          },
        ],
        icon: <LabelLLM />,
        description: t('labelllmDescription'),
      },
      {
        name: 'MinerU',
        links: [
          { name: 'Github', link: 'https://github.com/opendatalab/MinerU' },
          { name: t('tryOnline'), link: 'https://opendatalab.com/OpenSourceTools/Extractor/PDF' },
        ],
        icon: <MinerU />,
        description: t('minerUDescription'),
      },
    ],
    [t],
  );

  return (
    <div>
      <div className={styles.title}>{t('toolboxWelcome')}</div>
      <div className={styles.panel}>
        {_.map(apps, (app) => {
          return (
            <div key={app.name} className={styles.appWrapper}>
              <div className={styles.appContainer}>
                <div className={styles.header} onClick={() => handleGoApp(app)}>
                  <Avatar shape="square" className={styles.avatar} src={app.icon} />
                  <div className={styles.appInfo}>
                    {app.name}
                    <div className={styles.description}>{app.description}</div>
                  </div>
                </div>
                <div className={styles.links}>
                  {_.map(app.links, (link) => {
                    return (
                      <a href={link.link} key={link.name} target="_blank" rel="noreferrer" className={styles.link}>
                        {link.name}
                        <ArrowRightOutlined className={styles.arrow} />
                      </a>
                    );
                  })}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
