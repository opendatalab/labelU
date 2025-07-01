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
      tool: 'lineTool',
      config: {
        isShowCursor: false,
        lineType: 0,
        lineColor: 1,
        edgeAdsorption: false,
        drawOutsideTarget: true,
        copyBackwardResult: false,
        attributeConfigurable: true,
        textConfigurable: false,
        textCheckType: 4,
        lowerLimitPointNum: 2,
        upperLimitPointNum: '',
        attributes: [{ color: '#11bb33', key: '标签-1', value: 'value-1' }],
      },
    },
  ],
};
