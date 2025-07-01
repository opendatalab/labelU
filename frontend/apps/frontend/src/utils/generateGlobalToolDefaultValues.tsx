import type { EnumerableAttribute, TagAnnotationEntity, TextAnnotationEntity, TextAttribute } from '@labelu/interface';
import { uid } from '@labelu/video-react';

export function generateDefaultValues(
  attributes?: (TextAttribute | EnumerableAttribute)[],
): (TagAnnotationEntity | TextAnnotationEntity)[] {
  const result: (TagAnnotationEntity | TextAnnotationEntity)[] = [];

  if (!attributes) {
    return result;
  }

  for (let i = 0; i < attributes.length; i++) {
    const stringItem = attributes[i] as TextAttribute;

    if (stringItem.type === 'string' && stringItem.defaultValue) {
      result.push({
        id: uid(),
        type: 'text',
        value: {
          [stringItem.value]: stringItem.defaultValue,
        },
      });
    }

    const tagItem = attributes[i] as EnumerableAttribute;

    if (tagItem.type === 'enum' || tagItem.type === 'array') {
      const defaultValues = [];
      for (let j = 0; j < tagItem.options.length; j++) {
        if (tagItem.options[j].isDefault) {
          defaultValues.push(tagItem.options[j].value);
        }
      }

      if (defaultValues.length > 0) {
        result.push({
          id: uid(),
          type: 'tag',
          value: {
            [tagItem.value]: defaultValues,
          },
        });
      }
    }
  }

  return result;
}
