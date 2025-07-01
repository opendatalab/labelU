declare interface Window {
  __REDUX_DEVTOOLS_EXTENSION_COMPOSE__: () => any;
}

declare interface ObjectConstructor {
  keys: <T>(o: T) => (keyof T)[];
}
