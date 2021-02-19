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
These classes use meta classes to avoid using the :func:`disctools.commands.inject`
In short: "These classes return an instance on definition"

Why use these?
**************
If you write many commands then :func:`disctools.commands.inject` may become repetitive
hence you can trade some readability and use implicit instance creation provided by these classes.

.. note::
    You do not need to use any decorators with these classes.
    But if any [decorators] must be used then expect an instance instead of a class.

.. warning::
    Since these classes initialize on definition, they may cause errors when inheriting from them
    hence you may instead create a new class and set the metaclass as a  :class:`disctools.commands.CmdInitType` or  :class:`disctools.commands.CogCmdInitType`
    and set the variable as the `__class__` attribute of the instance.

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


But decorating the class is recommended.

Instance Checks
---------------
All the Commands are a subclass of :class:`disctools.commands.Command`, hence to check if a command is a disctools command
You may use ``isinstance(cmd, disctools.Command)``

Parameters
----------
The parameters passed to a disctools Command slightly differ from :class:`discord.ext.commands.Command`
To understand the difference we first need to define two terms regarding commands.

Signature
    The signature or parameters of a function are determined by the `main` method. it ignores

Parent
    Every command in a :class:`discord.ext.commands.Cog` or a CogCmd (aka :class:`disctools.CCmd` & :class:`disctools.ICCmd`) has access to the Cog or CogCmd.
    | For those who understand python better than english.

    .. code-block:: python3

        class MyCCmd(disctools.CCmd): # This could be a Cog
            @disctools.inject()
            class MyCmd(disctools.Command):
                async def main(self, parent, ctx, firstArg):
                    assert isinstance(parent, disctools.CCmd)
                    assert isinstance(ctx, commands.Context)
                    await ctx.send(firstArg)

    This is true for the `main` method and other methods such as:
        * :meth:`disctools.commands.Command.on_error`
        * :meth:`disctools.commands.Command.pre_invoke`
        * :meth:`disctools.commands.Command.post_invoke`

Hence every DiscTools command will be passed a `parent` argument between `ctx` & `self`, if it (the Command) has a `parent`

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
