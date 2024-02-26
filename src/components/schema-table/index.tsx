import { useState, type FC } from 'react';
import { Link } from 'react-router-dom';
import { BiChevronRight } from '@react-icons/all-files/bi/BiChevronRight';
import { BiChevronDown } from '@react-icons/all-files/bi/BiChevronDown';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

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
const typeBadgeMap = {
  string: 'badge-secondary',
  number: 'badge-success',
  boolean: 'badge-error',
  array: 'badge-primary',
  object: 'badge-neutral',
  null: 'badge-neutral',
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
  return `/schema/reference/${getReferenceName(ref)}`;
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
              (value.type === 'array' && value.items?.$ref) ||
              value.$ref ||
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
                value.type.map((typeItem) => typeBadgeMap[typeItem] ? (
                  <div key={typeItem} className={clsx('badge badge-outline', typeBadgeMap[typeItem])}>
                    {typeItem}
                  </div>
                ) : <Link key={typeItem} to={makeReferenceUrl(typeItem)}>{typeItem.split('/')[2]}</Link>)
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
