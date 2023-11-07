module.exports = {
  root: true,
  extends: [require.resolve('@shlab/fabric/dist/eslint')],
  rules: {
    '@typescript-eslint/no-namespace': 0,
  },
  globals: {
    JSX: true,
    React: true,
    NodeJS: true,
  },
  rules: {
    'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
  },
};
