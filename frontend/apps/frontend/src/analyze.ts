import * as storage from '@/utils/storage';

// ==========================【埋点】=========================
const correctInfo = {
  token: '5ea1ddb69d6519b6',
  host: 'labelu.shlab.tech',
  api: 'https://analyze.shlab.tech/api/v1/log/create',
};

const userid = storage.get('userid');
const username = storage.get('username');

function main() {
  if (!window.AnalyzeWiz) {
    console.warn('未引入埋点脚本');
    return;
  }

  if (location.host.startsWith('localhost')) {
    return;
  }

  if (userid) {
    window.AnalyzeWiz.setUser({
      id: `${username}-${userid}`,
      name: username,
    });
  } else {
    // 从sso进来还未获取到用户信息，此时将用户信息设置为未登录
    window.AnalyzeWiz.setUser({
      id: 'unlogin',
      name: '未登录',
    });
  }

  window.AnalyzeWiz.init({
    organize: 'labelu-online',
    delay: 0,
    // 默认为test环境的token，prod 为 5ea1ddb69d6519b6
    token: correctInfo.token,
    api: correctInfo.api,
    actions: [
      // 浏览器url访问或刷新
      {
        name: 'DOMContentLoaded',
        selector: 'window',
        handler: () => {
          return {
            type: 'page_view',
            resourceType: 'page',
            resourceId: location.pathname + location.search + location.hash,
          };
        },
      },
      {
        name: 'click',
        selector: '[data-wiz="task-create"]',
        data: {
          type: 'button_click',
          resourceType: 'button',
          resourceId: 'task-create',
        },
      },
      {
        name: 'click',
        selector: '[data-wiz="documentation"]',
        data: {
          type: 'button_click',
          resourceType: 'button',
          resourceId: 'documentation',
        },
      },
      {
        name: 'click',
        selector: '[data-wiz="local-deploy-top-right"]',
        data: {
          type: 'button_click',
          resourceType: 'button',
          resourceId: 'local-deploy-top-right',
        },
      },
      {
        name: 'click',
        selector: '[data-wiz="local-deploy-alert"]',
        data: {
          type: 'button_click',
          resourceType: 'button',
          resourceId: 'local-deploy-alert',
        },
      },
    ],
  });
}

main();
