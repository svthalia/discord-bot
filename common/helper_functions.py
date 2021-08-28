import asyncio
from common.bot_logger import get_logger

logger = get_logger(__name__)


async def reply_and_delete(ctx, reply: str):
    try:
        await ctx.author.send(reply)
        await ctx.message.delete()
    except:
        if ctx.guild:
            logger.warning(
                "Could not reply to/remove old message: 'ctx.message.content=%s' by user: 'ctx.author=%s'",
                ctx.message.content,
                ctx.author,
            )


async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))
