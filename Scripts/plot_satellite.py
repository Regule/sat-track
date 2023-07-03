'''
This script will be used for plotting satellite over some desired location.
'''
import sys
import os
import logging
import argparse
import pygame as pg
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from beyond.io.tle import Tle
from beyond.dates import timedelta
import xml.etree.ElementTree as ET

#---------------------------------------------------------------------------------------------------
#                                            LOGGING
#---------------------------------------------------------------------------------------------------
logger = logging.getLogger()
iprint = logger.info
wprint = logger.warning
eprint = logger.error

def setup_logger(dataset_path, output_file='console_output.txt'):
    log_formatter = logging.Formatter('%(message)s')

    logfile_path = os.path.join(dataset_path, output_file)
    file_handler = logging.FileHandler(logfile_path)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    logger.setLevel(logging.INFO)

#---------------------------------------------------------------------------------------------------
#                                           CONFIG PARSING 
#---------------------------------------------------------------------------------------------------
class ExtendedArgumentParser(argparse.ArgumentParser):

    def __init__(self, config_argument='config_file' ,description=None):
        super().__init__(description)
        self.add_argument(f'--{config_argument}', type=str, default=None,
                          help='XML file with arguments')
        self.config_argument = config_argument

    def parse_args(self):
        args = super().parse_args()
        
        print(vars(args))

        try:
            defaults = self.parse_xml_file(getattr(args, self.config_argument))
            for arg in vars(args):
                if getattr(args, arg) is None and arg in defaults:
                    setattr(args, arg, defaults[arg])
        except KeyError:
            print('No config file given.')

        return args

    @staticmethod
    def parse_xml_file(xml_file):
        defaults = {}
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for param in root.findall('param'):
                name = param.get('name')
                value = param.get('value')
                defaults[name] = value
        except ET.ParseError:
            print("Error parsing XML file.")
        return defaults

#---------------------------------------------------------------------------------------------------
#                                            MAIN FUNCTION 
#---------------------------------------------------------------------------------------------------

def main(args):
    pass

if __name__ == '__main__':
    parser = ExtendedArgumentParser()
    args = parser.parse_args()
    main(args)
