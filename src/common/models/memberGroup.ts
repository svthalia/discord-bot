import { Member } from './member';

export enum MemberGroupType {
  SOCIETY = 'society',
  COMMITTEE = 'committee',
  BOARD = 'board'
}

export interface MemberGroup {
  pk: string;
  name: string;
  type: MemberGroupType;
}

export interface MemberGroupDetails extends MemberGroup {
  chair?: Member;
  members: MemberGroupMember[];
}

export interface MemberGroupMember {
  member: Member;
  chair: boolean;
  role?: string;
}
