import * as path from 'path';
import { defineConfig } from 'rspress/config';
import { pluginGoogleAnalytics } from 'rsbuild-plugin-google-analytics';

export default defineConfig({
  root: path.join(__dirname, 'docs'),
  title: 'LabelU',
  lang: 'zh',
  base: '/labelU/',
  description: 'LabelU is a comprehensive data annotation platform designed for handling multimodal data. It offers a range of advanced annotation tools and efficient workflows, making it easier for users to tackle annotation tasks involving images, videos, and audio. LabelU is tailored to meet the demands of complex data analysis and model training.',
  icon: '/logo.svg',
  logoText: "LabelU",
  logo: {
    light: '/logo.svg',
    dark: '/logo.svg',
  },
  builderConfig: {
    plugins: [
      pluginGoogleAnalytics({ id: 'G-VZ82VW0WEH' }),
    ],
    source: {
      alias: {
        'components': path.join(__dirname, 'components'),
        '@en': path.join(__dirname, 'docs/en'),
        '@zh': path.join(__dirname, 'docs/zh'),
      },
    },
  },
  route: {
    cleanUrls: true,
  },
  globalStyles: path.join(__dirname, 'styles/index.css'),
  themeConfig: {
    footer: {
      message: 'Powered by OpenDataLab',
    },
    locales: [
      {
        lang: 'en',
        label: 'English',
        title: 'LabelU',
        description: 'LabelU is a comprehensive data annotation platform designed for handling multimodal data. It offers a range of advanced annotation tools and efficient workflows, making it easier for users to tackle annotation tasks involving images, videos, and audio. LabelU is tailored to meet the demands of complex data analysis and model training.',
        editLink: {
          docRepoBaseUrl:
            'https://github.com/opendatalab/labelU/tree/website/docs',
          text: 'Edit this page on GitHub',
        },
      },
      {
        lang: 'zh',
        label: '简体中文',
        title: 'LabelU',
        outlineTitle: '目录',
        prevPageText: '上一页',
        nextPageText: '下一页',
        description: 'LabelU是一款综合性的数据标注平台，专为处理多模态数据而设计。该平台旨在通过提供丰富的标注工具和高效的工作流程，帮助用户更轻松地处理图像、视频和音频数据的标注任务，满足各种复杂的数据分析和模型训练需求。',
        editLink: {
          docRepoBaseUrl:
            'https://github.com/opendatalab/labelU/tree/website',
          text: '在 GitHub 上编辑此页',
        },
      },
    ],
    socialLinks: [
      {
        icon: {
          svg: `<div id="labelukit">
            LabelU-kit
            <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 24 24" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M13 3L16.293 6.293 9.293 13.293 10.707 14.707 17.707 7.707 21 11 21 3z"></path><path d="M19,19H5V5h7l-2-2H5C3.897,3,3,3.897,3,5v14c0,1.103,0.897,2,2,2h14c1.103,0,2-0.897,2-2v-5l-2-2V19z"></path></svg>
            <style>
              #labelukit {
                display: flex;
                align-items: center;
                gap: 0.5em;
              }
              .social-links:nth-child(1) > div {
                width: auto;
              }
            </style>
          </div>`
        },
        mode: 'link',
        content: 'https://github.com/opendatalab/labelU-kit#readme',
      },
      { icon: 'github', mode: 'link', content: 'https://github.com/opendatalab/labelU' },
    ],
  },
});
