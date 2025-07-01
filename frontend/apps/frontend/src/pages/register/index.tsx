import { Form, Input } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import _ from 'lodash';
import { useMutation } from '@tanstack/react-query';
import { FlexLayout } from '@labelu/components-react';
import { useTranslation } from '@labelu/i18n';

import { signUp } from '@/api/services/user';
import { ReactComponent as EmailIcon } from '@/assets/svg/email.svg';
import { ReactComponent as PasswordIcon } from '@/assets/svg/password.svg';
import { message } from '@/StaticAnt';
import LanguageSwitcher from '@/components/LangSwitcher';

import LogoTitle from '../../components/LogoTitle';
import { ButtonWrapper, FormWrapper, LoginWrapper } from '../login/style';

interface FormValues {
  username: string;
  password: string;
  confirmPassword: string;
}

const SignUpPage = () => {
  const [form] = Form.useForm<FormValues>();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const signUpMutation = useMutation({
    mutationFn: signUp,
    onSuccess: () => {
      message.success(t('signUpSuccess'));
      navigate('/login');
    },
    onError: () => {
      message.error(t('signUpFailed'));
    },
  });

  const register = async function () {
    form.validateFields().then(async (values) => {
      signUpMutation.mutate(_.pick(values, ['username', 'password']));
    });
  };

  const handleSubmit = (e: React.MouseEvent) => {
    e.preventDefault();
    form.submit();
  };

  return (
    <LoginWrapper flex="column" justify="center" items="center">
      <LogoTitle />
      <FormWrapper gap=".5rem" flex="column">
        <Form form={form} onFinish={register}>
          <FlexLayout flex="column">
            <h1>{t('signUp')}</h1>
            <Form.Item
              name="username"
              rules={[
                { required: true, message: t('emailPlease') },
                { type: 'email', message: t('emailFormatPlease') },
              ]}
            >
              <Input placeholder={t('email')} prefix={<EmailIcon />} />
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
              <Input.Password placeholder={t('password')} prefix={<PasswordIcon />} visibilityToggle={false} />
            </Form.Item>

            <Form.Item
              name="confirmPassword"
              dependencies={['password']}
              rules={[
                {
                  required: true,
                  message: t('confirmPasswordPlease'),
                },
                ({ getFieldValue }) => ({
                  validator(_unused, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }

                    return Promise.reject(new Error(t('passwordRepeatedUnMatch')));
                  },
                }),
                {
                  min: 6,
                  message: t('passwordLengthError'),
                },
              ]}
            >
              <Input.Password placeholder={t('passwordConfirm')} visibilityToggle={false} prefix={<PasswordIcon />} />
            </Form.Item>

            <Form.Item>
              <ButtonWrapper block type="primary" onClick={handleSubmit} loading={signUpMutation.isPending}>
                {t('signUp')}
              </ButtonWrapper>
            </Form.Item>
          </FlexLayout>
        </Form>
        <FlexLayout justify="space-between" items="center">
          <LanguageSwitcher />
          <div>
            {t('alreadyHaveAccount')} <Link to={'/login'}>{t('login')}</Link>
          </div>
        </FlexLayout>
      </FormWrapper>
    </LoginWrapper>
  );
};
export default SignUpPage;
