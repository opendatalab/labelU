export function get(key: string) {
  if (typeof key !== 'string') {
    return Promise.reject(new Error('Key must be a string'));
  }

  try {
    const result = localStorage.getItem(key);

    if (result === null) {
      return null;
    } else {
      let parsedResult;
      try {
        parsedResult = JSON.parse(result);
      } catch (error) {
        return result;
      }
      return parsedResult;
    }
  } catch (err) {
    throw new Error('Error retrieving data from localStorage');
  }
}

export function set(key: string, payload: unknown) {
  try {
    if (typeof payload === 'string') {
      localStorage.setItem(key, payload);
    } else if (typeof payload === 'object') {
      localStorage.setItem(key, JSON.stringify(payload));
    } else {
      throw new Error('payload type error');
    }
  } catch (err) {
    console.warn(err);
  }
}
