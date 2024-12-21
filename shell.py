import os
import tarfile
from collections import deque
from typing import Iterable, NoReturn
from datetime import datetime
import pygame

import tree
import colors


def get_time() -> str:
    return datetime.now().isoformat()


font_name = pygame.font.match_font('arial')


def render_text(text, size, x, y, color) -> tuple[pygame.Surface, pygame.Rect]:
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)

    return text_surface, text_rect


def draw_text(surf, text, size, x, y, color) -> tuple[pygame.Surface, pygame.Rect]:
    text_surface, text_rect = render_text(text, size, x, y, color)
    surf.blit(text_surface, text_rect)

    return text_surface, text_rect


text_on_screen = pygame.sprite.Group()


class TextOnScreen(pygame.sprite.Sprite):
    def __init__(self, text, size, x, y, color):
        pygame.sprite.Sprite.__init__(self)

        self.text = text
        self.size = size
        self.color = color

        self.image, self.rect = render_text(text, size, x, y, color)

        self.add(text_on_screen)

    def add_text(self, new_text: str):
        self.text += new_text
        self.image, self.rect = render_text(self.text, self.size, self.rect.x, self.rect.y, self.color)

    def cut_text(self, amount_of_chars: int):
        self.text = self.text[:-amount_of_chars]
        self.image, self.rect = render_text(self.text, self.size, self.rect.x, self.rect.y, self.color)


class FileSystemItem:
    TYPES = {"file", "dir"}
    ROOT_MADE = False

    def __init__(self, kind: str, name: str):
        if kind not in FileSystemItem.TYPES:
            raise ValueError(f"Incorrect kind: {kind}.\nCorrect types are {FileSystemItem.TYPES}")
        self.type: str = kind

        if name == "":
            if not FileSystemItem.ROOT_MADE:
                FileSystemItem.ROOT_MADE = True
                self.name = name
                return
            else:
                raise ValueError(f"Name cannot be blank")
        if '/' in name:
            raise ValueError(f"Name cannot contain a '/'. Your name: {name}")
        if kind == "dir":
            if name[0] == '.':
                raise ValueError(f"Name of directory cannot begin with a '.'")
        self.name = name

        if kind == "file":
            self.hidden = self.name[0] == '.'

    def __str__(self):
        return f"<{self.name}>"

    def __repr__(self):
        return self.__str__()

    def is_file(self) -> bool:
        return self.type == "file"

    def is_dir(self) -> bool:
        return self.type == "dir"


