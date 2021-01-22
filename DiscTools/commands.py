# MIT License

# Copyright (c) 2020 TEEN-BOOM

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from asyncio.coroutines import iscoroutinefunction
from typing import Callable

import discord
from discord.ext.commands import Cog
from discord.ext.commands import Command as _Command
from discord.ext.commands import Group as _Group
from discord.ext.commands.core import wrap_callback
from discord.ext.commands.errors import TooManyArguments

__all__ = (
    "CogCommandType",
    "CmdInitType",
    "CogCmdInitType",
    "Command",
    "CCmd",
    "ICommand",
    "ICCmd",
    "inject",
    "inject_cmd"
)

# PHILOSOPHY:: [I Like Grouped Commands]

## Types ##

class CogCommandType(type):
    """This is adds Cog like behavior to Commands.

    This adds functionality to implicitly register Command objects as Sub Commands.
    This Meta only picks :class:`discord.ext.commands.Command` instances
    using :func:`isinstance` builtin.

    """
    def __new__(cls, name, bases, attrs):
        subcommands = {}
        command_cls = super().__new__(cls, name, bases, attrs)
        for base in reversed(command_cls.__mro__[0:-1]):
            for name, attr in base.__dict__.items():
                if isinstance(attr, _Command):
                    if name in subcommands:
                        del subcommands[name]
                    subcommands[name] = attr
        else:
            command_cls.__fut_sub_cmds__ = subcommands
        return command_cls

class CmdInitType(type):
    """Initializes a Command during definition"""
    def __new__(cls, NamE, BaseS, AttrS, **kwargs) -> object: # type: ignore
        meta_args = ()
        if '__init_args__' in AttrS:
            meta_args = AttrS['__init_args__']
            del AttrS['__init_args__']
        clas = super().__new__(cls, NamE, BaseS, AttrS)
        inst = clas(*meta_args, **kwargs)
        return inst

# Metaclass of a metaclass or a function changing
# the super class is extremely complicated hence this.
class CogCmdInitType(CogCommandType):
    """Initializes a Cog like Cmd during definition"""
    def __new__(cls, NamE, BaseS, AttrS, **kwargs) -> object: # type: ignore
        meta_args = ()
        if '__init_args__' in AttrS:
            meta_args = AttrS['__init_args__']
            del AttrS['__init_args__']
        clas = super().__new__(cls, NamE, BaseS, AttrS)
        inst = clas(*meta_args, **kwargs)
        return inst


## Commands ##

