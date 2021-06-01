# MIT License

# Copyright (c) 2020-present WizzyGeek

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
from inspect import Parameter, isawaitable, isclass, ismethod
from types import FunctionType, MethodType
from typing import (ClassVar, Coroutine, Generic, TYPE_CHECKING, Any, Callable, Mapping, Optional, Tuple,
                    Type, TypeVar, Union)

# import discord
from discord.errors import ClientException
from discord.ext.commands import Cog
from discord.ext.commands import Command as _Command
from discord.ext.commands import Group as _Group
from discord.ext.commands.core import command, group, wrap_callback
from discord.ext.commands.errors import TooManyArguments
from discord.ext.commands import Context as _Cont

if TYPE_CHECKING:
    from discord.ext.commands.core import GroupMixin
    from discord.ext.commands.errors import CommandError
else:
    pass

Context = TypeVar("Context", bound=_Cont)

__all__ = (
    "CogCommandType",
    "Command",
    "CCmd",
    "inject"
)

AsyncCallable = Callable[..., Coroutine[Any, Any, Any]]
T = TypeVar("T", bound=Callable)

def _doc_only(func: T) -> T:
    func.__doc_only__ = None # type: ignore[attr-defined]
    return func

# PHILOSOPHY:: [I Like Grouped Commands]
## Types ##

# TODO:: [Determine wether our callback is supposed to act as a method]

class CogCommandType(type):
    """This is the metaclass for :class:`.CCmd`

    Registers class attributes which are of type :class:`discord.ext.commands.Command`,
    and have a falsy :attr:`discord.ext.commands.Command.parent` attribute.

    Basically registers all 'parent-less' which are defined in the body of the class.

    Internal Workings
    -----------------
    Adds an attribute named ``__fut_sub_cmds__`` of type ``Dict[str, discord.ext.commands.Command]``
    to the class. On the first initialisation of the class, the commands are registered as subcommands.
    All the instances following the first do not register the subcommands as they are assumed to be
    copies of the first instance, hence their proper initialiasation is assumed to be handled by
    the (``copy()`` method of the) first instance of the class.
    """
    def __new__(cls, name, bases, attrs, **kwargs):
        subcommands = {}
        command_cls = super().__new__(cls, name, bases, attrs, **kwargs)
        for base in reversed(command_cls.__mro__[0:-1]):
            for name, attr in base.__dict__.items():
                if isinstance(attr, _Command):
                    if name in subcommands:
                        del subcommands[name]
                    if not attr.parent:
                        subcommands[name] = attr
        else:
            command_cls.__fut_sub_cmds__ = subcommands
        return command_cls

## Commands ##

