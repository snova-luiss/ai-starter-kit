import json
import os
import sys
from typing import Any, Dict, List

import pandas as pd
from weave import Dataset

current_dir = os.path.dirname(os.path.abspath(__file__))
utils_dir = os.path.abspath(os.path.join(current_dir, '..'))
repo_dir = os.path.abspath(os.path.join(utils_dir, '..'))
sys.path.append(utils_dir)
sys.path.append(repo_dir)

from abc import ABC, abstractmethod


class DatasetConverter(ABC):
    """Abstract base class for dataset converters."""

    @abstractmethod
    def convert(self) -> List[Dict[str, str]]:
        """Converts the dataset to a list of dictionaries."""
        pass


class JSONDatasetConverter(DatasetConverter):
    """Converter for JSON data."""

    def __init__(self, path: str) -> None:
        self.json_data = self.load_data(path)

    def load_data(self, path: str) -> Any:
        """Load data from a JSON file."""
        try:
            with open(path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f'Error loading JSON data from {path}: {str(e)}')

    def convert(self) -> List[Dict[str, str]]:
        """Convert JSON data to a list of dictionaries."""
        return self.json_data


class DataFrameDatasetConverter(DatasetConverter):
    """Converter for CSV data."""

    def __init__(self, filepath: str) -> None:
        self.dataframe = self.load_data(filepath)

    def load_data(self, filepath: str) -> pd.DataFrame:
        """Load data from a CSV file."""
        try:
            return pd.read_csv(filepath)
        except FileNotFoundError as e:
            raise ValueError(f'Error loading CSV data from {filepath}: {str(e)}')

    def convert(self) -> List[Dict[str, str]]:
        """Convert the DataFrame to a list of dictionaries."""
        return self.dataframe.to_dict(orient='records')


class DatasetConverterFactory:
    """Factory to create dataset converters based on the input type."""

    @staticmethod
    def create_converter(filepath: str) -> DatasetConverter:
        """Create a dataset converter based on the file extension."""
        _, extension = os.path.splitext(filepath)
        extension = extension.lower()

        if extension == '.json':
            return JSONDatasetConverter(filepath)
        elif extension in ['.csv', '.txt']:
            return DataFrameDatasetConverter(filepath)
        else:
            raise ValueError('Unsupported file type. Please provide a JSON or CSV file.')


class WeaveDatasetManager:
    """Class to manage Weave datasets."""

    def __init__(self, name: str, filepath: str) -> None:
        self.name = name
        self.filepath = filepath

    def create_dataset(self) -> Dataset:
        converter = DatasetConverterFactory.create_converter(self.filepath)
        converted_data = converter.convert()
        return Dataset(name=self.name, rows=converted_data)
