import Undici from 'undici';

const { THALIA_SERVER_URL } = process.env;
const THALIA_API_URL = THALIA_SERVER_URL + 'api/v2';

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
  return response.body.json();
};

export const getAuthenticatedMember = async (token: string) => {
  return getMember(token, 'me');
};

export const getMember = async (token: string, id: string | number) => {
  const response = await Undici.request(`${THALIA_API_URL}/members/${id}/`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  console.log(response);

  return await response.body.json();
};
