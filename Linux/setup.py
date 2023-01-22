import os
from shutil import copytree, rmtree


def set_shell_config(fpath: str):
    """设置shell配置文件"""
    with open(fpath, 'r', encoding='utf-8') as fr:
        origin_content = fr.readlines()
        start, end = 0, 0
        if origin_content:
            for cnt, line in enumerate(origin_content):
                if line.strip() == '#region project initialize':
                    start = cnt
                if start != 0 and line.strip() == '#endregion':
                    end = cnt + 1
                    break
    content = '#region project initialize\n' \
            + f'source {HOME}/.config/Code/projectTemplate/init_vscode_project.sh\n' \
            + '#endregion'
    with open(fpath, 'w', encoding='utf-8') as fw:
        if not origin_content:
            fw.write(content)
        elif start != 0:
            fw.writelines(origin_content[0:start])
            if len(origin_content[start - 1].strip()) != 0:
                if origin_content[start - 1][-1] != '\n': 
                    fw.write('\n\n')
                else:
                    fw.write('\n')
            fw.write(content)
            if end > start and end < len(origin_content):
                if len(origin_content[end].strip()) != 0:
                    fw.write('\n\n')
                else:
                    fw.write('\n')
                fw.writelines(origin_content[end:])
        else:
            fw.writelines(origin_content)
            fw.write('\n')
            if origin_content[-1][-1] != '\n':
                fw.write('\n')
            fw.write(content)


def copy_template():
    """拷贝项目模板到默认模板放置位置"""
    vscode_config_path = f'{HOME}/.config/Code'
    destination = os.path.join(vscode_config_path, 'projectTemplate')
    if not os.path.exists(vscode_config_path):
        os.makedirs(vscode_config_path)
    if os.path.exists(destination):
        rmtree(destination)
    copytree('projectTemplate', destination)


if __name__ == "__main__":
    HOME = os.environ['HOME']
    # 拷贝模板
    copy_template()
    # 设置shell配置文件
    bashrc_path = os.path.join(HOME, '.bashrc')
    zshrc_path = os.path.join(HOME, '.zshrc')
    if not os.path.exists(bashrc_path):
        fw = open(bashrc_path, 'w', encoding='utf-8')
        fw.close()
    set_shell_config(bashrc_path)

    if os.path.exists(zshrc_path):
        set_shell_config(zshrc_path)