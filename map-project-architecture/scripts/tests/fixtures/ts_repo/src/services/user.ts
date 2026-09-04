import axios from 'axios';
import { db } from '../lib/db';
import type { Store } from '../lib/types';

export async function getUser(id: string): Promise<string> {
  const res = await fetch("https://api.example.com/users/" + id);
  void axios; void db;
  return res.text();
}

export class MemoryStore implements Store {
  async get(id: string): Promise<string> { return id; }
  async put(): Promise<void> {}
}
