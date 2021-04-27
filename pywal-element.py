import os
import typing
from typing import Any
import json
import collections
import sys
import shutil
import subprocess
import argparse

import pywal

default_theme_map = {
    'accent-color': 'color2',
    'primary-color': 'color0',
    'warning-color': 'color1',

    'sidebar-color': 'color0',
    'roomlist-background-color': 'color0',
    'roomlist-text-color': 'color7',
    'roomlist-text-secondary-color': 'color4',
    'roomlist-highlights-color': 'color3',
    'roomlist-separator-color': 'color3',

    'timeline-background-color': 'color0',
    'timeline-text-color': 'color7',
    'timeline-text-secondary-color': 'color5',
    'reaction-row-button-selected-bg-color': 'color6'
    }


def generate_json(colors: dict[str, str], theme_map: dict[str, str], is_dark: bool) -> collections.OrderedDict[str, Any]:
    theme: collections.OrderedDict[str, Any] = collections.OrderedDict()
    theme['name'] = "pywal-element"
    theme['is_dark'] = is_dark


    theme_color = collections.OrderedDict()
    for item in theme_map.items():
        theme_color[item[0]] = colors[item[1]]

    theme['colors'] = theme_color

    return theme


def gen_new_cfg(config, theme):

    if not 'settingDefaults' in config or not 'custom_themes' in config['settingDefaults']:
        config['settingDefaults'] = {'custom_themes': [theme]}
    else:
        custom_themes = config['settingDefaults']['custom_themes']
        custom_themes = list(filter(lambda th: th['name'] != 'pywal-element', custom_themes))
        custom_themes.append(theme)

        config['settingDefaults']['custom_themes'] = custom_themes

    return json.dumps(config, indent=4)

def main():

    default_location: list[str] = os.path.join(*[os.environ["HOME"], ".cache", "wal", "colors.json"])


    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str, default=default_location, help='Path to json file')
    parser.add_argument('-d', '--is-dark', type=bool, default=True, help='Is dark theme?')
    parser.add_argument('-e', '--element-config-path', type=str, default='/etc/element/config.json', help='Path to element config')
    parser.add_argument('-o', '--override-color-map', type=str, default='', help='Path to json file for overriding mapping of pywal colors to element')
    args = parser.parse_args()


    if not os.access(args.element_config_path, os.W_OK):
        os.execvp('sudo', ['sudo', 'python3'] + sys.argv + ['-p', args.path])
        sys.exit()


    theme_map = default_theme_map
    if args.override_color_map != '':
        theme_map = json.load(args.override_color_map)

    cache_wal: str = default_location if args.path == '' else args.path
    colors: dict[str, (str, dict[str, str])] = pywal.colors.file(cache_wal)
    theme: dict = generate_json(colors['colors'], theme_map, args.is_dark)


    new_cfg: str = ''
    with open(args.element_config_path) as json_file:
        new_cfg = gen_new_cfg(json.load(json_file), theme)
    print(new_cfg)


    backup: str = os.path.dirname(args.element_config_path) + "/.backup.config.json"
    print('Copying config to ' + backup)
    shutil.copyfile(args.element_config_path, backup)


    with open(args.element_config_path, 'r+') as cfg:
        cfg.seek(0)
        cfg.write(new_cfg)
        cfg.truncate()

    print('New config written')

if __name__ == "__main__":
    main()
