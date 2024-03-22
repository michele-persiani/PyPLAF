import itertools

from argumentation_framework.frameworks import ArgumentationFramework
from argumentation_framework.inference_rules import *
from collections import defaultdict
import sympy




class Argument:
    """
    Interface for arguments
    """


    def attacks(self, a):
        """
        Returns whether the argument attacks another
        :param a:
        :return: True/False
        """
        pass




class LogicArgument(Argument):

    """
    Logical argument whose attack relation is defined based on wther it invalidate either premises or conclusions
    of another argument (thus obtaining undercut and rebut types of attack)
    """

    def __init__(self, premise: dict, rule: InferenceRule):
        """
        :param premise: dict of {name : truth_value} pairs
        :param rule: InferenceRule of the argument
        """
        self.rule = rule
        self.premise = premise


    @property
    def claim(self) -> dict:
        """
        Returns the argument's claim obtained testing its inference rule
        Returns None if the premises are not satisfied
        :return:
        """
        return self.rule.conclusion if self.rule.is_satisfied_by(self.premise) else None


    def attacks(self, a):
        return self.attacks_rebut(a) or self.attacks_undercut(a)


    def attacks_undercut(self, argument):
        assert isinstance(argument, LogicArgument)

        claim = self.claim
        if claim is None:
            return False
        other_support = defaultdict(lambda: False, argument.premise)
        return any([k in other_support and other_support[k] is not v for k, v in claim.items()])


    def attacks_rebut(self, argument):
        assert isinstance(argument, LogicArgument)
        other_claim = argument.claim
        claim = self.claim
        if claim is None or other_claim is None:
            return False

        return any([k in other_claim and other_claim[k] is not v for k, v in claim.items()])


    def __str__(self):
        return str(self.rule)


    def __repr__(self):
        return str(self)


    def __hash__(self):
        return hash(str(self))





def make_simple_logic_argument(support: dict, claim: dict) -> LogicArgument:
    """
    Create an argument of the type {support} -> {claim} where support and claim are conjunctions of atoms.
    :param support: dictionary {str: bool} of support atoms
    :param claim: dictionary {str: bool} of claim atoms
    :return:
    """

    symbs_support = sympy.symbols(list(support.keys()))
    premise = sympy.And(*[s if support[s.name] else ~s for s in symbs_support])
    rule = ModusPonens(premise, claim)

    return LogicArgument(support, rule)



def make_argumentation_framework(arguments: list[Argument]) -> ArgumentationFramework:
    """
    Creates an ArgumentationFramework from a list of arguments. The size of the argumentation framework will be of
    the number of arguments
    :param arguments: arguments to build the argumentation framework with
    :return:
    """
    af = ArgumentationFramework(len(arguments))

    for i_a0, j_a1 in itertools.product(enumerate(arguments), enumerate(arguments)):
        i, a0 = i_a0
        j, a1 = j_a1
        af.set_attacks(i, j, a0.attacks(a1))

    return af