class Command(_Command, Generic[Context]):
    """A Command

    This is the base class for all Command classes defined in this package.
    This is a generic type.

    Attributes
    ----------
    cogcmd : Optional[:class:`disctools.commands.CCmd`]
        The :class:`CogCmd` the Command belongs to.

    Example
    -------
    .. code-block:: python

        class SomeCog(SomeCogAbstraction):
            def __str__(self): return "SomeCog"

            @inject(aliases=["test"])
            class Test(Command):
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
    cogcmd: Optional[CCmd]
    use_main: ClassVar[bool] = False

    def __init__(self, func: Optional[AsyncCallable] = None, **kwargs) -> None:
        if func is None or self.use_main:
            func = self.main
            self.__class__.use_main = True
            if Command.main.__doc__:
                del Command.main.__doc__
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

    async def __call__(self, *args, **kwargs) -> Any:
        if self.cog is not None and not isinstance(self.callback, staticmethod):
            return await self.callback(self.cog, *args, **kwargs)
        return await self.callback(*args, **kwargs)

    def __init_subclass__(cls, **kwargs) -> None:
        # I have kept this here so that, if any code divers
        # Want to make a command without a docstring
        # for some reason, besides it gives me peace of mind
        # to know that docstrings wont be messed with at doctime
        if not kwargs.get("_root", False):
            # Assign class's doc to main mehod
            # if main method doesn't have the doc
            main_m = getattr(cls, "main", None)
            if getattr(main_m, "__doc__", None) is None:
                setattr(main_m, '__doc__', getattr(cls, '__doc__', None))
        return super().__init_subclass__()

    @property
    def owner(self) -> Union[CCmd, Cog, GroupMixin, _Command, None]:
        """Union[
            :class:`CCmd`,
            :class:`discord.ext.commands.Cog`,
            :class:`discord.ext.commands.core.GroupMixin`,
            :class:`discord.ext.commands.Command`, :obj:`None`]:
            The owner of the command, similar to :attr:`discord.ext.commands.Command.parent`"""
        if getattr(self, "cogcmd", None):
            return self.cogcmd
        if getattr(self, "cog", None):
            return self.cog
        return self.parent

    @_doc_only
    async def pre_invoke(self, ctx: Context) -> Any:
        """|overridecoro|
        The before_invoke hook.

        This can be over-rided as a static method.
        The before_invoke decorator can be used to specify another callback
        """
        pass

    @_doc_only
    async def main(self, ctx: Context) -> Any:
        """|overridecoro|
        The callback, this method is the body of the command
        This can be over-rided as a static method.
        """
        pass

    @_doc_only
    async def post_invoke(self, ctx: Context) -> Any:
        """|overridecoro|
        The after_invoke hook.

        This can be over-rided as a static method.
        The after_invoke decorator can be used to specify another callback
        """
        pass

    @_doc_only
    async def on_error(self, ctx: Context, error: CommandError):
        """|overridecoro|
        The local command error handler.
        """
        pass

    async def dispatch_error(self, ctx: Context, error: CommandError) -> None:
        ctx.command_failed = True
        cog = self.cog
        cogcmd = self.cogcmd

        if not hasattr(self.on_error, "__doc_only__"):
            injected = wrap_callback(self.on_error)
            _earg = self._get_extra_arg(self.on_error)
            if _earg:
                await injected(_earg, ctx, error)
            await injected(ctx, error)

        if cogcmd is not None:
            await wrap_callback(self.call_if_overridden)(cogcmd.on_subcommand_error, ctx, error)

        try:
            if cog is not None:
                local = Cog._get_overridden_method(cog.cog_command_error)
                if local is not None:
                    wrapped = wrap_callback(local)
                    await wrapped(ctx, error)
        finally:
            ctx.bot.dispatch('command_error', ctx, error)

    def _needs_ccmd(self, func: Callable) -> bool:
        if self.cogcmd is not None and not isinstance(func, MethodType):
            try:
                par = func.__qualname__.split(".")[-2]
            except IndexError:
                return False
            if self.cogcmd.__class__.__name__ == par:
                return True
        return False

    def _needs_cog(self, func: Union[AsyncCallable, MethodType]) -> bool:
        if self.cog is not None and not isinstance(func, MethodType):
            try:
                par = func.__qualname__.split(".")[-2]
            except IndexError:
                return False
            if self.cog.__class__.__name__ == par:
                return True
            return False
        return False

    def _get_extra_arg(self, func: Callable) -> Union[Cog, CCmd, None]:
        if self._needs_ccmd(func):
            return self.cogcmd
        if self._needs_cog(func):
            return self.cog
        return None

    @property
    def clean_params(self) -> Mapping[str, Parameter]:
        """:meta private:""" # Has Been documented in dpy.
        result = self.params.copy()

        if not ismethod(self.callback):
            if self._needs_cog(self.callback) or self._needs_ccmd(self.callback):
                result.popitem(last=False) # self

        try:
            result.popitem(last=False) # ctx, we will have at least 2 standard params
        except Exception:
            raise ValueError('Missing context parameter') from None
        return result

    async def _parse_arguments(self, ctx: Context) -> None:
        _earg = self._get_extra_arg(self.callback)
        ctx.args = [_earg, ctx] if _earg else [ctx]
        ctx.kwargs = {}
        args = ctx.args
        kwargs = ctx.kwargs

        view = ctx.view
        iterator = iter(self.params.items())

        if _earg:
            # we have 'self' as the first parameter so just advance
            # the iterator and resume parsing
            try:
                next(iterator)
            except StopIteration:
                fmt = 'Callback for {0.name} command is missing "self" parameter.'
                raise ClientException(fmt.format(self))

        # next we have the 'ctx' as the next parameter
        try:
            next(iterator)
        except StopIteration:
            fmt = 'Callback for {0.name} command is missing "ctx" parameter.'
            raise ClientException(fmt.format(self))

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

    async def call_before_hooks(self, ctx: Context) -> None:
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
            await self.call_if_overridden(cogcmd.subcommand_before_invoke, ctx)

        if self._before_invoke is not None:
            _earg = self._get_extra_arg(self._before_invoke)
            if _earg:
                _arg: Union[Tuple[Union[Cog, CCmd, None], Context], Tuple[Context]] = (_earg, ctx)
            else:
                _arg = (ctx,)
            await self.call_if_overridden(self._before_invoke, *_arg)

    async def call_after_hooks(self, ctx: Context) -> None:
        cog = self.cog
        cogcmd = self.cogcmd
        if self._after_invoke is not None:
            _earg = self._get_extra_arg(self._after_invoke)
            if _earg:
                _arg: Union[Tuple[Union[Cog, CCmd, None], Context], Tuple[Context]] = (_earg, ctx)
            else:
                _arg = (ctx,)
            await self.call_if_overridden(self._after_invoke, *_arg)

        if cogcmd is not None:
            await self.call_if_overridden(cogcmd.subcommand_after_invoke, ctx)

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
    async def call_if_overridden(member: Union[MethodType, Callable], *args, **kwargs) -> Any:
        if isinstance(member, MethodType):
            member = getattr(member.__func__, "__doc_only__", member)
        else:
            member = getattr(member, "__doc_only__", member)
        if member:
            ret = member(*args, **kwargs)
            if isawaitable(ret):
                return await ret
            return ret

class CCmd(Command[Context], _Group, metaclass=CogCommandType, _root=True):
    """Inherits from :class:`Command`.
    This is a generic type.

    Picks up any :class:`discord.ext.commands.Command` instances as subcommands.
    Any custom metaclass must be a subclass of :class:`CogCommandType` implementing
    any features on top of it.

    Also called :class:`CogCmd`
    """
    def __init__(self, func: Optional[AsyncCallable] = None, **kwargs) -> None:
        super().__init__(func=func, **kwargs)
        if self.__class__.__fut_sub_cmds__:
            for i in self.__class__.__fut_sub_cmds__.values():
                self.add_command(i)
                i.cogcmd = self
            self.__class__.__fut_sub_cmds__.clear()

    def copy(self):
        ret: CCmd = _Command.copy(self)
        for cmd in map(lambda x: x.copy(), self.commands):
            ret.add_command(cmd)
            cmd.cogcmd = ret
        return ret

    @_doc_only
    async def on_subcommand_error(self, ctx: Context, error: CommandError) -> Any:
        """|overridecoro|

        Invoked when any of the subcommands raise an error.
        """
        pass

    @_doc_only
    async def subcommand_before_invoke(self, ctx: Context) -> Any:
        """|overridecoro|

        Called before any subcommand is invoked.
        """
        pass

    @_doc_only
    async def subcommand_after_invoke(self, ctx: Context) -> Any:
        """|overridecoro|

        Called after any subcommand is invoked.
        """
        pass

    def command(self, *args, **kwargs):
        """This is a Decorator.

        Same as :method:`discord.ext.commmands.GroupMixin.command`:, but the decorator also works on classes

        Parameters
        ----------
        args
            The posititional args to use to initialise the class
        kwargs
            The key-word arguments to use to initialise the class.

        Returns
        -------
        Callable[[Union[:class:`types.FunctionType`, Type[:class:`discord.ext.commands.Command`]]], :class:`discord.ext.commands.Command`]
            The decorator which returns the instance.
            Raises :exc:`ValueError` if used on a class which isn't a :class:`discord.ext.commands.Command` subclass.
        """
        def decorator(obj: Union[FunctionType, Type[_Command]]) -> _Command:
            kwargs.setdefault('parent', self)
            if isinstance(obj, type):
                if issubclass(obj, _Command):
                    result = obj(*args, **kwargs)
                else:
                    raise ValueError(f"Expected discord.ext.commands.Command subclass got {type(obj)}")
            else:
                result = command(*args, **kwargs)(obj)
            self.add_command(result)
            return result

        return decorator

    def group(self, *args, **kwargs):
        """This is a Decorator.

        Same as :method:`discord.ext.commmands.GroupMixin.command`:, but the decorator also works on classes

        Parameters
        ----------
        args
            The posititional args to use to initialise the class
        kwargs
            The key-word arguments to use to initialise the class.

        Returns
        -------
        Callable[[Union[:class:`types.FunctionType`, Type[:class:`discord.ext.commands.Command`]]], :class:`discord.ext.commands.Command`]
            The decorator which returns the instance.
            Raises :exc:`ValueError` if used on a class which isn't a :class:`discord.ext.commands.Command` subclass.
        """
        def decorator(obj: Union[FunctionType, Type[_Group]]) -> _Group:
            kwargs.setdefault('parent', self)
            if isinstance(obj, type):
                if issubclass(obj, _Group):
                    result = obj(*args, **kwargs)
                else:
                    raise ValueError(f"Expected discord.ext.commands.Group subclass got {type(obj)}")
            else:
                result = group(*args, **kwargs)(obj)
            self.add_command(result)
            return result
        return decorator
# Alias
CogCmd = CCmd

## Decorators ##

G = TypeVar("G", bound=Command)

def inject(*args, **kwargs) -> Callable[[Type[G]], G]:
    """This is a Decorator.

    Return a class's instance

    Parameters
    ----------
    args
        The positional arguments to use to initialise the class.
    kwargs
        The Key-word arguments to use to initialise the class.

    Returns
    -------
    Callable
        The decorator which returns the instance.

    Raises
    ------
    :exc:`TypeError`
        If instead of a class (aka type instance) a :class:`discord.ext.commands.Command` is provided.


    Example
    -------
    .. code-block:: python

        class SomeCog(SomeSubCog):
            @inject()
            class MyCmd(Command):
                pass
    """
    def decorator(cls: Type[G]) -> G:
        if isinstance(cls, _Command):
            raise TypeError("Can not inject a command instance, expected a <class 'type'>")
        return cls(*args, **kwargs)
    return decorator
