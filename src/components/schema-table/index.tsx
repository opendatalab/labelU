import { useState, type FC } from 'react';
import { BiChevronRight } from '@react-icons/all-files/bi/BiChevronRight';
import { BiChevronDown } from '@react-icons/all-files/bi/BiChevronDown';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

interface SchemaProp {
  [key: string]: {
    required?: string[];
    type: string | string[];
    description?: string;
    default?: string | number | boolean;
    items?: { properties: SchemaProp };
    properties?: SchemaProp;
    additionalProperties?: {
      anyOf?: SchemaProp[];
    };
  };
}
const typeBadgeMap = {
  string: 'badge-secondary',
  number: 'badge-success',
  boolean: 'badge-error',
  array: 'badge-primary',
  object: 'badge-neutral',
} as Record<string, string>;

interface Schema {
  type: 'object';
  properties: SchemaProp;
  required: string[];
}

interface JsonSchemaTableProps {
  schema: Schema;
}

const JsonSchemaTable: FC<JsonSchemaTableProps> = ({ schema }) => {
  const { t } = useTranslation();
  const headers = [t('field'), t('type'), t('required'), t('default'), t('description')];

  // Manage expand/collapse state of each array field
  const [expandedFields, setExpandedFields] = useState<string[]>([]);

  const handleClick = (field: string) => {
    setExpandedFields((prevState) =>
      prevState.includes(field) ? prevState.filter((f) => f !== field) : [...prevState, field],
    );
  };

  // Recursively generate rows
  const generateRows = (properties: SchemaProp, requiredFields: string[], parentKey = '', isChild?: boolean, depth = 0) => {
    return Object.entries(properties).flatMap(([key, value]) => {
      const fullKey = parentKey + key;

      const rows = [
        <tr
          key={fullKey}
          className={clsx({
            'bg-slate-50': isChild,
          })}
        >
          <td
            style={{
              paddingLeft: `${1 * (depth + 1)}rem`,
            }}
          >
            <div className="flex items-center gap-2">
              {key}
              {((value.type === 'array' && value.items?.properties) ||
                (value.type === 'object' && (value.properties || value.additionalProperties))) && (
                <button className="btn btn-square btn-xs text-lg" onClick={() => handleClick(fullKey)}>
                  {expandedFields.includes(fullKey) ? <BiChevronDown /> : <BiChevronRight />}
                </button>
              )}
            </div>
          </td>
          <td>
            <div className="flex gap-2">
              {Array.isArray(value.type) ? (
                value.type.map((typeItem) => (
                  <div key={typeItem} className={clsx('badge badge-outline', typeBadgeMap[typeItem])}>
                    {typeItem}
                  </div>
                ))
              ) : (
                <div className={clsx('badge badge-outline', typeBadgeMap[value.type])}>{value.type}</div>
              )}
            </div>
          </td>
          <td>{requiredFields.includes(key) ? t('yes') : t('no')}</td>
          <td>{value.default ? value.default.toString() : '-'}</td>
          <td>{value.description}</td>
        </tr>,
      ];

      if (
        ((value.type === 'array' && value.items?.properties) || (value.type === 'object' && value.properties)) &&
        expandedFields.includes(fullKey)
      ) {
        const nestedProperties = value.type === 'array' ? value.items!.properties : value.properties;

        rows.push(...generateRows(nestedProperties!, value.required ?? [], `${fullKey}.`, true, depth + 1));
      }

      if (value.additionalProperties && expandedFields.includes(fullKey)) {
        if (value.additionalProperties.anyOf) {
          rows.push(
            ...generateRows(
              { '[string]': { type: value.additionalProperties.anyOf.map((item) => item.type as unknown as string) } },
              requiredFields,
              `${fullKey}.`,
              true,
              depth + 1,
            ),
          );
        }
      }

      return rows;
    });
  };

  return (
    <table className="table">
      <thead>
        <tr>
          {headers.map((header, index) => (
            <th key={index}>{header}</th>
          ))}
        </tr>
      </thead>
      <tbody>{generateRows(schema.properties, schema.required)}</tbody>
    </table>
  );
};

export default JsonSchemaTable;
