import os
my_list = ['BASE', 'BASE xBU xPY', 'BU GROUP REL', 'PY REL']

my_string = "Citadel_v3_m_citadel_backwall_stones_Roughness_Utility - Raw"

filePath = "Citadel_v3_m_citadel_backwall_stones_Color_ACES - ACEScg.1001.exr"

specialCharsList = [" ", "-", ".", ",", ";", "#",
                         "'", "´", "`", "!", "?", "%", "&", "~", "*"]


def replaceSpecialChars(input_string: str, replaceCharList: list, replaceChar):
    for item in replaceCharList:
        input_string = input_string.replace(item, replaceChar)

    return input_string


# output = replaceSpecialChars(my_string, specialCharsList, "_")

# print(output)
print(os.path.splitext(os.path.split(filePath)[1])[1][1:])
