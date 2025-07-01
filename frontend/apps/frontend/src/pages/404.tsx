import styled from 'styled-components';
import { useTranslation } from '@labelu/i18n';

import { ReactComponent as NotFoundIcon } from '@/assets/svg/not-found.svg';
import Navigate from '@/components/Navigate';

const NotFoundWrapper = styled.div`
  display: flex;
  width: 100vw;
  height: 100vh;
  flex-direction: column;

  .content {
    flex: 1;
    display: flex;
    width: 100%;
    background-color: var(--color-fill-quaternary);
  }

  .inner {
    margin: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
`;

const NotFoundPage: React.FC<Record<string, unknown>> = () => {
  const { t } = useTranslation();
  return (
    <NotFoundWrapper>
      <Navigate />
      <div className="content">
        <div className="inner">
          <NotFoundIcon />
          <h3>{t('404notFound')}</h3>
        </div>
      </div>
    </NotFoundWrapper>
  );
};

export default NotFoundPage;
