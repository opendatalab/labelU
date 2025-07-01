export const jsonParse = (value: string): any => {
  return JSON.parse(value, (k: any, v: any) => {
    try {
      // 将正则字符串转成正则对象
      if (eval(decodeURIComponent(v)) instanceof RegExp) {
        return eval(decodeURIComponent(v));
      }
      return v;
    } catch (e) {
      return v;
      // nothing
    }
  });
};

export const jsonStringify = (value: Record<string, unknown>, type = 2): any => {
  return JSON.stringify(
    value,
    (k: any, v: any) => {
      if (v instanceof RegExp) {
        return encodeURIComponent(v.toString());
      }
      return v;
    },
    type,
  );
};

/**
 * 深度比较两个对象是否相等
 * @method compare
 * @param oldData 需要比较的值
 * @param newData 需要比较的值
 * @return {Boolean} 判断后的结果
 */
export const compare = function (...args: [string | any[], string | any[]]) {
  const oldData = args[0];
  const newData = args[1];

  if (oldData === newData) {
    return true;
  }
  // @ts-ignore
  const arg = Array.prototype.slice.call(...args);
  const objCall = (obj: any, string: string) => Object.prototype.toString.call(obj) === `[object ${string}]`;
  if (arg.every((obj) => objCall(obj, 'Object')) && Object.keys(oldData).length === Object.keys(newData).length) {
    // @ts-ignore
    for (const key in oldData) {
      if (oldData.hasOwnProperty(key) && !compare(oldData[key], newData[key])) return false;
    }
  } else if (arg.every((obj) => objCall(obj, 'Array')) && oldData.length === newData.length) {
    // @ts-ignore
    for (const key in oldData) {
      if (!compare(oldData[key], newData[key])) return false;
    }
  } else {
    return false;
  }
  return true;
};

export function downloadFromUrl(url: string, name?: string) {
  const link = document.createElement('a');
  link.href = url;

  if (name) {
    link.setAttribute('download', name);
  }

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export function getThumbnailUrl(url: string) {
  return url.replace(/(.*)(\..*)$/, '$1-thumbnail$2');
}
