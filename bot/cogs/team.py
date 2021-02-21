from random import shuffle
import csv

from discord import Member, VoiceChannel, errors
from discord.ext import commands, tasks
from common.discord_helper import get_member_list, string_to_role

from common.bot_logger import get_logger
from common.helper_functions import reply_and_delete

logger = get_logger(__name__)


class Team:
    def __init__(self, name: str):
        self.__name = name
        self.__members = []
        self.__size = 0
        self.__vc = None

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name

    @property
    def size(self):
        return self.__size

    @property
    def members(self):
        return self.__members

    def add_member(self, member: Member):
        if member not in self.__members:
            self.__members.append(member)
            self.__size += 1

    def rem_member(self, member: Member):
        for m in self.__members:
            if m.id == member.id:
                self.__members.remove(m)
                self.__size -= 1

    @property
    def vc(self):
        return self.__vc

    @vc.setter
    def vc(self, vc: VoiceChannel):
        self.__vc = vc


class TeamCog(commands.Cog, name="Team commands"):
    def __init__(self, bot):
        self.bot = bot
        self.teams = []
        logger.info("Team cog initialized")
        self.clean_up_vc.start()

    def create_team(self, team, name):
        i = 2
        new_name = name
        while new_name in [t.name for t in self.teams]:
            new_name = name + "." + str(i)
            i += 1
        teamObj = Team(new_name)
        self.teams.append(teamObj)

        for member in team:
            for t in self.teams:
                for m in t.members:
                    if member.id == m.id:
                        t.rem_member(member)
            teamObj.add_member(member)

    @commands.group(name="team", invoke_without_command=True)
    async def team(self, ctx):
        await reply_and_delete(ctx, "'team' needs a sub-command!")
        await ctx.send_help(self.team)

    @team.command(help="Create one or multiple team(s)")
    @commands.has_permissions(administrator=True)
    async def create(self, ctx, *teams):
        for name in teams:
            existing_t = False
            for t in self.teams:
                if t.name == name:
                    existing_t = True
                    await reply_and_delete(ctx, "Team " + name + " already exists.")
            if not existing_t:
                self.teams.append(Team(name))
                await reply_and_delete(ctx, "Team " + name + " was added!")

    @team.command(help="Remove one or multiple team(s)")
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, *teams):
        for name in teams:
            team_found = False
            for t in self.teams:
                if t.name == name:
                    team_found = True
                    try:
                        if t.vc:
                            await t.vc.delete()
                        self.teams.remove(t)
                        await reply_and_delete(ctx, "Team " + name + " was removed.")
                    except:
                        await reply_and_delete(
                            ctx, "Could not remove team " + name + "."
                        )
            if not team_found:
                await reply_and_delete(
                    ctx, "Could not remove team " + name + ", does it exist?"
                )

    @team.command(help="Rename a team")
    @commands.has_permissions(administrator=True)
    async def rename(self, ctx, old: str, new: str):
        for t in self.teams:
            if t.name == old:
                t.name = new
                return
        await reply_and_delete(ctx, "Could not find team " + old)

    @team.command(name="list", help="Show list of teams")
    async def list_teams(self, ctx):
        t_list = ""
        for t in self.teams:
            t_list += t.name + ", "
        await ctx.send(t_list[:-2])

    @team.command(help="Show members of one or multiple team(s)")
    async def show(self, ctx, *teams):
        for team in teams:
            for t in self.teams:
                if t.name == team:
                    if t.size > 0:
                        names = ""
                        for m in t.members:
                            names += m.display_name + ", "
                        await reply_and_delete(
                            ctx, "Team " + team + " has members: " + names[:-2]
                        )
                    else:
                        await reply_and_delete(ctx, "Team " + team + " is empty!")

    @team.command(help="Add members to a team")
    @commands.has_permissions(administrator=True)
    async def add_member(self, ctx, t_name: str, *members):
        members, not_found = get_member_list(ctx, members)
        if not_found != "":
            await reply_and_delete(ctx, "Could not find member(s): " + not_found[:-2])

        for member in members:
            already_in_team = False
            team = None
            for t in self.teams:
                for m in t.members:
                    if member.id == m.id:
                        await reply_and_delete(
                            ctx,
                            member.display_name
                            + " is already in team "
                            + t.name
                            + ", remove them first.",
                        )
                        already_in_team = True
                if t.name == t_name:
                    team = t
            if not already_in_team:
                if not team:
                    await reply_and_delete(ctx, "Team " + t_name + " was not found.")
                else:
                    try:
                        team.add_member(member)
                    except:
                        await reply_and_delete(ctx, "Error while adding member.")

    @team.command(help="Remove members from their team")
    @commands.has_permissions(administrator=True)
    async def remove_member(self, ctx, *members):
        members, not_found = get_member_list(ctx, members)
        if not_found != "":
            await reply_and_delete(ctx, "Could not find member(s): " + not_found[:-2])
        for member in members:
            removed = False
            for t in self.teams:
                for m in t.members:
                    if member.id == m.id:
                        try:
                            t.rem_member(member)
                            removed = True
                            await reply_and_delete(
                                ctx,
                                member.display_name
                                + " was successfully removed from team "
                                + t.name
                                + ".",
                            )
                        except:
                            logger.error(
                                "Could not remove "
                                + member.display_name
                                + " from "
                                + t.name
                            )
                            await reply_and_delete(
                                ctx, "Error in removing member from team."
                            )
            if not removed:
                await reply_and_delete(
                    ctx, member.display_name + " was not in any team."
                )

    @team.command(help="Move all connected users to a voice channel per team")
    @commands.has_permissions(administrator=True)
    async def voice(self, ctx):
        original_vc = ctx.author.voice.channel
        for team in self.teams:
            if not team.vc:
                try:
                    team.vc = await ctx.guild.create_voice_channel(
                        team.name, category=original_vc.category
                    )
                except errors.Forbidden:
                    await reply_and_delete(
                        ctx,
                        "The bot needs permission to manage channels.",
                    )
            for member in team.members:
                if member.voice and member.voice.channel == original_vc:
                    try:
                        await member.move_to(team.vc)
                    except errors.Forbidden:
                        await reply_and_delete(
                            ctx,
                            "The bot needs permission to move members.",
                        )

    @team.command(help="Move all members in a team channel to given voice channel")
    @commands.has_permissions(administrator=True)
    async def gather(self, ctx, vc: VoiceChannel):
        for team in self.teams:
            if team.vc:
                for member in team.vc.members:
                    await member.move_to(vc)
        await ctx.send("Successfully moved members")

    @team.command(name="import", help="Import a csv of users attached to the message")
    @commands.has_permissions(administrator=True)
    async def import_csv(self, ctx):
        if len(ctx.message.attachments) == 0:
            await ctx.send(
                "We could not find an attachment in your message!\n"
                + "Upload a file with the following formatting:\n"
                + "```Team 1,Alice#1234,Bob#4321\nTeam 2,Eve#0987,Dave#6758```"
            )
        if len(ctx.message.attachments) > 1:
            await ctx.send("You provided multiple attachments, please only send one.")

        self.reset(ctx)

        content = await ctx.message.attachments[0].read()
        reader = csv.reader(content.decode("utf-8").split("\n"), delimiter=",")
        for row in reader:
            await self.create(ctx, *[row[0]])
            await self.add_member(ctx, row[0], *row[1:])

        await ctx.send("Members successfully imported.")

    @team.command(help="Reset all teams")
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx):
        for team in self.teams:
            if team.vc:
                await team.vc.delete()
                team.vc = None
        self.teams = []

        await ctx.send("Team successfully reset.")

    @team.group(
        name="divide",
        invoke_without_command=True,
        help="Get help for team divide commands",
    )
    async def divide(self, ctx):
        await reply_and_delete(ctx, "'team divide' needs a sub-command!")
        await ctx.send_help(self.team.divide)

    @divide.command(help="Split current voice channel into `n` groups")
    @commands.has_permissions(administrator=True)
    async def random(self, ctx, n: str):
        # handle parameter
        try:
            n = int(n)
        except:
            await reply_and_delete(ctx, "Number of groups should be an integer value.")
            return

        vc = ctx.author.voice.channel
        if not vc:
            await reply_and_delete(
                ctx, "You have to be connected to a voice channel to use this command."
            )
            return

        connected = [m for m in vc.members if not m.bot]
        if len(connected) < n:
            await reply_and_delete(
                ctx,
                f"There are less than {n} users connected to your voice channel.",
            )
            return

        shuffle(connected)
        divided_teams = [
            [connected[i] for i in range(len(connected)) if (i % n) == r]
            for r in range(n)
        ]

        i = 0
        for t in divided_teams:
            self.create_team(t, "Team " + str(i))
            i += 1

    @divide.command(help="Split current voice channel into teams based on their role.")
    @commands.has_permissions(administrator=True)
    async def role(self, ctx, *roles):
        vc = ctx.author.voice.channel
        if not vc:
            await reply_and_delete(
                ctx, "You have to be connected to a voice channel to use this command."
            )
            return
        connected = [m for m in vc.members if not m.bot]
        roles = [await string_to_role(ctx, arg) for arg in roles]

        divided_teams = [[] for _ in range(len(roles))]
        for c in connected:
            placed = False
            for i in range(len(roles)):
                if roles[i] in c.roles and not placed:
                    divided_teams[i].append(c)
                    placed = True

        i = 0
        for t in divided_teams:
            self.create_team(t, roles[i].name)
            i += 1

    @tasks.loop(minutes=1)
    async def clean_up_vc(self):
        for team in self.teams:
            if team.vc:
                if len(team.vc.members) == 0:
                    await team.vc.delete()
                    team.vc = None

    @clean_up_vc.before_loop
    async def before_clean_up_vc(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(TeamCog(bot))