class Command(_Group):
    """A Command

    This is the base class for all Command classes defined in this package.
    Even though this inherits from Group it won't add injected commands on definition
    Instead use CCmd or add commands on intialisation.

    Attributes
    ----------
    cogcmd : Optional[Union[:class:`disctools.commands.CCmd`, :class:`disctools.commands.ICCmd`]]
        The :class:`CogCmd` the Command belongs to.

    Note
    ----
        This differs in six ways from :class:`discord.ext.commands.Command`
            1. We declare a class instead of function.
            2. The name is set to class name if not provided.
            3. This is a subclass of :class:`discord.ext.commands.Group`
            4. We shall decorate the class with :func:`inject` to return an instance.
            5. `invoke_without_command` parameter defaults to `True`
            6. The hooks are invoked in the following order ``Bot -> Cog -> CogCmd -> Command`` for before invoke and in reverse order for after.

    Special Methods
    ---------------
    This class has four special methods.
        1. ``main``
        2. ``pre_invoke``
        3. ``post_invoke``
        4. ``on_error``

    Each of these methods is expected to be a coroutine.
    These methods have their parent as the second argument after ``self``.
    for example, if a command is a part of a cog or cog-cmd then the argument of the special methods becomes ``(self, CogOrCogCMD, ctx, *args, **kwargs)``,
    if a command is directly added to a bot then the argument becomes ``(self, ctx, *args, **kwargs)``

    Example
    -------
    .. code-block:: python

        class SomeCog(SomeCogAbstraction):
            @inject(aliases=["Test"])
            class test(Command):
                async def pre_invoke(self, cog, ctx):
                    return await SomePreInvokeAbs(cmd=self, cog=cog, ctx=ctx)

                @staticmethod
                async def main(cog, ctx, msg: str = "hi"):
                    return await ctx.send(msg)

                async def post_invoke(self, inst, ctx):
                    return await SomePostInvokeAbs(cmd=self, cog=cog, ctx=ctx)

                async def on_error(self, cog, ctx, error):
                    try:
                        await ctx.send("An error occurred")
                    except:
                        pass
    """
    def __init__(self, func=None, **kwargs):
        if func is None:
            try:
                func = self.main
            except AttributeError as err:
                raise AttributeError(
                    "Subclass of disctools.commands.Command requires main method to be defined if func argument is None") from err

        if not kwargs.get("invoke_without_command", None):
            kwargs["invoke_without_command"] = True

        super().__init__(func, **kwargs)

        if hasattr(self, "pre_invoke"):
            self.before_invoke(self.pre_invoke)
        if hasattr(self, "post_invoke"):
            self.after_invoke(self.post_invoke)

        self.name = kwargs.get('name', str(self.__class__.__name__))

        try:
            self.cogcmd
        except AttributeError:
            self.cogcmd = None

        if hasattr(self, "on_error"):
            if not iscoroutinefunction(self.on_error):
                raise TypeError('The error handler must be a coroutine.')

    # TODO:: Call this when either parent, cog, cogcmd is set. preferably without dunders
    # def __ext_init__(self) -> None:
    #     pass

    def main_command(self, func):
        """A decorator which sets the callback.

        Parameters
        ----------
        func : Coroutine
            A Coroutine which should be the command callback.

        Returns
        -------
        Coroutine
            The coroutine that was passed.
        """
        self.callback = func
        return func

    async def __call__(self, *args, **kwargs):
        if self.cogcmd is not None: # I guess this works for both decorated and class commands
            return await self.callback(self.cogcmd, *args, **kwargs)
        return await super().__call__(*args, **kwargs)

    async def dispatch_error(self, ctx, error):
        ctx.command_failed = True
        cog = self.cog
        cogcmd = self.cogcmd

        try:
            self.on_error
        except AttributeError:
            pass
        else:
            if cog:
                await self.on_error(self.cog, ctx, error)
            elif cogcmd is not None:
                await self.on_error(self.cogcmd, ctx, error)
            else:
                await self.on_error(ctx, error)

        if cogcmd is not None:
            await wrap_callback(cogcmd.on_subcommand_error)(ctx, error)

        try:
            if cog is not None:
                local = Cog._get_overridden_method(cog.cog_command_error)
                if local is not None:
                    wrapped = wrap_callback(local)
                    await wrapped(ctx, error)
        finally:
            ctx.bot.dispatch('command_error', ctx, error)

    @property
    def clean_params(self):
        """:meta private:""" # Has Been documented in dpy.
        result = self.params.copy()
        if (self.cog is not None or self.cogcmd is not None) and not isinstance(self.callback, staticmethod):
            result.popitem(last=False) # parent/self

        try:
            result.popitem(last=False) # ctx, we will have at least 2 standard params
        except Exception:
            raise ValueError('Missing context parameter') from None

        return result

    async def _parse_arguments(self, ctx: discord.ext.commands.Context):
        par = self.cog or self.cogcmd
        ctx.args = [ctx] if par is None else [par, ctx]
        ctx.kwargs = {}
        args = ctx.args
        kwargs = ctx.kwargs

        view = ctx.view
        iterator = iter(self.params.items())

        if par is not None:
            # we have ~~'self'~~ 'par' as the first parameter so just advance
            # the iterator and resume parsing
            try:
                next(iterator)
            except StopIteration:
                fmt = 'Callback for {0.name} command is missing "self" parameter.'
                raise discord.ClientException(fmt.format(self))

        # next we have the 'ctx' as the next parameter
        try:
            next(iterator)
        except StopIteration:
            fmt = 'Callback for {0.name} command is missing "ctx" parameter.'
            raise discord.ClientException(fmt.format(self))

        for name, param in iterator:
            if param.kind == param.POSITIONAL_OR_KEYWORD:
                transformed = await self.transform(ctx, param)
                args.append(transformed)
            elif param.kind == param.KEYWORD_ONLY:
                # kwarg only param denotes "consume rest" semantics
                if self.rest_is_raw:
                    converter = self._get_converter(param)
                    argument = view.read_rest()
                    kwargs[name] = await self.do_conversion(ctx, converter, argument, param)
                else:
                    kwargs[name] = await self.transform(ctx, param)
                break
            elif param.kind == param.VAR_POSITIONAL:
                while not view.eof:
                    try:
                        transformed = await self.transform(ctx, param)
                        args.append(transformed)
                    except RuntimeError:
                        break

        if not self.ignore_extra:
            if not view.eof:
                raise TooManyArguments('Too many arguments passed to ' + self.qualified_name)

    async def call_before_hooks(self, ctx: discord.ext.commands.Context):
        cog = self.cog
        cogcmd = self.cogcmd

        hook = ctx.bot._before_invoke
        if hook is not None:
            await hook(ctx)

        # call the cog local hook if applicable:
        if cog is not None:
            hook = Cog._get_overridden_method(cog.cog_before_invoke)
            if hook is not None:
                await hook(ctx)

        if cogcmd is not None:
            await cogcmd.subcommand_before_invoke(ctx)

        if self._before_invoke is not None:
            if cog:
                await self._before_invoke(self.cog, ctx) # Parent
            elif cogcmd:
                await self._before_invoke(self.cogcmd, ctx)
            else:
                await self._before_invoke(ctx)

    async def call_after_hooks(self, ctx: discord.ext.commands.Context):
        cog = self.cog
        cogcmd = self.cogcmd
        if self._after_invoke is not None:
            if cog:
                await self._after_invoke(self.cog, ctx) # Parent
            elif cogcmd:
                await self._after_invoke(self.cogcmd, ctx)
            else:
                await self._after_invoke(ctx)

        if cogcmd is not None:
            await cogcmd.subcommand_after_invoke(ctx)

        # call the cog local hook if applicable:
        if cog is not None:
            hook = Cog._get_overridden_method(cog.cog_after_invoke)
            if hook is not None:
                await hook(ctx)

        # call the bot global hook if necessary
        hook = ctx.bot._after_invoke
        if hook is not None:
            await hook(ctx)

