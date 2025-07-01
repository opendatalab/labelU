import { FancyBoolean } from './Boolean.fancy';
import { FancyEnum } from './Enum.fancy';
import { FancyString } from './String.fancy';
import { FancyNumber } from './Number.fancy';

export const inputs: Record<string, React.FC<any>> = {
  enum: FancyEnum,
  string: FancyString,
  number: FancyNumber,
  boolean: FancyBoolean,
};

export function add<T>(type: string, component: React.FC<T>) {
  if (inputs[type]) {
    console.warn(`[FancyInput] ${type} already exists`);
    return;
  }

  inputs[type] = component;
}

export function remove(type: string) {
  delete inputs[type];
}
