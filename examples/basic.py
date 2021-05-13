# This is free and unencumbered software released into the public domain.

# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# For more information, please refer to <https://unlicense.org>

import disctools
from discord.ext import commands
import logging

logging.basicConfig(
    format='%(asctime)s | %(name)s | %(levelname)s:: %(message)s',
    datefmt="[%X]",
    level=logging.INFO
)
Bot = disctools.Bot("~")

@Bot.inject(name="echo", invoke_without_subcommand=False)
class test(disctools.CCmd):
    async def main(self, ctx, msg: str = ";-;"):
        """Echo? anyone there? - [p]echo [msg]"""
        await ctx.send(msg)

    async def subcommand_before_invoke(self, ctx):
        await ctx.send("Test before hook PASS")

    async def subcommand_after_invoke(self, ctx):
        await ctx.send("Test after hook PASS")

    @disctools.inject(name="becho")
    class better_echo(disctools.Command):
        async def pre_invoke(self, ctx):
            return await ctx.send("I am gonna echo")

        async def main(self, ctx, *, msg: str = "*silence*"):
            """Echo but better! - [p]echo becho [msg]"""
            return await ctx.send(msg)

        async def post_invoke(self, ctx):
            return await ctx.send("I echoed you!")

    # You may do this but, without disctools.Command you lose the self argument.
    @commands.command(cls=disctools.Command, name="secho")
    async def simple_echo(self, ctx, *, msg: str = "*silence echoes*"):
        """Echo but dead simple - [p]echo secho [msg]"""
        return await ctx.send(msg)

Bot.run("<TOKEN>")
