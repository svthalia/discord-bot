import { SlashCommand, CommandOptionType, SlashCreator, CommandContext } from 'slash-create';

export default class HelloCommand extends SlashCommand {
  constructor(creator: SlashCreator) {
    super(creator, {
      name: 'hello',
      description: 'Says hello to you.',
      options: [
        {
          type: CommandOptionType.STRING,
          name: 'food',
          description: 'What food do you like?'
        }
      ]
    });
  }

  async run(ctx: CommandContext) {
    const name = ctx.member.displayName ?? ctx.user.username;
    return {
      content: ctx.options.food ? `You like ${ctx.options.food}? Nice!` : `Hello, ${name}!`,
      ephemeral: true
    };
  }
}
