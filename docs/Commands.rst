Commands
========
These aim to provide more control over commands

.. currentmodule:: disctools.commands

Command Types
-------------
.. autoclass:: CogCommandType

Commands
--------

.. autoclass:: Command
    :no-undoc-members:
    :members:

.. autoclass:: CCmd
    :members:

.. autoclass:: CogCmd

.. note::

    :class:`Command` & :class:`CCmd` are generic in :class:`discord.ext.commands.Context`,
    similar to `discord-ext-typed-commands <https://github.com/bryanforbes/discord-ext-typed-commands/>`_
    Consider the following example:

    .. code-block:: python3

        class echo(disctools.Command[MyContext]):
            ...

        CT = TypeVar('CT', bound=discord.ext.commands.Context)
        class MyCogCmd(disctools.CCmd[CT]):
            def MySpecialMethod(self, ctx: CT) -> CT:
                ...
            ...

        def setup(bot: MyBot):
            bot.add_command(MyCogCmd[MyContext](name="test"))
            ...

Decorators
----------

.. autodecorator:: inject

Differences
-----------
Differences from discord.py commands

Checks
******
Due to the way discord.py's decorators are written they can be used on the instance of the Command as well as the main method

Example
~~~~~~~

    .. code-block:: python3

        # note that decorator is above the inject decorator
        @discord.ext.commands.guild_only()
        @disctools.inject(aliases=["test"])
        class Test(disctools.Command):
            @discord.ext.commands.is_owner()
            async def main(self, ctx, msg):
                return await ctx.send(msg)

            async def on_error(self, ctx, error):
                if isinstance(error, discord.ext.commands.NotOwner):
                    await ctx.send("You are not my Owner!")
                elif isinstance(error, discord.ext.commands.NoPrivateMessage):
                    await ctx.send("I don't like DMs")

You may apply decorators from :mod:`discord.ext.commands` on either the method or the instance.

.. note::
    You can not apply any decorators on the class. For example see the following.

        .. code-block:: python3

            @disctools.inject(...)
            @discord.ext.commands.guild_only() # applied before initialiasation
            class Test(disctools.Command):
                ...

    Will not work, since the check is applied on the class.


Pre/Post Invoke Hook Order
**************************
Conventionally, the hooks are invoked in the following order::

    Command Specific before invoke hook
    Cog before invoke hook
    Bot before invoke hook
    main (Command)
    Command Specific after invoke hook
    Cog after invoke hook
    Bot after invoke hook


But, in DiscTools the hooks are invoked in the following order::

    Bot before invoke hook
    Cog or CogCmd before invoke hook
    Command Specific before invoke hook
    main (Command)
    Command Specific after invoke hook
    Cog or CogCmd after invoke hook
    Bot after invoke hook
