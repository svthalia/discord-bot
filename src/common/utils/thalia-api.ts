import Undici from 'undici';
import { HttpMethod } from 'undici/types/dispatcher';
import { Member } from '../models/member';
import { MemberGroupDetails } from '../models/memberGroup';
import { settle } from './async';

const { THALIA_SERVER_URL } = process.env;
const THALIA_API_URL = THALIA_SERVER_URL + 'api/v2';

const request = async (token: string, path: string, method: HttpMethod = 'GET') => {
  const response = await Undici.request(`${THALIA_API_URL}${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  if (response.statusCode > 200) {
    console.error(path, method);
    console.error(response.statusCode);
    console.error(await response.body.text());
  }

  return response;
};

export const getBackendToken = async () => {
  const { THALIA_CLIENT_ID, THALIA_CLIENT_SECRET } = process.env;
  const response = await Undici.request(`${THALIA_SERVER_URL}user/oauth/token/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Accept: 'application/json; charset=UTF-8'
    },
    body: `grant_type=client_credentials&client_id=${THALIA_CLIENT_ID}&client_secret=${THALIA_CLIENT_SECRET}`
  });
  const result = await response.body.json();
  return result['access_token'];
};

export const getAuthenticatedMember = async (token: string) => {
  return getMember(token, 'me');
};

export const getMember = async (token: string, id: string | number): Promise<Member> => {
  const response = await request(token, `/members/${id}/`);
  return response.body.json();
};

export const getMemberGroups = async (token: string): Promise<MemberGroupDetails[]> => {
  const groups = await getPaginatedResult(token, `/activemembers/groups/`);
  return settle(groups.map((group) => getIndividualGroup(token, group['pk'])));
};

export const getMembers = async (token: string): Promise<Member[]> => {
  return getPaginatedResult(token, `/members/`);
};

const getIndividualGroup = async (token: string, id: string): Promise<MemberGroupDetails> => {
  const response = await request(token, `/activemembers/groups/${id}/`);
  const data = (await response.body.json()) as Omit<MemberGroupDetails, 'chair'>;
  return {
    ...data,
    chair: (data.members || []).find((member) => member.chair)?.member
  };
};

export const getPaginatedResult = async <T>(token: string, path: string): Promise<T[]> => {
  const response = await request(token, `${path}?limit=100`);
  const data = await response.body.json();

  if ('detail' in data && 'throttle' in data.detail) {
    return [];
  }
  const results = data['results'];

  if (data.count > 100) {
    const num = Math.ceil(data.count / 100);

    const getNext = async (i) => {
      const response = await request(token, `${path}?limit=100&offset=${100 * i}`);

      const data = await response.body.json();
      return data.results;
    };

    const nexts = await settle<any>(Array.from(Array(num).keys()).map((x) => getNext(x + 1)));
    nexts.forEach((next) => results.append(next));
  }

  return results;
};
