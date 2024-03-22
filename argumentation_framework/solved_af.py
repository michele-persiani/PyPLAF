import solved_af.tasks as tasks
from solved_af.framework import FrameworkRepresentation
from argumentation_framework.util import execute_with_timeout
# NB solved-af required glucose-syrup to be installed



# List of all supported enumeration tasks along with the method which is used to solve said task.

# Complete semantics
EE_CO = 'EE-CO' #completeFullEnumeration
SE_CO = 'SE-CO' #completeSingleEnumeration

# Grounded semantics
SE_GR = 'SE-GR' #groundedSingleEnumeration

# Preferred semantics
EE_PR = 'EE-PR' #preferredFullEnumeration
SE_PR = 'SE-PR' #preferredSingleEnumeration

# Stable semantics
EE_ST = 'EE-ST' #stableFullEnumeration
SE_ST = 'SE-ST' #stableSingleEnumeration


# List of all supported decision tasks along with the method which is used to solve said task.

# Complete semantics
DC_CO = 'DC-CO' #completeCredulousDecision
DS_CO = 'DS-CO' #completeSkepticalDecision

# Grounded semantics
DC_GR = 'DC-GR' #groundedCredulousDecision,

# Preferred semantics
DC_PR = 'DC-PR' #preferredCredulousDecision,
DS_PR = 'DS-PR' #preferredSkepticalDecision,

# Stable semantics
DC_ST = 'DC-ST' #stableCredulousDecision,
DS_ST = 'DS-ST' #stableSkepticalDecision



valid_tasks = [EE_CO, SE_CO, SE_GR, EE_PR, SE_PR, EE_ST, SE_ST,
               DC_CO, DS_CO, DC_GR, DC_PR, DS_PR, DC_ST, DS_ST,
               ]



_TIMEOUT = 300


def find_extensions(solved_af_framework: FrameworkRepresentation, task_name: str = EE_CO):
    """
    Find the extensions for the provided argumentation framework
    :param solved_af_framework: A saf.framework.FrameworkRepresentation instance
    :param task_name: name of type of enumeration to find
    :return: solution as an extension if task is single enumeration, or a list of extensions otherwise
    """
    global i
    assert task_name in valid_tasks, f'{task_name} is not a task in {valid_tasks}'
    task_type = task_name[:2]

    parsed_solution = []

    taskMethod = tasks.getTaskMethod(task_name, is_enumeration=True)
    try:
        solution = execute_with_timeout(_TIMEOUT, lambda x: list(taskMethod(x)), solved_af_framework)
        if task_type == 'SE' and solution is not None:
            parsed_solution = solved_af_framework.valuesToArguments(solution)
        elif task_type == 'EE':
            parsed_solution = [solved_af_framework.valuesToArguments(ext) for ext in solution]
    except TimeoutError:
        print('timeout')
    finally:
        return parsed_solution




def find_acceptance(solved_af: FrameworkRepresentation, argument_value, task_name: str = DC_CO):
    """

    :param solved_af: A saf.framework.FrameworkRepresentation instance
    :param argument_value: id of the argument in side the framework for which to find the decision result
    :param task_name: name of the type of decision (eg. skeptical, credulous acceptance)
    :return: decision value True/False
    """
    # Assuming a decision problem
    assert task_name in valid_tasks, f'{task_name} is not a task in {valid_tasks}'
    acceptanceMethod = tasks.getTaskMethod(task_name, is_enumeration=False)
    argument_value = solved_af.argumentToValue(argument_value)
    parsed_solution = False

    try:
        parsed_solution = execute_with_timeout(_TIMEOUT, lambda x: acceptanceMethod(*x), (solved_af, argument_value,))
    except TimeoutError:
        print('timeout')
    finally:
        return parsed_solution

