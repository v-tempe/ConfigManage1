import unittest
import pygame
from shell import Shell


comp_name = "step"
path_to_filesystem = "/home/step/Documents/Hometasks/config_manage/file_system/filesystem.tar"
path_to_logs = "./log_file.xml"


class MyTestCase(unittest.TestCase):

    def test_pwd(self):
        expected = "/home/step"
        with open("test_pwd.txt", 'r') as my_file:
            actual = my_file.read()
        self.assertEqual(actual.strip(), expected.strip())

    def test_ls(self):
        expected = "Puctures        Downloads        Documents"
        with open("test_ls.txt", 'r') as my_file:
            actual = my_file.read()
        self.assertEqual(actual.strip(), expected.strip())

    def test_ls_l(self):
        expected = "Puctures\nDownloads\nDocuments\n"
        with open("test_ls_l.txt", 'r') as my_file:
            actual = my_file.read()
        self.assertEqual(actual, expected)

    def test_who(self):
        expected = "step    2024-12-20T17:57:48.546472"
        with open("test_who.txt", 'r') as my_file:
            actual = my_file.readline()
        self.assertEqual(actual.strip(), expected.strip())

    def test_whoami(self):
        expected = "step"
        with open("test_whoami.txt", 'r') as my_file:
            actual = my_file.readline()
        self.assertEqual(actual.strip(), expected.strip())


if __name__ == '__main__':
    unittest.main()
