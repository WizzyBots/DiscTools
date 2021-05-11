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
from __future__ import annotations

from asyncio.coroutines import iscoroutinefunction
from typing import Callable, Union, TYPE_CHECKING
from inspect import isawaitable, ismethod

import discord
from discord.ext.commands import Cog
from discord.ext.commands import Command as _Command
from discord.ext.commands import Group as _Group
from discord.ext.commands.core import wrap_callback
from discord.ext.commands.errors import TooManyArguments

if TYPE_CHECKING:
    from discord.ext.commands.core import GroupMixin

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

def _doc_only(func):
    func.__doc_only__ = None
    return func

# PHILOSOPHY:: [I Like Grouped Commands]
## Types ##

class CogCommandType(type):
    """This is adds Cog like behavior to Commands.

    This adds functionality to implicitly register Command objects as Sub Commands.
    This Meta only picks :class:`discord.ext.commands.Command` instances
    using :func:`isinstance` builtin.

    """
    def __new__(cls, name, bases, attrs, **kwargs):
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
    def __new__(cls, name, bases, attrs, **kwargs):
        meta_args = ()
        if '__init_args__' in attrs:
            meta_args = attrs['__init_args__']
            del attrs['__init_args__']

        klass = super().__new__(cls, name, bases, attrs)
        if kwargs.get("_root", False):
            try:
                delattr(klass.main, "__doc_only__") # type: ignore
            except AttributeError:
                pass
        return klass(*meta_args, **kwargs)

class CogCmdInitType(CmdInitType, CogCommandType):
    """Initializes a Cog like Cmd during definition"""
    pass


## Commands ##

class Command(_Command):
    """A Command

    This is the base class for all Command classes defined in this package.

    Attributes
    ----------
    cogcmd : Optional[:class:`disctools.commands.CCmd`]
        The :class:`CogCmd` the Command belongs to.

    Example
    -------
    .. code-block:: python

        class SomeCog(SomeCogAbstraction):
            def __str__(self): return "SomeCog"

            @inject(aliases=["Test"])
            class test(Command):
                async def pre_invoke(self, ctx):
                    await ctx.send(str(self.cog))

                async def main(self, ctx, msg: str = "hi"):
                    return await ctx.send(self.logic(msg))

                def logic(self, s: str, me: bool = False) -> str:
                    return ("Me: " * me) + ("You: " * (not me)) + s

                async def post_invoke(self, ctx):
                    await ctx.send(self.logic("Yes", True))

                async def on_error(self, ctx, error):
                    try:
                        await ctx.send(f"An error occurred in {self} owned by {self.owner}")
                    except:
                        pass

    Which will output the following for the invocation string ``test``::

        SomeCog
        You: hi
        Me: Yes

    or when an error occurs::

        An error occurred in Test owned by SomeCog

    """
    def __init__(self, func=None, **kwargs):
        if func is None:
            func = self.main
            if hasattr(func, "__doc_only__"):
                raise ValueError("main method must be overridded for subclass of disctools.commands.Command if func argument is None")

        kwargs.setdefault("invoke_without_command", True)
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

    async def __call__(self, *args, **kwargs):
        if self.cog is not None and not isinstance(self.callback, staticmethod):
            return await self.callback(self.cog, *args, **kwargs)
        return await self.callback(*args, **kwargs)

    def __init_subclass__(cls, **kwargs) -> None:
        if kwargs.get("_root", False):
            print(cls)
            strip_doc = {"pre_invoke", "main", "post_invoke", "on_error"}
            for i in strip_doc:
                i_func = getattr(cls, i, None)
                if i_func:
                    if hasattr(i_func, '__doc_only__'):
                        try:
                            del i_func.__doc__
                        except AttributeError:
                            pass
        return super().__init_subclass__()

    @property
    def owner(self) -> Union[CCmd, Cog, GroupMixin, None]:
        """Union[:class:`CCmd`, :class:`discord.ext.commands.Cog`, :class:`discord.ext.commands.core.GroupMixin`, None]:
            The owner of the command, similar to :attr:`discord.ext.commands.Command.parent`"""
        if getattr(self, "cogcmd", None):
            return self.cogcmd
        if getattr(self, "cog", None):
            return self.cog
        return self.parent

    @_doc_only
    async def pre_invoke(self, ctx):
        """|overridecoro|
        The before_invoke hook.

        This can be over-rided as a static method.
        The before_invoke decorator can be used to specify another callback
        """
        pass

    @_doc_only
    async def main(self, *args, **kwargs):
        """|overridecoro|
        The callback, this method is the body of the command
        This can be over-rided as a static method.
        """
        pass

    @_doc_only
    async def post_invoke(self, ctx):
        """|overridecoro|
        The after_invoke hook.

        This can be over-rided as a static method.
        The after_invoke decorator can be used to specify another callback
        """
        pass

    @_doc_only
    async def on_error(self, ctx, error):
        """|overridecoro|
        The local command error handler.
        """
        pass

    async def dispatch_error(self, ctx, error):
        ctx.command_failed = True
        cog = self.cog
        cogcmd = self.cogcmd

        if not hasattr(self.on_error, "__doc_only__"):
            injected = wrap_callback(self.on_error)
            if self._needs_cog(self.on_error):
                await injected(cog, ctx, error)
            await injected(ctx, error)

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

    def _needs_cog(self, func) -> bool:
        if self.cog is not None:
            if ismethod(func):
                if func.__self__ == self:
                    return False
                return True
            elif func in self.__class__.__dict__.values():
                return False
            return True
        return False

    @property
    def clean_params(self):
        """:meta private:""" # Has Been documented in dpy.
        result = self.params.copy()

        if not ismethod(self.callback):
             if self._needs_cog(self.callback) or self.cogcmd:
                result.popitem(last=False) # self

        try:
            result.popitem(last=False) # ctx, we will have at least 2 standard params
        except Exception:
            raise ValueError('Missing context parameter') from None
        return result

    async def _parse_arguments(self, ctx: discord.ext.commands.Context):
        _cog = self._needs_cog(self.callback) or self.cogcmd
        ctx.args =[self.cog, ctx] if _cog else [ctx]
        ctx.kwargs = {}
        args = ctx.args
        kwargs = ctx.kwargs

        view = ctx.view
        iterator = iter(self.params.items())

        if _cog:
            # we have 'self' as the first parameter so just advance
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
            if self._needs_cog(self._before_invoke):
                _arg = (cog, ctx)
            else:
                _arg = (ctx)
            self.call_if_overridden(self._before_invoke, *_arg)

    async def call_after_hooks(self, ctx: discord.ext.commands.Context):
        cog = self.cog
        cogcmd = self.cogcmd
        if self._after_invoke is not None:
            if self._needs_cog(self._after_invoke):
                _arg = (cog, ctx)
            else:
                _arg = (ctx)
            await self.call_if_overridden(self._after_invoke, *_arg)

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

    @staticmethod
    async def call_if_overridden(method, *args, **kwargs):
        method = getattr(method.__func__, "__doc_only__", method)
        if method:
            ret = method(*args, **kwargs)
            if isawaitable(ret):
                return await ret
            return ret


class CCmd(Command, _Group, metaclass=CogCommandType, _root=True):
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

class ICommand(Command, metaclass=CmdInitType, _root=True):
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


class ICCmd(CCmd, metaclass=CogCmdInitType, _root=True):
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
