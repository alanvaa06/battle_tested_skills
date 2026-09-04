import { getUser } from '../../../services/user';

export async function GET(): Promise<Response> {
  return new Response(await getUser('1'));
}
