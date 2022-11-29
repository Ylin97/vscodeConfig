#!/usr/bin/bash
template_path="$HOME/.config/Code"

if [ ! -d $template_path ]; then
    mkdir -p $template_path
fi

cmd="cp -r ./projectTemplate $template_path"
if eval $cmd; then
    echo -e "\n#Initialize vscode project\nsource \$HOME/.config/Code/projectTemplate/init_vscode_project.sh" >> $HOME/.bashrc
    if [ -e "$HOME/.zshrc" ]; then
        echo -e "\n#Initialize vscode project\nsource \$HOME/.config/Code/projectTemplate/init_vscode_project.sh" >> $HOME/.zshrc
    fi
fi
