export default {
  attributes: [
    {
      color: '#ff6600',
      key: '通用标签-1',
      value: 'common-value-1',
    },
  ],
  commonAttributeConfigurable: true,
  tools: [
    {
      tool: 'rectTool',
      config: {
        isShowCursor: false,
        showConfirm: false,
        skipWhileNoDependencies: false,
        drawOutsideTarget: false,
        copyBackwardResult: false,
        minWidth: 1,
        attributeConfigurable: true,
        textConfigurable: false,
        textCheckType: 4,
        customFormat: '',
        attributes: [{ color: '#11bb33', key: '标签-1', value: 'value-1' }],
      },
    },
  ],
};
