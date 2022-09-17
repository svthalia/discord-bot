export interface Member {
  pk: string;
  membership_type: 'member' | 'benefactor' | 'honorary member';
  profile: {
    display_name: string;
    short_display_name: string;
    starting_year: number;
    profile_description: string;
  };
}

export interface MemberWithDiscord extends Member {
  discord: string;
}

export interface MemberWithRoles extends MemberWithDiscord {
  roles: string[];
}
