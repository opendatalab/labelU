import React, { useState, type FC } from 'react';
import { BiChevronRight } from '@react-icons/all-files/bi/BiChevronRight';
import { BiChevronDown } from '@react-icons/all-files/bi/BiChevronDown';
import clsx from 'clsx';
import { useI18n } from 'rspress/runtime';

// 继承span的所有props
interface BadgeProps extends React.HTMLProps<HTMLSpanElement> {
  children: React.ReactNode;
}
function Badge({ children, className, ...props }: BadgeProps) {
  return <span className={clsx('px-1 py-0.5 rounded text-sm', className)} {...props}>{children}</span>;
}

interface SchemaProp {
  [key: string]: {
    required?: string[];
    $ref?: string;
    type: string | string[];
    description?: string;
    default?: string | number | boolean;
    items?: { properties: SchemaProp, $ref?: string, anyOf?: SchemaProp[]};
    properties?: SchemaProp;
    additionalProperties?: {
      anyOf?: SchemaProp[];
    };
  };
}

const badgeColors = {
  string: 'bg-blue-100 text-blue-500',
  number: 'bg-green-100 text-green-500',
  integer: 'bg-green-100 text-green-500',
  boolean: 'bg-red-100 text-red-500',
  array: 'bg-yellow-100 text-yellow-500',
  object: 'bg-purple-100 text-purple-500',
  null: 'bg-gray-100 text-gray-500',
} as Record<string, string>;

interface Schema {
  type: 'object';
  properties: SchemaProp;
  required: string[];
  definitions: SchemaProp;
}

interface JsonSchemaTableProps {
  schema: Schema;
}

// #/definitions/TextAttribute -> text-attribute
function getReferenceName(ref: string) {
  return ref.split('/').pop()!.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
}

function makeReferenceUrl(ref: string) {
  return `/schema/interface/${getReferenceName(ref)}`;
}

const resolveRef = (ref: string, definitions: SchemaProp | undefined) => {
  if (!definitions || !ref.startsWith('#/definitions/')) {
    return null;
  }

  const path = ref.slice('#/definitions/'.length).split('/');
  let schema: SchemaProp | undefined = definitions;

  for (const segment of path) {
    schema = schema[segment] as unknown as SchemaProp;

    if (!schema) {
      break;
    }
  }

  return schema;
};

const JsonSchemaTable: FC<JsonSchemaTableProps> = ({ schema }) => {
  const t = useI18n();
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
              (value.type === 'array' && value.items?.$ref) ||
              value.$ref ||
                (value.type === 'object' && (value.properties || value.additionalProperties))) && (
                <button className="bg-blue-100 text-blue-500 rounded cursor-pointer text-lg" onClick={() => handleClick(fullKey)}>
                  {expandedFields.includes(fullKey) ? <BiChevronDown /> : <BiChevronRight />}
                </button>
              )}
            </div>
          </td>
          <td>
            <div className="flex gap-2">
              {Array.isArray(value.type) ? (
                value.type.map((typeItem) => badgeColors[typeItem] ? (
                  <Badge key={typeItem} className={clsx(badgeColors[typeItem])}>
                    {typeItem}
                  </Badge>
                ) : <a key={typeItem} href={makeReferenceUrl(typeItem)}>{typeItem.split('/')[2]}</a>)
              ) : (
                <Badge className={clsx(badgeColors[value.type])}>{value.type}</Badge>
              )}
            </div>
          </td>
          <td>{requiredFields.includes(key) ? t('yes') : t('no')}</td>
          <td>{value.default ? value.default.toString() : '-'}</td>
          <td>{value.description}</td>
        </tr>,
      ];

      if (value.type === 'array' && value?.items?.anyOf) {
        rows.push(
          ...generateRows(
            { '': { type: value.items.anyOf.map((item) => (item.type || item.$ref) as unknown as string) } },
            value.required ?? [],
            `${fullKey}.`,
            true,
            depth + 1,
          ),
        );
      }

      if (
        ((value.type === 'array' && value.items?.$ref) || (value.type === 'object' && value.$ref))
        && expandedFields.includes(fullKey)
      ) {
        const refs = resolveRef(value.$ref || value.items!.$ref!, schema.definitions);

        // @ts-ignore
        rows.push(...generateRows(refs.properties!, refs.required ?? [], `${fullKey}.`, true, depth + 1));
      }

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
    <table className="table w-full">
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
