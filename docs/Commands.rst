Commands
========
These aim to provide more control over commands

Command Types
-------------
.. autoclass:: disctools.commands.CogCommandType

.. autoclass:: disctools.commands.CmdInitType

.. autoclass:: disctools.commands.CogCmdInitType

Commands
--------
.. autoclass:: disctools.commands.Command
    :no-undoc-members:
    :members:

.. autoclass:: disctools.commands.CCmd
    :members:

.. autoclass:: disctools.commands.CogCmd


Pre-Injected Commands
---------------------
Abstract
********
These classes use meta-classes to avoid using the :func:`disctools.commands.inject`
In short: "These classes return an instance on definition"

Why use these?
**************
If you write many commands then :func:`disctools.commands.inject` may become repetitive
hence you can trade some readability and use implicit instance creation provided by these classes.

.. note::
    In case the need to subclass these classes arises, you may simply do the following.

    .. code-block:: py

        class MyICmd(metaclass=CmdInitType):
            pass

        MyICmd = MyICmd.__class__

.. autoclass:: disctools.commands.ICommand

.. autoclass:: disctools.commands.ICCmd

Decorators
----------

.. autofunction:: disctools.commands.inject

.. autofunction:: disctools.commands.inject_cmd


Differences
===========
Differences from discord.py commands

Checks
------
Due to the way discord.py's decorators are written they can be used on the instance of the Command as well as the main method

Example
*******

    .. code-block:: python3

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

You may apply decorators from :mod:`discord.ext.commands` on either the method or the class

Instance Checks
---------------
All the Commands are a subclass of :class:`disctools.commands.Command`, hence to check if a command is a disctools command
You may use ``isinstance(cmd, disctools.Command)``

Pre/Post Invoke Hook Order
--------------------------
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
