import { isEqual } from 'lodash-es';
import type { Dispatch, SetStateAction } from 'react';
import { useCallback, useLayoutEffect, useEffect, useRef, useState } from 'react';

export interface Option<Data> {
  threshold?: number;
  afterFetching?: (data: Data) => void;
  isEnd?: (allData?: Data) => boolean;
  watch?: any;
  beforeFetching?: () => Promise<unknown>;
}

// type TData = Record<string, any>[];

/**
 * 滚动加载
 * @param service 请求函数
 * @param container 滚动元素容器，不传默认使用body
 * @param options
 * @returns
 */
export function useScrollFetch<T extends any[] | undefined>(
  service: (isReset: boolean) => Promise<T>,
  container?: HTMLDivElement | (() => HTMLDivElement | null) | undefined,
  options?: Option<T>,
): [T, boolean, Dispatch<SetStateAction<T>>, () => Promise<unknown>] {
  const { threshold, afterFetching, isEnd, watch } = {
    threshold: 0,
    ...options,
  };

  if (typeof isEnd !== 'function') {
    throw Error('options.isEnd must be a function');
  }

  const [isLoading, toggleLoading] = useState<boolean>(false);
  const [data, setData] = useState<T>([] as unknown as T);
  const watchedValue = useRef<any>(watch);
  const isFetching = useRef<boolean>(false);
  const initialized = useRef<boolean>(false);

  const wrappedService = useCallback(
    async (reset?: boolean) => {
      if (typeof options?.beforeFetching === 'function') {
        await options.beforeFetching();
      }

      isFetching.current = true;
      toggleLoading(true);
      const promise = service(!!reset);

      if (!(promise instanceof Promise)) {
        console.warn('service must be an async function');
        return Promise.resolve(promise);
      }
      return promise
        .then((response) => {
          if (typeof afterFetching === 'function') {
            afterFetching(response);
          }

          isFetching.current = false;

          if (reset) {
            setData(response);
          } else if (response) {
            setData(data?.concat(response) as T);
          }
          toggleLoading(false);
        })
        .catch(() => {
          toggleLoading(false);
        });
    },
    [afterFetching, data, options, service],
  );

  // 第一次加载
  useEffect(() => {
    if (!initialized.current) {
      wrappedService();

      initialized.current = true;
    }
  }, [wrappedService]);

  // 监听watch变化，初始时不应该触发加载，有变化后，需要重置数据
  useEffect(() => {
    if (typeof watch === 'undefined' || watch === null) {
      return;
    }

    const shouldReload = Array.isArray(watchedValue.current)
      ? watchedValue.current.some((item, index) => !isEqual(item, watch[index]))
      : watchedValue.current !== watch;

    if (shouldReload) {
      wrappedService(true);
      watchedValue.current = watch;
    }
  }, [watch, wrappedService]);

  const handleOnScroll = useCallback(() => {
    const _container = typeof container === 'function' ? container() : container;
    const shouldFetch =
      (!_container
        ? document.documentElement.scrollHeight - window.scrollY - document.body.offsetHeight <= threshold
        : _container.scrollHeight - _container.scrollTop - _container.offsetHeight <= threshold) && !isEnd(data);

    if (shouldFetch && !isFetching.current) {
      wrappedService();
    }
  }, [container, data, isEnd, threshold, wrappedService]);

  // 添加事件监听
  useLayoutEffect(() => {
    const _container = typeof container === 'function' ? container() : container;
    (_container || window).addEventListener('scroll', handleOnScroll, true);

    return () => {
      (_container || window).removeEventListener('scroll', handleOnScroll, true);
    };
  }, [container, handleOnScroll]);

  return [data, isLoading, setData, wrappedService];
}
