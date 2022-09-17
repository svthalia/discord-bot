import { Member } from './member';

export interface MemberGroup {
  pk: string;
  name: string;
  type: 'society' | 'committee' | 'board';
}

export interface MemberGroupDetails extends MemberGroup {
  chair?: string;
  members: MemberGroupMember[];
}

export interface MemberGroupMember {
  member: Member;
  chair: boolean;
  role?: string;
}
