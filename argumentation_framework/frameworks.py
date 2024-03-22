from __future__ import annotations
from collections import defaultdict
from solved_af.framework import ListGraphFramework, FrameworkRepresentation
import numpy as np
from argumentation_framework.solved_af import *
from argumentation_framework.util import parallelize_iterations




class ArgumentationFramework:


    def __init__(self, max_num_arguments: int):
        self._attacks = np.zeros((max_num_arguments, max_num_arguments, ))
        self._arguments_mask = np.ones(max_num_arguments)
        self._data = defaultdict(lambda: {})

    @property
    def num_arguments(self)-> int:
        """
        Getter for the number of unmasked arguments of the framework
        :return: int
        """
        return int(sum(self._arguments_mask))

    @property
    def num_max_arguments(self)-> int:
        """
        Getter for the number maximum number of arguments that the framework can have. Namely, number of arguments either
        masked or unmasked
        :return: int
        """
        return int(self._arguments_mask.shape[0])

    @property
    def all_arguments(self):
        """
        Getter for all arguments
        :return: array of ints of shape (num_max_arguments, )
        """
        return np.arange(self.num_arguments)

    @property
    def arguments(self): # Arguments after masking
        """
        Getter for unmasked arguments
        :return: array of ints of shape (num_arguments, )
        """
        arguments = np.arange(self.num_arguments)
        arguments = arguments[np.nonzero(self.argument_mask)]
        return arguments

    @property
    def argument_mask(self):
        """
        Getter for the arguments mask
        :return: boolean array of shape (max_num_arguments,)
        """
        return np.copy(self._arguments_mask)


    @argument_mask.setter
    def argument_mask(self, v):
        """
        Setter for the argument mask
        :param v: array of booleans of shape (max_num_arguments,)
        :return: None
        """
        v = (v > 0).astype('bool').reshape(-1)
        assert len(v) == len(self._arguments_mask)
        self._arguments_mask = v


    def mask_argument(self, n, v):
        """
        Sets the msk for an argument
        :param n: argument to set its mask of
        :param v: mask value
        :return: None
        """
        self._arguments_mask[n] = min(max(v, 0), 1)


    @property
    def attacks_matrix(self):
        """
        Gets the full attack matrix including masked arguments
        :return: array of shape (max_num_arguments, max_num_arguments)
        """
        return np.copy(self._attacks)


    @property
    def attacks_relation(self):
        """
        Gets the attack relations pairs for unmasked arguments only
        :return: list of attack pairs (from, to)
        """
        atks = []
        for i, j in np.argwhere(self._attacks):
            if np.any(i == self.arguments) and np.any(j == self.arguments):
                atks += [(i, j), ]
        return np.array(atks, dtype='int')


    def set_data(self, idx, **kwargs):
        """
        Sets arbitrary data to associate with an argument
        :param idx: id of the argument in [0..n)
        :param kwargs:
        :return: None
        """
        assert 0 <= idx < self.num_arguments
        self._data[idx].update(dict(kwargs))


    def get_data(self, idx):
        """
        Gets the data associated with the given argument id
        :param idx: argument id
        :return: a dictionary with the previously added data
        """
        assert 0 <= idx < self.num_arguments
        return self._data[idx]


    def set_attacks(self, frm: int, to: int, v: bool):
        """
        Sets to 'v' an attack relation 'frm' --> 'to'
        :param frm: attacking argument. int
        :param to: attacked argument. int
        :param v: value of the attacks relation
        :return: None
        """
        self._attacks[frm, to] = max(0, min(int(v), 1))


    def get_attacks(self, frm: int, to: int):
        """
        Returns whether 'frm' attack 'to'
        :param frm: attacking argument
        :param to: attacked argument
        :return: 1 if 'frm' attacks 'to', 0 otherwise
        """
        return self._attacks[frm, to]


    def to_solved_af(self) -> FrameworkRepresentation:
        """
        Transform to a FrameworkRepresentation object that is supported by the package solved-af.
        Masked arguments are ignored.
        :return: a FrameworkRepresentation
        """
        arguments = self.arguments
        attacks = self.attacks_relation

        return ListGraphFramework(arguments, attacks)


    def solve_extensions(self, extension_type: str = EE_CO):
        """
        Find the extensions of the requested type.
        See framework.solved_af.py for the available extensions
        :param extension_type: type of extensions to find
        :return: a list of extensions. Each extensions is a list of arguments
        """
        af = self.to_solved_af()
        enum = find_extensions(af, extension_type)

        if len(enum) == 0:
            return [[], ]
        if len(enum) > 0 and not isinstance(enum[0], list):
            return [enum, ]
        else:
            return enum


    def solve_decision(self, argument_value: int, decision_type=DC_CO):
        """
        Find the decision result for the requested type of decision
        See framework.solved_af.py for the available decision
        :param argument_value: argument to take the decision upon
        :param decision_type: type of decision
        :return:
        """
        af = self.to_solved_af()
        return find_acceptance(af, argument_value, decision_type)




    def equivalent_to(self, other: ArgumentationFramework, criteria: str):
        """
        Compute equivalence of frameworks given the criteria
        :param other:
        :param criteria:
        :return:
        """
        assert isinstance(other, ArgumentationFramework)
        assert self.num_arguments == other.num_arguments


        if criteria.startswith('SE') or criteria.startswith('EE'):
            to_str_set = lambda y: set(map(lambda x: str(sorted(x)), y))
            extensions = to_str_set(self.solve_extensions(criteria))
            other_extensions = to_str_set(other.solve_extensions(criteria))
            return extensions.issubset(other_extensions) and other_extensions.issubset(extensions)

        elif criteria.startswith('DC') or criteria.startswith('DS'):
            for arg in self.all_arguments:
                if not np.any(arg == self.arguments) and not np.any(arg == other.arguments):
                    self_decision = other_decision = False
                elif not np.any(arg == self.arguments) and np.any(arg == other.arguments):
                    other_decision = other.solve_decision(arg, criteria)
                    self_decision = False
                elif np.any(arg == self.arguments) and not np.any(arg == other.arguments):
                    self_decision = self.solve_decision(arg, criteria)
                    other_decision = False
                else:
                    self_decision = self.solve_decision(arg, criteria)
                    other_decision = other.solve_decision(arg, criteria)
                if self_decision != other_decision:
                    return False
            return True
        else:
            assert False, f'{criteria} is not a valid criteria'








