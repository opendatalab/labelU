export interface WebSocketClientOptions {
  reconnectInterval: number;
  maxReconnectAttempts: number;
}

export default class WebSocketClient {
  public url: string;
  public options: WebSocketClientOptions;
  public reconnectAttempts: number;
  public handlers: Map<string, ((data?: any) => void)[]> = new Map();
  public ws: WebSocket | null = null;
  private shouldReconnect: boolean = true;

  constructor(url: string, options = {}) {
    this.url = url;
    this.options = {
      reconnectInterval: 3000,
      maxReconnectAttempts: 5,
      ...options,
    };
    this.reconnectAttempts = 0;
    this.connect();
    // Heartbeats
    this.on('ping', () => this.send('pong', null));
  }

  public connect() {
    this.shouldReconnect = true;
    this.ws = new WebSocket(this.url);
    this._setupEventHandlers();
  }

  public disconnect() {
    this.shouldReconnect = false;
    if (this.ws) {
      this.ws.close();
    }
  }

  private _setupEventHandlers() {
    if (!this.ws) {
      return;
    }
    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      this.emit('connect');
    };

    this.ws.onclose = () => {
      this.emit('disconnect');
      if (this.shouldReconnect) {
        this.reconnect();
      }
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.emit(message.type, message.data);
    };

    this.ws.onerror = (error) => {
      this.emit('error', error);
    };
  }

  public destroy() {
    this.shouldReconnect = false;
    this.disconnect();
    this.handlers.clear();
  }

  public reconnect() {
    if (this.reconnectAttempts < this.options.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => this.connect(), this.options.reconnectInterval);
    }
  }

  public on(event: string, handler: (data?: any) => void) {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, []);
    }

    this.handlers.get(event)!.push(handler);
  }

  public off(event: string, handler: (data?: any) => void) {
    if (this.handlers.has(event)) {
      this.handlers.set(
        event,
        this.handlers.get(event)!.filter((h) => h !== handler),
      );
    }
  }

  public emit(event: string, data: any = null) {
    if (this.handlers.has(event)) {
      this.handlers.get(event)!.forEach((handler) => handler(data));
    }
  }

  public send(type: string, data: any) {
    if (!this.ws) {
      return;
    }

    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data }));
    }
  }
}
