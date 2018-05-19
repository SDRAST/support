import os
import re
import subprocess

def pull_submodule_branches():
    """
    Even after calling git submodule update --init --recursive
    submodule will be on a detached branch. We can remedy this by
    going into the submodule and calling "get checkout <branch>"
    and "git pull origin <branch>"
    """
    cur_dir = os.getcwd()
    gitmodules = ".gitmodules"
    if gitmodules not in os.listdir(cur_dir):
        print("Can't find {} in current directory {}".format(gitmodules, cur_dir))
        return
    gitmodules_path = os.path.join(cur_dir, gitmodules)
    with open(gitmodules_path,"r") as f:
        gitmodules_str = f.read()

    def process_submodule_info(line_iter, submodule_info):
        line = next(line_iter, None)
        if not line.startswith("\t"):
            return line_iter, submodule_info
        else:
            split = [i.strip() for i in line.split("=")]
            submodule_info[split[0]] = split[1]
            return process_submodule_info(line_iter, submodule_info)

    def get_submodule_names(line_iter, names):
        line = next(line_iter)
        if "submodule" in line:
            split = line.split(" ")
            name = split[-1].strip("]\"")
            line_iter, info = process_submodule_info(line_iter, {})
            names[name] = info
            return get_submodule_names(line_iter, names)
        else:
            return names

    gitmodules_lines = iter(gitmodules_str.split("\n"))
    names = get_submodule_names(gitmodules_lines,{})
    print(names)
    # info = process_submodule_info(gitmodules_lines, {})
    # print(info)


if __name__ == '__main__':
    pull_submodule_branches()