class ProbabilisiticWrapper:
    """
    Probabilistic argumentation framework that allows to enumerate all framework instances and solve them.
    The framework is stored and handled in its Normal Attack Form. Argument 0 is the ground truth argument
    [see Theofrastos et al., Hunter et al.].
    """

    def __init__(self, af: ArgumentationFramework):
        self._p_attks = np.zeros((af.num_arguments + 1, af.num_arguments + 1))
        self._wrapped = af
        self._p_attks[1:, 1:] = af.attacks_matrix

    @property
    def wrapped_framework(self):
        return self._wrapped


    @property
    def p_attacks_normal_form(self):
        p_orig = np.copy(self.wrapped_framework.attacks_matrix)
        p_attks = np.copy(self._p_attks)
        p_attks[1:, 1:] *= p_orig
        return p_attks


    def get_p_attacks(self):
        return self.p_attacks_normal_form[1:, 1:]


    def set_p_attacks(self, frm: int, to: int, p: float):
        """
        Sets the probability of an attack from 'arg_from' to 'arg_to'
        :param frm: argument from which the attack starts. int value inside [0..num_args-1)
        :param to: argument that is being attacks. int value inside [0..num_args-1)
        :param p: probability of the attack. float value in (0..1]
        :return: None
        """
        assert 0 <= p <= 1, '0 <= p <= 1'

        self._p_attks[frm+1, to+1] = p
        self.wrapped_framework.set_attacks(frm, to, p > 0)


    def set_p_arg(self, argn: int, p: float):
        """
        Sets the probability that an argument exists inside the framework. By default all arguments exists
        :param argn: argument to set the probability to. value [0..num_args)
        :param p: probability of the argument. value (0..1]
        :return: None
        """
        assert 0 <= p <= 1, '0 <= p <= 1'

        self._p_attks[0, argn + 1] = 1 - p


    def get_p_arg(self, argn:int) -> float:
        return 1 - self._p_attks[0, argn + 1]


    def __yield_all_frameworks(self):
        queue = list()
        queue.append((1, np.copy(self.p_attacks_normal_form)))
        while len(queue) > 0:
            p, curr = queue.pop(0)
            indeces = np.argwhere((curr > 0) * (curr < 1))
            if len(indeces) == 0:
                yield p, curr
            else:
                i, j = indeces[0, :]
                proba = self.p_attacks_normal_form[i, j]
                curr_p_0 = np.copy(curr)
                curr_p_0[i, j] = 1
                queue.append((p * proba, curr_p_0))
                curr_p_1 = np.copy(curr)
                curr_p_1[i, j] = 0
                queue.append((p * (1 - proba), curr_p_1))


    def enumerate_frameworks(self):
        """
        Enumerate all possible instances of the framework in attack normal form
        :return: generator for list of tuples [(p, af),...]
        """

        results = list(self.__yield_all_frameworks())

        for p, af_attacks in results:
            anf_num_arguments = self.wrapped_framework.num_arguments + 1
            af = ArgumentationFramework(anf_num_arguments)
            af.argument_mask = np.zeros(anf_num_arguments)
            for a in self.wrapped_framework.arguments:
                af.mask_argument(a + 1, 1)
            af.mask_argument(0, 1)
            for i, j in np.argwhere(af_attacks):
                af.set_attacks(i, j, 1)
            yield p, af


    def get_p_extension(self, extension_type: str):
        """
        Gets the probability of extensions
        :param extension_type: type of extension to compute

        # Complete semantics
        'EE-CO' #completeFullEnumeration
        'SE-CO' #completeSingleEnumeration

        # Grounded semantics
        'SE-GR' #groundedSingleEnumeration

        # Preferred semantics
        'EE-PR' #preferredFullEnumeration
        'SE-PR' #preferredSingleEnumeration

        # Stable semantics
        'EE-ST' #stableFullEnumeration
        'SE-ST' #stableSingleEnumeration

        :return: list of tuples [(p, extension), ...]
        """
        from collections import defaultdict
        hash_proba = defaultdict(lambda: 0.)
        hash_extension = {}

        def __solve_for_p_af(x):
            p, af = x
            enumeration = af.solve_extensions(extension_type)

            n_enums = len(enumeration)

            for i in range(n_enums):
                enum_i = np.array(sorted(enumeration[i]), 'int32')
                assert np.any(enum_i == 0), 'The ground truth argument should be present in all extensions'
                enum_i = np.delete(enum_i, np.argwhere(enum_i == 0)) # Remove ground truth
                enum_i -= 1 # arguments [1..n] becomes [0..n-1]
                enum_i.flags.writeable = False
                hashed = hash(np.sort(enum_i).tobytes())


                hash_proba[hashed] += p
                hash_extension[hashed] = enum_i
            return None

        frameworks = list(self.enumerate_frameworks())
        #for af in frameworks:
        #    __solve_for_p_af(af)

        parallelize_iterations(frameworks, __solve_for_p_af)


        for k in hash_proba.keys():
            yield hash_proba[k], hash_extension[k],


    def get_p_decision(self, argument: int, decision_type: str):
        """
        Returns the probability of a decision
        :param argument: argument to take the decision over
        :param decision_type: type of decision

        # Complete semantics
        'DC-CO' #completeCredulousDecision
        'DS-CO' #completeSkepticalDecision

        # Grounded semantics
        'DC-GR' #groundedCredulousDecision,

        # Preferred semantics
        'DC-PR' #preferredCredulousDecision,
        'DS-PR' #preferredSkepticalDecision,

        # Stable semantics
        'DC-ST' #stableCredulousDecision,
        'DS-ST' #stableSkepticalDecision
        :return:
        """
        v = np.zeros(2)
        argument += 1

        def __solve_for_p_af(x):
            p, af = x
            decision = af.solve_decision(argument, decision_type)
            v[int(decision)] += p

        parallelize_iterations(self.enumerate_frameworks(), __solve_for_p_af)

        return v[1]


    def get_p_equivalent_to(self, paf, criteria: str):
        """
        Gets the probability that this framework is equivalent to another given a criteria or extensions or decisions


        # Complete semantics
        'EE-CO' #completeFullEnumeration
        'SE-CO' #completeSingleEnumeration

        # Grounded semantics
        'SE-GR' #groundedSingleEnumeration

        # Preferred semantics
        'EE-PR' #preferredFullEnumeration
        'SE-PR' #preferredSingleEnumeration

        # Stable semantics
        'EE-ST' #stableFullEnumeration
        'SE-ST' #stableSingleEnumeration

        # Complete semantics
        'DC-CO' #completeCredulousDecision
        'DS-CO' #completeSkepticalDecision

        # Grounded semantics
        'DC-GR' #groundedCredulousDecision,

        # Preferred semantics
        'DC-PR' #preferredCredulousDecision,
        'DS-PR' #preferredSkepticalDecision,

        # Stable semantics
        'DC-ST' #stableCredulousDecision,
        'DS-ST' #stableSkepticalDecision
        :param paf:
        :param criteria:
        :return:
        """
        assert isinstance(paf, ProbabilisiticWrapper)
        import itertools
        combinations = list(itertools.product(list(self.enumerate_frameworks()), list(paf.enumerate_frameworks())))

        p, P = 0, 0

        n = 0

        def __solve_for_p_af(x):
            nonlocal p, P, n
            (p_0, af_0), (p_1, af_1) = x[0], x[1]
            eq = af_0.equivalent_to(af_1, criteria)
            p += eq * p_0 * p_1
            P += p_0 * p_1
            n += 1
            print(f'Computing equivalence {criteria}... {n}/{len(combinations)}')

        parallelize_iterations(combinations, __solve_for_p_af)

        return p



