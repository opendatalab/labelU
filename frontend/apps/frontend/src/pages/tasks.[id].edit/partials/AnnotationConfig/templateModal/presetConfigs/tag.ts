export default {
  commonAttributeConfigurable: false,
  drawOutsideTarget: false,
  tools: [
    {
      tool: 'tagTool',
      config: {
        textConfigurable: false,
        textCheckType: 0,
        attributes: [
          {
            key: '标签-1',
            value: 'value-1',
            type: 'enum',
            options: [
              {
                key: '选项1-1',
                value: 'option1-1',
                isDefault: false,
              },
            ],
          },
        ],
      },
    },
  ],
};
