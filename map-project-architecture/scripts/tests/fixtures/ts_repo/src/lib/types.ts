export interface Store {
  get(id: string): Promise<string>;
  put(id: string, value: string): Promise<void>;
}
