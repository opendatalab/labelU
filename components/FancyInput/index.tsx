import { FancyCategoryAttribute } from '../CustomFancy/CategoryAttribute.fancy';
import { FancyAttributeList } from '../CustomFancy/ListAttribute.fancy';
import { inputs, add, remove } from './fancyInput';
import type { FancyInputProps } from './types';

export default function FancyInput({ type, ...props }: FancyInputProps) {
  const Input = inputs[type];

  if (!Input) {
    console.warn(`FancyInput: ${type} is not supported`);
    return <>Not supported yet</>;
  }

  return <Input {...props} />;
}

add('list-attribute', FancyAttributeList);
add('category-attribute', FancyCategoryAttribute);

export { add, remove };
