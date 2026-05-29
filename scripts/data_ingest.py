"""数据接入"""
import pandas as pd


def load_csv(path):
    return pd.read_csv(path)


def load_dict(records: list):
    return pd.DataFrame(records)
