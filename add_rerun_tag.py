# from subprocess import check_output
import re
import failure_tc
# def get_file(method_name):
#   file_grepped = check_output(f'grep -r "def {method_name}" | head -1', shell=True, universal_newlines=True).strip()
#   file = file_grepped.split(':')[0]
#   return file


def parse(method_name, file, tag='rerun'):
    # file = get_file(method_name)
    with open(file, 'r') as f:
        config_file = f.read()

    pattern = rf"(@test.attr\(type=\[)(.*)(\]\W+.*\W+def )({method_name})"
    found_code = re.search(pattern, config_file, re.M)
    # If code is not found, it is due to skip decorator,so find it in next line
    if not found_code:
        pattern = rf"(@test.attr\(type=\[)(.*)(\]\W+.*\W+.*\W+def )({method_name})"
    # Group 2 is the existing tag and Group 4 is the method_name
    tagged_code = re.sub(pattern, rf"\1\2, '{tag}'\3\4", config_file, re.M)
    if tagged_code:
        with open(file, 'w') as f:
            f.write(tagged_code)


if __name__ == "__main__":
    failure_tc.parse_data()
    for i, tc in enumerate(failure_tc.tc_list):
        parse(method_name=tc, file=failure_tc.loc_list[i])

