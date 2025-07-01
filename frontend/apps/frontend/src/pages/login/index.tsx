import type { FormProps } from 'antd';
import { Input, Form } from 'antd';
import { Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { FlexLayout } from '@labelu/components-react';
import { useTranslation } from '@labelu/i18n';
import { useEffect } from 'react';

import { login } from '@/api/services/user';
import { ReactComponent as EmailIcon } from '@/assets/svg/email.svg';
import { ReactComponent as PasswordIcon } from '@/assets/svg/password.svg';
import LanguageSwitcher from '@/components/LangSwitcher';
import useMe from '@/hooks/useMe';

import LogoTitle from '../../components/LogoTitle';
import { ButtonWrapper, FormWrapper, LoginWrapper } from './style';

interface FormValues {
  username: string;
  password: string;
}

const LoginPage = () => {
  const [form] = Form.useForm<FormValues>();
  const me = useMe();
  const { t } = useTranslation();
  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      window.location.href = '/tasks';
    },
  });

  useEffect(() => {
    if (me.data?.id) {
      window.location.href = '/tasks';
    }
  }, [me]);

  const handleLogin: FormProps<FormValues>['onFinish'] = async (values) => {
    loginMutation.mutate(values);
  };

  const handleSubmit = (e: React.MouseEvent | React.KeyboardEvent) => {
    e.preventDefault();
    form.submit();
  };

  return (
    <LoginWrapper flex="column" justify="center" items="center">
      <LogoTitle />
      <FormWrapper gap=".5rem" flex="column">
        <Form<FormValues> form={form} onFinish={handleLogin}>
          <FlexLayout flex="column">
            <h1>{t('login')}</h1>
            <Form.Item
              name="username"
              rules={[
                { required: true, message: t('emailPlease') },
                { type: 'email', message: t('emailFormatPlease') },
              ]}
            >
              <Input placeholder={t('email')} prefix={<EmailIcon />} onPressEnter={handleSubmit} />
            </Form.Item>
            <Form.Item
              name="password"
              rules={[
                { required: true, message: t('passwordPlease') },
                {
                  pattern: /^\S+$/,
                  message: t('passwordCannotContainsWhitespace'),
                },
                {
                  min: 6,
                  message: t('passwordLengthError'),
                },
              ]}
            >
              <Input.Password
                placeholder={t('password')}
                prefix={<PasswordIcon />}
                visibilityToggle={false}
                onPressEnter={handleSubmit}
              />
            </Form.Item>
            <Form.Item>
              <ButtonWrapper loading={loginMutation.isPending} block type="primary" onClick={handleSubmit}>
                {t('login')}
              </ButtonWrapper>
            </Form.Item>
          </FlexLayout>
        </Form>
        <FlexLayout justify="space-between" items="center">
          <LanguageSwitcher />
          <Link to="/register">{t('signUp')}</Link>
        </FlexLayout>
      </FormWrapper>
    </LoginWrapper>
  );
};
export default LoginPage;
