const fs = require('fs');
const path = require('path');

const _ = require('lodash');
let codeTemplate;
const targetPath = path.join(__dirname, '../src/styles/global-variables.css');
const tokenPath = path.join(__dirname, '../src/styles/theme.json');
const { theme } = require('antd');
const prettier = require('prettier');
const { defaultAlgorithm, defaultSeed } = theme;

const mapToken = defaultAlgorithm(defaultSeed);

try {
  const theme = {
    ...mapToken,
    ...require(tokenPath).token,
  };

  const result = _.chain(theme)
    .keys()
    .map((key) => {
      const newKey = key
        .replace(/([A-Z])+/g, (match) => {
          return `-${match}`;
        })
        .toLowerCase();
      if (
        newKey.includes('size') ||
        newKey.includes('border-radius') ||
        newKey.includes('control-height') ||
        newKey.includes('line-width-bold')
      ) {
        return `--${newKey}: ${theme[key]}px;`;
      }

      let value = theme[key];

      if (typeof value === 'number' && value.toString().length > 5) {
        value = parseFloat(value.toFixed(2));
      }

      return `--${newKey}: ${value};`;
    })
    .value();

  codeTemplate = `
  /**
   * 此文件由apps/frontend/scripts/generate_css_variables_from_antd_theme_token.js脚本生成
   * 请勿直接修改此文件
   * */
    :root {
      ${result.join('\n')}
    }
  `;

  fs.unlinkSync(targetPath);
} catch (err) {
} finally {
  if (codeTemplate) {
    fs.writeFile(
      targetPath,
      prettier.format(codeTemplate, {
        parser: 'css',
      }),
      'utf-8',
      () => {
        console.log(`🎉 ${targetPath}已生成`);
      },
    );
  }
}
