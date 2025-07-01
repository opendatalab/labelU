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
      tool: 'polygonTool',
      config: {
        isShowCursor: false,
        lineType: 0,
        lineColor: 0,
        drawOutsideTarget: false,
        edgeAdsorption: false,
        copyBackwardResult: false,
        attributeConfigurable: true,
        textConfigurable: false,
        upperLimitPointNum: 100,
        lowerLimitPointNum: 3,
        textCheckType: 0,
        customFormat: '',
        attributes: [{ color: '#11bb33', key: '标签-1', value: 'value-1' }],
      },
    },
  ],
};
