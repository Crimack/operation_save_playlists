import os


def make_dir(name):
    if not os.path.exists(name):
        os.mkdir(name)


def make_failed_dir():
    make_dir('failed')


def make_success_dir():
    make_dir('success')


def make_results_dir():
    make_dir('results')


def make_backup_dir():
    make_dir('backup')
