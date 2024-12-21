import pygame

import shell


comp_name: str
path_to_filesystem: str
path_to_logs: str


comp_name = "step"
path_to_filesystem = "/home/step/Documents/Hometasks/config_manage/file_system/filesystem.tar"
path_to_logs = "./log_file.xml"


if __name__ == '__main__':
    my_shell = shell.Shell(comp_name, path_to_filesystem, path_to_logs)
    my_shell.work()
