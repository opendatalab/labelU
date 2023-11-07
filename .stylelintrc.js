const { stylelint } = require('@shlab/fabric');

const prettierConfig = require('./.prettierrc');

module.exports = {
  ...stylelint,
  customSyntax: 'postcss-scss',
  plugins: ['stylelint-prettier'],
  rules: {
    'prettier/prettier': [true, prettierConfig],
    'selector-class-pattern': null,
    'no-descending-specificity': null,
    'declaration-block-no-redundant-longhand-properties': null,
  },
};
