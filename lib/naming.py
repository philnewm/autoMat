from maya import cmds
import logging

logging.basicConfig()
logger = logging.getLogger('naming')
logger.setLevel(logging.DEBUG)


def rename_shader_if_exists(self, node_name: str, suffix: str = '_AutoMatShader'):
    """
    Check if node_name already exists as shader node name in the running maya instance
    Add counter to name in case node_name already exists
    Is also able to use a suffix for shader node name identification

    Args:
        node_name (str): string to check against current maya instance
        suffix (str): string to add to shader node name

    Returns:
        str: input string as is or string with added counter
    """
    counter = 1  # init counter

    if cmds.objExists(node_name + suffix):

        while cmds.objExists(node_name + str(counter) + suffix):
            counter += 1

        return node_name + str(counter)
    else:

        return node_name


def rename_if_exists(self, node_name: str):
    """
    Check if node_name already exists in the running maya instance
    Add counter to name in case node_name already exists

    Args:
        node_name (str): string to check against current maya instance

    Returns:
        str: input string as is or string with added counter
    """
    counter = 1  # init counter

    if cmds.objExists(node_name):

        while cmds.objExists(node_name + str(counter)):
            counter += 1

        return node_name + str(counter)
    else:

        return node_name


def replaceSpecialChars(self, input_string: str, replaceCharList: list, replaceChar):
    """
    Replace all scpecial characters from replaceCharList found in inoput_string.

    Args:
        input_string (str): String to check for special characters
        replaceCharList (list): list of characters to replace
        replaceChar (_type_): new character to replace it with

    Returns:
        _type_: string without special characters
    """
    for item in replaceCharList:
        input_string = input_string.replace(item, replaceChar)

    logger.debug(f"Converted string: {input_string}")
    return input_string
