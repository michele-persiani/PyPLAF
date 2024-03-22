# Solved-AF -- Copyright (C) 2020  David Simon Tetruashvili

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""This module provides solved-af with represenations of Argumentation
    Frameworks and related methods.
"""

import abc
from typing import List, Set

import solved_af.utils as utils


class FrameworkRepresentation(metaclass=abc.ABCMeta):
    """Abstract class defining the base framework representation."""

    def __init__(self, arguments, attacks):
        super().__init__()
        self._values_to_arguments = arguments
        self._arguments_to_values = {arg: i for i,
                                     arg in enumerate(arguments, start=1)}
        self._args = self.argumentsToValues(arguments)
        self._atts = [[self.argumentToValue(arg)
                       for arg in attack] for attack in attacks]

    def argumentToValue(self, argument_name: str) -> int:
        return self._arguments_to_values[argument_name]

    def valueToArgument(self, argument_value: int) -> str:
        return self._values_to_arguments[argument_value - 1]

    def valuesToArguments(self, argument_values: List[int]) -> List[str]:
        return [self.valueToArgument(v) for v in argument_values]

    def argumentsToValues(self, argument_names: List[str]) -> List[int]:
        return [self.argumentToValue(v) for v in argument_names]

    def __iter__(self):
        return iter(self._args)

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'getAttackersOf') and
                callable(subclass.getAttackersOf) and
                hasattr(subclass, 'getAttackedBy') and
                callable(subclass.getAttackedBy) and
                hasattr(subclass, 'getAttackersOfSet') and
                callable(subclass.getAttackersOfSet) and
                hasattr(subclass, 'getAttackedBySet') and
                callable(subclass.getAttackedBySet) and
                hasattr(subclass, 'getArguments') and
                callable(subclass.getArguments) and
                hasattr(subclass, 'getAttacks') and
                callable(subclass.getAttacks) and
                hasattr(subclass, 'characteristic') and
                callable(subclass.characteristic) and
                hasattr(subclass, '__len__') and
                callable(subclass.__len__) or
                NotImplemented)

    @abc.abstractmethod
    def getAttackersOf(self, arg: int) -> List[int]:
        """Get a list of all arguments which attack of a given argument."""
        raise NotImplementedError

    @abc.abstractmethod
    def getAttackedBy(self, arg: int) -> List[int]:
        """Get a list of all arguments which are attacked by a given
        argument."""
        raise NotImplementedError

    @abc.abstractmethod
    def getArguments(self) -> List[int]:
        """Get a list of all arguments in the framework."""
        raise NotImplementedError

    @abc.abstractmethod
    def getAttacks(self) -> List[List[int]]:
        """Get a list of all attacks in the framework."""
        raise NotImplementedError

    @abc.abstractmethod
    def characteristic(self, argument_values_set: Set[int]) -> Set[int]:
        """The characteristic function F of the framework."""
        raise NotImplementedError

    @abc.abstractmethod
    def __len__(self) -> int:
        """Get the number of arguments in the framework."""
        raise NotImplementedError


class ListGraphFramework(FrameworkRepresentation):
    """Framework representation via keeping a lists for each argument of
        arguments which it is attacking and is attacked by.
    """

    # TODO Add SCC and layer split support in construction

    def __init__(self, arguments, attacks):
        """Construct the framework from parsed and validated data.
        Where arguments is a list of named/numbered arguments."""
        super().__init__(arguments, attacks)
        self._node_list = [(set(), set()) for _ in range(len(self._args))]
        for (attacker, attacked) in self._atts:
            self._node_list[attacker - 1][0].add(attacked)
            self._node_list[attacked - 1][1].add(attacker)

        self.LENGTH = len(self._node_list)

    def __len__(self):
        return self.LENGTH

    def __str__(self):
        retStr = ""
        for i, (attacking, attacked_by) in enumerate(self._node_list):
            arg = self.valueToArgument(i)
            white_space = ' ' * len(arg)
            SEP = ', '
            def to_str_repr(vs): return SEP.join(self.valuesToArguments(vs))
            attacking_str, attacked_by_str = to_str_repr(
                attacking), to_str_repr(attacked_by)
            retStr += (
                f'{white_space} {attacking_str}\n'
                f'{white_space}\U0001f855\n'
                f'{arg}\n'
                f'{white_space}\U0001f854\n'
                f'{white_space} {attacked_by_str}\n\n'
            )
        return retStr

    def characteristic(self, argument_values):
        """The charachteristic function of the AF defined as giving the
            set of arguments in the AF which defend some other set of
            arguments.

        Arguments:
            argument_values {Set[int]} -- the arguments whose defending
                set to find

        Returns:
            Set[int] -- the defnding set of argument_values
        """

        # ? Maybe use binary representations of the sets of arguments to
        # ? compair?

        # * Can use lookups in self._att? One by one instead
        # * of computing sets...

        # {B | ∃C ∈ Args. C attacks B}
        attacked_by_args = self.getAttackedBySet(argument_values)

        return {arg for arg in self
                if self.getAttackersOf(arg).issubset(attacked_by_args)}

    @staticmethod
    def _indexOf(arg_value):
        return arg_value - 1

    def getAttackedBy(self, arg):
        return self._node_list[self._indexOf(arg)][0]

    def getAttackersOf(self, arg):
        return self._node_list[self._indexOf(arg)][1]

    def getAttackedBySet(self, arg_set):
        return utils.flattenSet([self.getAttackedBy(arg) for arg in arg_set])

    def getAttackersOfSet(self, arg_set):
        return utils.flattenSet([self.getAttackersOf(arg) for arg in arg_set])

    def getArguments(self):
        return self._args

    def getAttacks(self):
        return self._atts


@utils.memoize
def extensionToInt(extension):
    """Convert an extension into a binary value of arbitrary precision
    in order to comapre extensions efficiently.

    Arguments:
        extension {List[int]} -- the extension to get the
            binary representation of

    Returns:
        int -- the representation of the extension
    """

    rep = 0

    for arg in extension:
        rep += 2**(arg-1)

    return rep


def isIncluded(extension, other):
    """Check if an extension is included in another
        (w.r.t set inclusion).

    Arguments:
        extension {List[int]} -- extension to check inclusion for
        other {List[int]} -- extension to check inclusion against

    Returns:
        bool -- if the extension is included in the other
    """

    ext_rep = extensionToInt(extension)
    other_rep = extensionToInt(other)

    if ext_rep > other_rep:
        return False

    return other_rep & ext_rep == ext_rep


# def getMinimal(extensions):
#     extensions.sort(key=len)
#     for ext in extensions:
#         if all((isIncluded(ext, other) for other in extensions)):
#             return ext


def getAllMaximal(extensions):
    """Filter all maximal (w.r.t. set inclusion) extension from an
        iterable. Do this by keeping a reference to a currenly maximal
        set of extension and either adding the next extension from the
        iterable to it or removing those found not to be maximal from it
        after considering the said next extension.

    Arguments:
        extensions {List[List[int]]} -- list of extensions to find the
            maximal from w.r.t. the list.

    Returns:
        Set[List[int]] -- the maximal extensions from the list
            w.r.t. the list.
    """
    currently_maximal = set()

    for ext in extensions:
        is_maximal = True
        non_maximal = []

        for other in currently_maximal:
            if isIncluded(ext, other):
                is_maximal = False
                break
            elif isIncluded(other, ext):
                non_maximal.append(other)

        currently_maximal.difference_update(non_maximal)

        if is_maximal:
            currently_maximal.add(ext)

    return currently_maximal
