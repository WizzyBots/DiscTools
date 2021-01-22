"""Job focused Context classes for discord.py"""

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

from typing import Optional, Sequence, Tuple, Union

import aiohttp
import discord
from discord.ext.commands import Context as _Context


def _maybe_sequence(doubtful) -> Sequence:
    if not isinstance(doubtful, Sequence):
        return [doubtful]
    else:
        return doubtful

class TargetContext(_Context):
    """A Context class with utilities to determine Member hierarchy.

    Helps in checks for moderation Commands.
    """

    def __init__(self, **kwargs):
        """Salt and peppa."""
        super().__init__(**kwargs)
        self._target = None
        self.targets = self.message.mentions

    @property
    def targets(self):
        """Sequence[:class:`discord.Member`] : A sequence of Members that were mentioned, this shall be set on invoke.
        By default it is set to a list of mentions in the message"""
        return self._target

    @targets.setter
    def  targets(self, user: Union[discord.Member, Sequence[discord.Member]]) -> None:
        self._target = _maybe_sequence(user)

    @property
    def is_author_target(self) -> bool:
        """bool : This property is equivalent to ``ctx.is_user_target()`` or ``ctx.is_user_target(ctx.author)``"""
        return self.author in self.targets

    def is_user_target(self, user: discord.Member) -> bool:
        """Check if a user is a target

        Parameters
        ----------
        user : :class:`discord.Member`
            The user to verify as target

        Returns
        -------
        bool
            True if the user is the target, else False
        """
        if user == self.author:
            return self.is_author_target
        return user in self.targets


    def _above_check(self, user: discord.Member, users: Optional[Union[discord.Member, Sequence[discord.Member]]] = None) -> Tuple[bool, Union[discord.Member, None]]:
        if user == self.guild.owner:
            return True, None
        if users is None:
            users = self.targets
        else:
            users = _maybe_sequence(users)

        for member in users:
            if member == self.guild.owner:
                return False, member
            if member.top_role > user.top_role:
                return False, member
            else:
                pass
        else:
            return True, None

    def is_author_above(self, users: Optional[Union[discord.Member, Sequence[discord.Member]]] = None) -> Tuple[bool, Union[discord.Member, None]]:
        """Check if author is above all given users

        Parameters
        ----------
        users :  Optional[Union[:class:`discord.Member`, Sequence[:class:`discord.Member`]]]
            The user(s) to check against, if none, then command's targets are used, by default None.

        Returns
        -------
        Tuple[bool, Union[:class:`discord.Member`, None]]
            A tuple of length two. If author is above targets then first element will
            be True and second element will be None. If author is not above target then
            first element will be False and second element will be the first user who is above the author.
            Example output: ``(True, None)``, ``(False, <discord.Member Object>)``.
        """
        return self._above_check(self.author, users)

    def is_bot_above(self, users: Optional[Union[discord.Member, Sequence[discord.Member]]] = None) -> Tuple[bool, Union[discord.Member, None]]:
        """Check if bot is above all given users, similar to :meth:`TargetContext.is_author_above`

        Parameters
        ----------
        users :  Optional[Union[:class:`discord.Member`, Sequence[:class:`discord.Member`]]]
            The user(s) to check against, if none, then command's targets are used, by default None.

        Returns
        -------
        Tuple[bool, Union[:class:`discord.Member`, None]]
            Same as :meth:`TargetContext.is_author_above`. Only that the comparisn is with Bot.
        """
        return self._above_check(self.author, users)

    async def whisper(self, user: Optional[Union[discord.Member, Sequence[discord.Member]]] = None, *args, **kwargs) -> None:
        """|coro|
        DM all targets of a command.

        Parameters
        ----------
        user : Optional(Union[:class:`discord.Member`, List[discord.Member]])
            The member(s) to DM. Defaults to self.targets.
        args
            The positional arguments that should be used to message the targets.
        kwargs
            The Key-word arguments that should be used to message the targets.

        Returns
        -------
            NoneType
        """
        if user is None:
            user = self.targets
        if not isinstance(user, Sequence):
            return await user.send(*args, **kwargs)
        else:
            for target in user:
                target.send(*args, **kwargs)


class EmbedingContext(_Context):
    """Introduces :meth:`send_embed` which helps reduce usage of :class:`discord.Embed`"""
    async def send_embed(self, *args, **kwargs) -> discord.Message:
        """|coro|
        Send an embed.

        This is a shorthand to creating an :class:`discord.Embed` and sending it.
        All arguments are passed to :class:`discord.Embed`.


        Returns
        -------
        :class:`discord.Message`
            The message that was sent.
        """
        return await self.send(embed=discord.Embed(*args, **kwargs))

    # async def send(self, content=None, **kwargs) -> discord.Message:
    #     """Convert all messages outbound from the bot to Blue Embed."""
    #     if content is not None and kwargs.pop("embed", None) is None:
    #         embed = embed = discord.Embed(description=content, colour=discord.Colour.blue())
    #         return await super().send(embed=embed, **kwargs)
    #     else:
    #         return await super().send(content=content, **kwargs)


class WebHelperContext(_Context):
    """Contains utilities for web requests method.

    Helps in shortening code for web requests based commands,
    Currently only has one method."""
    async def web_request(self, url: str) -> aiohttp.ClientResponse:
        """|coro|
        Make a http rquest with aiohttp

        Parameters
        ----------
        url : str
            The url to send the http request

        Returns
        -------
        :class:`aiohttp.ClientResponse`
            The requests response
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                return r