class CCmd(Command, metaclass=CogCommandType):
    """Inherits from :class:`Command`.

    This picks up any :class:`discord.ext.commands.Command` instances as subcommands.
    Any custom metaclass must be a subclass of :class:`CogCommandType` implementing
    any features on top of it.

    It is also called ``CogCmd``
    """
    def __init__(self, func=None, **kwargs):
        super().__init__(func=func, **kwargs)
        for i in self.__fut_sub_cmds__.values():
            # -- Let errors be raised ; DESC:: [This handles all the stuff that is
            self.add_command(i) #               usually done for an instance in a cog]
            i.cogcmd = self # This Will let subcommands access the CCmd to change the command behavior
            # i.__ext_init__()

    async def on_subcommand_error(self, ctx: discord.ext.commands.Context, error):
        """|overridecoro|

        Invoked when any of the subcommands raise an error.
        """
        pass

    async def subcommand_before_invoke(self, ctx: discord.ext.commands.Context):
        """|overridecoro|

        Called before any subcommand is invoked.
        """
        pass

    async def subcommand_after_invoke(self, ctx: discord.ext.commands.Context):
        """|overridecoro|

        Called after any subcommand is invoked.
        """
        pass

# Alias
CogCmd = CCmd

class ICommand(Command, metaclass=CmdInitType):
    """This class returns an instance on definition.

    This is a subclass of :class:`Command`

    This only accepts key-word arguments, but
    unavoidable positional args shall be passed as an iterable to
    ``__init_args__``, this class attribute is destroyed after the instance of the class is created


    Example
    -------
        .. code-block:: python

            class ICmd(ICommand, name="test"):
                __init_args__ = [None] # or (None,) | this is the func argument, if None then set to self.main
                                # Useful for some subclasses

    """
    def __init__(self, func=None, **kwargs):
        try:
            super().__init__(func=func, **kwargs)
        except AttributeError:
            async def x(*args, **kwargs): pass
            self.main = x
            super().__init__(func=func, **kwargs)
            del self.main

