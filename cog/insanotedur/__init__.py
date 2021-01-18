"""Bot avec le cog pour Insanotedur"""

from .insanotedur import Insanotedur


async def setup(bot):
    bot.add_cog(await Insanotedur.create(bot))
