import sympy
from collections import defaultdict




class InferenceRule:
    """
    Rule to infer conclusions from a kb
    """

    def __init__(self, premise: sympy.Basic, conclusion: dict):
        """

        :param premise: logic formula for the premise of this rule
        :param conclusion: dictionary {string : bool}. atoms that the rule yields if its premise are satisfied
        """
        self._premise = premise
        self._conclusion = conclusion

    @property
    def premise(self) -> sympy.Basic:
        """
        Gets the logic formula for the premise of this rule
        :return: a sympy logical formula
        """
        return self._premise

    @property
    def conclusion(self) -> dict:
        """
        Gets the conclusion of the inference rule, in the form of atoms that the rule would yield if its premise were satisfied
        :return:
        """
        return self._conclusion


    def apply_to(self, kb: dict):
        """
        Adds the rule's conclusions to the given kb only if the premises are satisfied by it
        :param kb: kb to test and add conslusions to
        :return: None
        """
        if self.is_satisfied_by(kb):
            kb.update(self.conclusion)


    def is_satisfied_by(self, kb: dict):
        """
        Returns whether the rule is satisfied by the given KB
        :param kb:  dictionary {atom : truth_value} of truth values in the KB
        :return: true if kb satisfies the rule
        """
        raise NotImplementedError


    def __str__(self):
        return '{0} \u2192 {1}'.format(
            self.premise,
            ', '.join(map(lambda x: ('' if self.conclusion[x] else '~') + x, self.conclusion.keys()))
        )




class ModusPonens(InferenceRule):
    """
    Rule to infer conclusions from a kb
    """

    def __init__(self, premise: sympy.Basic, conclusion: dict):
        super().__init__(premise, conclusion)


    def is_satisfied_by(self, kb: dict):
        kb0 = {}
        for sym in self.premise.free_symbols:
            kb0[sym] = False
        kb0.update(kb)
        return bool(self.premise.subs(kb0))



if __name__ == '__main__':
    a, b, c = sympy.symbols('a,b,c')

    df = (a & b)
    kb = {'a': True, 'b': True}
    rule = ModusPonens(a & b, {'c': True})
    rule.apply_to(kb)

    print('solution', kb)

    kb = {'a': True, 'b': False}
    rule = ModusPonens(a & b, {'c': True})
    rule.apply_to(kb)

    print('solution', kb)