class ICCmd(CCmd, metaclass=CogCmdInitType):
    """This is similar to :class:`ICommand` but this class inherits from :class:`CCmd` instead.

    Metaclass of subclasses must be a subclass of :class:`CogCmdInitType`

    Hence this class doesn't need any decorators to be intialized,
    as this class returns an instance on definition.
    This is equivalent to::

        @inject(name="test")
        class MyCCmd(CCmd):
            pass

    Example
    -------
    .. code-block:: python

        class CCmd(ICCmd, name="test"):
            __init_args__ = [None] # or (None,) | this is the func argument, if None then set to self.main
                              # Useful for some subclasses
            class SomeCmd(ICommand, name="first"):
                @staticmethod
                async def main(cog, ctx):
                    await ctx.send("pass")

            @inject(name="second")
            class SomeOtherCmd(Command):
                async def main(self, cog, ctx):
                    await ctx.send("pass")

    """
    def __init__(self, func=None, **kwargs):
        try:
            super().__init__(func=func, **kwargs)
        except AttributeError:
            async def x(*args, **kwargs): pass
            self.main = x
            super().__init__(func=func, **kwargs)
            del self.main


# The definition of the class is equal to ICommand = ICommand()
# Hence we must set variable(which acts like the name in python)
# To the class of the object, to allow inheritance & other class functionalities.
ICommand = ICommand.__class__ # type: ignore
ICCmd = ICCmd.__class__ # type: ignore

## Decoratores ##
def inject(**kwargs) -> Callable:
    """This is a Decorator.

    Return a class's instance

    Parameters
    ----------
    kwargs
        The Key-word arguments to use to initialise the class.

    Returns
    -------
    Callable
        The decorator which returns the instance.

    Raises
    ------
    TypeError
        If instead of a class (aka type instance) a :class:`discord.ext.commands.Command` is provided.


    Example
    -------
    .. code-block:: python

        class SomeCog(SomeSubCog):
            @inject()
            class MyCmd(Command):
                pass
    """
    def decorator(cls):
        if isinstance(cls, _Command):
            raise TypeError("Can not inject a command instance, expected a <class 'type'>")
        return cls(**kwargs)
    return decorator

def inject_cmd(inst) -> Callable:
    """This is a Decorator.

    Inject a command instance into a class.

    An alternative to discord.ext.commands.command decorator

    Parameters
    ----------
    inst : object
        A class's instance

    Returns
    -------
    Callable
        The decorator returning the instance.

    Raises
    ------
    TypeError
        If a class instance is not provided.


    Example
    -------
    .. code-block:: python

        class SomeCog(SomeSubCog):
            @inject_cmd(MySubclassedCmd(name="test"))
            async def test(self):
                pass
    """
    def decorator(cls_attr):
        if isinstance(inst, type):
            raise TypeError("Can not inject a <class 'type'> instance, expected a discord.ext.comands.Command instance.")
        return inst
    return decorator
