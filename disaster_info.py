#!/usr/bin/env python3

import argparse
import config
import logging
import requests
import sys
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from googletrans import Translator


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class DisasterInfo(ABC):
    """
    Abstract base class for disaster information.
    """
    def __init__(self, data: Dict[str, Any]):
        self.raw_data = data
        self.id = data.get('id', 'Unknown ID')
        self.time = data.get('time', 'Unknown Time')

    @abstractmethod
    def display(self) -> None:
        pass

    def _translate(self, text: str) -> str:
        """
        Translates Japanese text to English.
        Returns original text if translation fails.

        Args:
            text (str): The Japanese text to translate.

        Returns:
            str: Translated English text or original text.
        """
        if not text or text == 'Unknown Area' or text == 'Unknown Location':
            return text

        try:
            translator = Translator()
            result = translator.translate(text, src='ja', dest='en')
            return result.text
        except Exception as e:
            logging.warning(f"Translation failed for '{text}': {e}")
            return text

class Earthquake(DisasterInfo):
    """Class for earthquake information."""
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        earthquake = data.get('earthquake', {})
        hypocenter = earthquake.get('hypocenter', {})

        self.time = earthquake.get('time', 'Unknown Time')
        raw_name = hypocenter.get('name', 'Unknown Location')
        self.name = self._translate(raw_name)
        self.magnitude = hypocenter.get('magnitude', -1.0)
        self.tsunami_status = earthquake.get('domesticTsunami', 'None')

    def display(self) -> None:
        print(f"Earthquake ID: {self.id}")
        print(f"Hypocenter: {self.name}")
        print(f"Magnitude: {self.magnitude}")
        print(f"Time: {self.time}")
        tsunami_msg = "No tsunami triggered." if self.tsunami_status == 'None' else self.tsunami_status
        print(f"Tsunami: {tsunami_msg}")

class Tsunami(DisasterInfo):
    """Class for tsunami information."""
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        issue = data.get('issue', {})
        self.time = issue.get('time', 'Unknown Time')
        raw_areas = [area.get('name', 'Unknown Area') for area in data.get('areas', [])]
        self.areas = [self._translate(raw_area) for raw_area in raw_areas]

    def display(self) -> None:
        print(f"Tsunami ID: {self.id}")
        print(f"Time: {self.time}")
        print(f"Areas: {', '.join(self.areas)}")

class APIClient:
    """Class for handling API communication."""
    def __init__(self, url: str):
        self.url = url

    def fetch_data(self, code: int, limit: int) -> List[Dict[str, Any]]:
        """
        Fetches JSON data from the API.

        Args:
            code (int): Information code (551: Earthquake, 552: Tsunami)
            limit (int): The number of records to fetch.

        Returns:
            List[Dict]: A list of fetched JSON data.

        Raises:
            requests.RequestException: If a network error occurs.
        """
        params = {"codes": code, "limit": limit, "offset": 0}
        try:
            response = requests.get(self.url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error occurred: {e}")
            sys.exit(1)
        except ValueError as e:
            logging.error(f"Failed to parse JSON: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Fetch and display earthquake/tsunami information.")
    parser.add_argument("--code", type=int, default=551, choices=[551, 552], help="Information code: 551 (Earthquake) or 552 (Tsunami). (default: 551)")
    parser.add_argument("--limit", type=int, default=1, help="Number of records to fetch. (default: 1)")
    args = parser.parse_args()

    client = APIClient(config.URL)
    data_list = client.fetch_data(args.code, args.limit)

    if not data_list:
        logging.info("No data found.")
        return

    count = 1
    for data in data_list:
        info_obj: Optional[DisasterInfo] = None

        if args.code == 551:
            info_obj = Earthquake(data)
        elif args.code == 552:
            info_obj = Tsunami(data)

        print(f"-----No. {count} -----")
        if info_obj:
            info_obj.display()

        count += 1

if __name__ == "__main__":
    main()
