DiscTools
==========

About
-----
This library is about discord.py helper classes, functions and alternatives, which can not (& should not) be included in discord.py library.

Installation
------------
*In Progress*

Example
-------
A basic Bot using DiscTools

.. code-block:: python3

    import disctools
    from discord.ext import commands
    import logging

    logging.basicConfig(
        format='%(asctime)s | %(name)s | %(levelname)s:: %(message)s',
        datefmt="[%X]",
        level=logging.INFO
    )
    Bot = disctools.Bot("~")

    @Bot.inject(name="Test", invoke_without_subcommand=False)
    class test(disctools.CCmd):
        async def main(self, ctx):
            await ctx.send("PASS")
        
        async def subcommand_before_invoke(self, ctx):
            await ctx.send("Test before hook PASS")
        
        async def subcommand_after_invoke(self, ctx):
            await ctx.send("Test after hook PASS")

        @disctools.inject()
        class First(disctools.Command):
            # Usage: `[p]Test First Hi!`
            async def pre_invoke(self, parent, ctx):
                return await ctx.send("Preparing...")

            async def main(self, parent, ctx, *, msg: str = "PASSS"):
                return await ctx.send(msg)

            async def post_invoke(self, parent, ctx):
                return await ctx.send("Exiting...")

        class Second(disctools.ICommand, aliases=["s"]):
            # Usage: `[p]Test [Second|s] Hi!`
            async def main(self, parent, ctx, *, msg: str = "PASSS"):
                """Interact with discord here, you may write everthing here."""
                return await ctx.send(msg)

            async def logic(self, msg):
                """Platform agnostic implementation of the command

                This is not enforced but recommended, so that it ts easier to migrate from discord's platform"""
                return msg

        # You may do this but, without disctools.Command or else you lose the self argument.
        @commands.command(cls=disctools.Command, name="Third")
        async def third(self, ctx, *, msg: str = "PASSS"):
            return await ctx.send(msg)

    Bot.run("<TOKEN>")


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   src/Commands.rst
   src/Bot.rst
   src/Context.rst
   src/Abstractions.rst
   src/Experimental.rst


Indices and tables
------------------

* :ref:`genindex`