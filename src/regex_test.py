import re

ignore_list = ['^\.', 'prev', 'thumb', 'swatch']

ignore_string = '('
sep = '|'

search_string = "vdcjfiw_4K_Albedo.exr"

# search_string = "There some Mayaswatches but are no .data vrayThumb files in here!"

for item in ignore_list:
    ignore_string += (item + sep)

pattern = re.compile(ignore_string[:-1] + ')', re.IGNORECASE)

match = pattern.search(search_string.lower())

if not match:
    print("Valid")
else:
    print(f"Invalid cause of: {match}")
