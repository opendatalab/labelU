export default {
  commonAttributeConfigurable: false,
  drawOutsideTarget: false,
  tools: [
    {
      tool: 'textTool',
      config: {
        textConfigurable: false,
        textCheckType: 0,
        attributes: [
          {
            key: '标签-1',
            value: 'value-1',
            type: 'string',
            stringType: 'text',
            required: true,
            defaultValue: '',
            maxLength: 1000,
          },
        ],
      },
    },
  ],
};