class Shell:
    SUPPORTED_COMMANDS = {"ls", "cd", "pwd", "exit", "who", "whoami", "mkdir", "rmdir", "touch", "clear"}
    THIS_FILE_SYMBOL = "."
    PARENT_FILE_SYMBOL = ".."
    WIDTH_PIXELS = 700
    HEIGHT_PIXELS = 500
    DISPLAY_CAPTION = "Shell emulator"
    TEXT_SIZE = 24
    LINE_HEIGHT_ON_SCREEN = 26

    def __init__(self, user_name: str, path_to_filesystem: str, path_to_logs: str):
        def add_file_name_to_tree(file_name: str):
            ...

        self.command = ""

        self.user: str = user_name
        self.__path_to_filesystem = path_to_filesystem
        self.__path_to_logs = path_to_logs

        root_dir = FileSystemItem("dir", "")
        self.filesystem: tree.Tree = tree.Tree(root_dir)
        node_of_home_dir: tree.TreeVertex = self.filesystem.get_root()

        self.home_dir: FileSystemItem = root_dir
        with tarfile.open(path_to_filesystem, 'a') as tar_archive:
            archive_members: list = tar_archive.getmembers()
            archive_members.sort(key=lambda s: archive_members.count('/'))
            for item in archive_members:
                #print(f"File Name: {item.name}")
                path_to_item: list[str] = item.name.split('/')
                item_name: str = path_to_item[-1]
                #print(f"{item_name=}")
                item_kind: str = "dir" if item.isdir() else "file"
                new_item = FileSystemItem(item_kind, item_name)

                self.filesystem.go_to_root()
                for i, node_in_path in enumerate(path_to_item[:-1]):
                    self.filesystem.go_to_child_with_param("name", node_in_path)
                self.filesystem.cur_vertex.create_child(new_item)

                if item_name == user_name:
                    self.filesystem.go_to_child(-1)
                    node_of_home_dir = self.filesystem.cur_vertex
                    self.home_dir = new_item
                    #print(f"{node_of_home_dir.value=}")

            self.filesystem.go_to_root()
        self.filesystem.go_to_certain_vertex(node_of_home_dir)
        self._finished = False

        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode([self.WIDTH_PIXELS, self.HEIGHT_PIXELS])
        pygame.display.set_caption(self.DISPLAY_CAPTION)
        self.text_screen_position_x = 0
        self.text_screen_position_y = 0

        self.log_file = open(path_to_logs, 'w')
        self.log_file.write(f"<log>\n")

    def print_on_screen(self, text: str, a_flag=False):
        TextOnScreen(text,
                     self.TEXT_SIZE,
                     self.text_screen_position_x,
                     self.text_screen_position_y,
                     colors.TERMINAL_TEXT)
        self.text_screen_position_y += Shell.LINE_HEIGHT_ON_SCREEN
        print(text)
        mode = 'a' if a_flag else 'w'
        with open(f"test_{self.command}.txt", mode) as test_file:
            print(text, file=test_file)

    def _finish_work(self):
        self._finished = True
        self.log_file.write(f"</log>\n")
        self.log_file.close()
        pygame.quit()

    @property
    def finished(self):
        return self._finished

    def __execute_command(self, command, *arguments: str) -> int:
        return getattr(self, command)(*arguments)

    def __post_execute_command(self, code: int, full_command: str) -> NoReturn:
        self.log_file.write(f'  <action user="{self.user}" time="{get_time()}" command="{full_command}"/>\n')
        if code == 101:
            self._finish_work()

    def process_command(self, full_command: list[str]):
        if full_command == []:
            return
        command: str = full_command[0]
        arguments = full_command[1:]

        if command in Shell.SUPPORTED_COMMANDS:
            result = self.__execute_command(command, *arguments)
            self.__post_execute_command(result, " ".join(full_command))
        else:
            self.print_on_screen(f"{command}: command not found")

    def get_pwd(self, *arguments) -> str:
        prev_nodes: deque[tree.TreeVertex] = deque()
        current_vertex: tree.TreeVertex = self.filesystem.cur_vertex

        prev_nodes.appendleft(self.filesystem.cur_vertex)
        while not self.filesystem.in_root():
            self.filesystem.go_to_parent()
            prev_nodes.appendleft(self.filesystem.cur_vertex)
        self.filesystem.go_to_certain_vertex(current_vertex)

        return "/".join([node.value.name for node in prev_nodes])

    def pwd(self, *arguments) -> int:
        self.command = "pwd"
        self.print_on_screen(self.get_pwd())
        return 0

    def ls(self, *arguments) -> int:
        self.command = "ls"
        flag_list = False
        for arg in arguments:
            if arg == '-l':
                self.command = "ls_l"
                flag_list = True

        if flag_list:
            for i, item in enumerate(self.filesystem.get_children()):
                item: tree.TreeVertex
                self.print_on_screen(item.value.name, True)
        else:
            self.print_on_screen("        ".join(item.value.name for item in self.filesystem.get_children()))

        return 0

    def cd(self, *arguments: str) -> int:
        self.command = "cd"
        if len(arguments) == 0:
            return 0
        if arguments[0] in {"--help", "?"}:
            self.print_on_screen(f"Usage: cd [PATH]")
            self.print_on_screen(f"  change the shell working directory")
            return 0
        path = arguments[0]

        elements_of_path: list[str] = path.split('/')

        for element in elements_of_path:
            if element == Shell.THIS_FILE_SYMBOL:
                pass
            elif element == Shell.PARENT_FILE_SYMBOL:
                if not self.filesystem.in_root():
                    self.filesystem.go_to_parent()
            else:
                if self.filesystem.cur_vertex.has_child_with_param("name", element):
                    self.filesystem.go_to_child_with_param("name", element)
                else:
                    self.print_on_screen(f"cd: {element}: No such file or directory")

        return 0

    def mkdir(self, *arguments: str):
        self.command = "mkdir"
        if len(arguments) == 0:
            self.print_on_screen(f"mkdir: missing name of a new directory")
            return 0

        path = arguments[0]

        current_vertex: tree.TreeVertex = self.filesystem.cur_vertex

        elements_of_path: list[str] = path.split('/')
        dir_name = elements_of_path.pop()

        for node in elements_of_path:
            if self.filesystem.cur_vertex.has_child_with_param("name", node):
                self.filesystem.go_to_child_with_param("name", node)
            else:
                self.print_on_screen(f"mkdir: {node}: no such file or directory")
                return 1

        try:
            new_dir = FileSystemItem("dir", dir_name)
        except ValueError:
            self.print_on_screen(f"mkdir: incorrect name of directory")
        else:
            self.filesystem.cur_vertex.create_child(new_dir)

        self.filesystem.go_to_certain_vertex(current_vertex)

    def rmdir(self, *arguments: str):
        ...

    def who(self, *arguments: str):
        self.command = "who"
        self.print_on_screen(f"{self.user}    {get_time()}")

    def whoami(self, *arguments: str):
        self.command = "whoami"
        self.print_on_screen(self.user)

    def clear(self, *arguments: str):
        self.screen.fill(colors.TERMINAL_BACKGROUND)

    def exit(self, *arguments) -> int:
        if arguments:
            self.print_on_screen(f"exit: too much arguments")
            return 1

        return 101

    def work(self):

        def input_command(prompt_text: str) -> str:

            prompt = TextOnScreen(prompt_text,
                                  24,
                                  0,
                                  self.text_screen_position_y,
                                  colors.TERMINAL_TEXT)

            user_text = TextOnScreen("",
                                     24,
                                     prompt.rect.right,
                                     self.text_screen_position_y,
                                     colors.TERMINAL_TEXT)

            running = True
            while running:
                for event in pygame.event.get():

                    if event.type == pygame.QUIT:
                        running = False

                    if event.type == pygame.KEYDOWN:

                        if event.key == pygame.K_BACKSPACE:
                            user_text.cut_text(1)
                        elif event.key == pygame.K_RETURN:
                            running = False
                            self.text_screen_position_y += self.LINE_HEIGHT_ON_SCREEN
                        else:
                            user_text.add_text(event.unicode)

                self.screen.fill(colors.TERMINAL_BACKGROUND)
                text_on_screen.draw(self.screen)
                pygame.display.flip()
                self.clock.tick(60)

            return user_text.text

        while not self.finished:
            #shell_input: str = input(f"(base) {self.get_pwd()}$ ")
            shell_input: str = input_command(f"(base) {self.get_pwd()}$ ")
            self.process_command(shell_input.split())
