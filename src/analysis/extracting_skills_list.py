import logging
import re
import unicodedata

import pandas as pd
from tqdm import tqdm

logger = logging.getLogger(__name__)


class SkillExtractor:
    """
    A class to extract skills from text using regular expressions and process DataFrames.
    """

    def __init__(self, skill_patterns):
        r"""
        Initialize the SkillExtractor.

        Args:
            skill_patterns (dict): A dictionary where keys are canonical skill names
                                   and values are lists of regex patterns for that skill.
                                   Example: {'Python': [r'\bpython\b', r'\bdjango\b'],
                                             'Java': [r'\bjava\b', r'\bspring\b']}
        """
        if not isinstance(skill_patterns, dict):
            raise TypeError('skill_patterns must be a dictionary.')

        self.skill_patterns = skill_patterns
        self.regex_patterns = {}
        self._prepare_regex_patterns()

    def _prepare_regex_patterns(self):
        """
        Compiles regex patterns for efficient matching.
        Patterns are compiled with re.IGNORECASE.
        """
        for skill_name, patterns in self.skill_patterns.items():
            if not isinstance(patterns, list):
                logger.warning(
                    f"Patterns for skill '{skill_name}' is not a list. Skipping this skill."
                )
                continue

            compiled_patterns = []
            for pattern_str in patterns:
                try:
                    compiled_patterns.append(
                        re.compile(pattern_str, re.IGNORECASE)
                    )
                except re.error as e:
                    logger.error(
                        f"Invalid regex pattern for skill '{skill_name}': '{pattern_str}'. Error: {e}"
                    )

            if compiled_patterns:
                self.regex_patterns[skill_name] = compiled_patterns
            else:
                logger.warning(
                    f"No valid regex patterns were compiled for skill '{skill_name}'."
                )

        if self.regex_patterns:
            logger.success(
                f'Successfully prepared regex patterns for {len(self.regex_patterns)} skills.'
            )
        else:
            logger.warning(
                'No regex patterns were prepared. Skill extraction will not find any skills.'
            )

    def normalize_text(self, text: str) -> str:
        """
        Normalize text by removing accents, converting to lowercase, and stripping whitespace.

        Args:
            text (str): The input string to normalize.

        Returns:
            str: The normalized string. Returns an empty string if input is None or empty.
        """
        if not text:
            return ''
        try:
            # Decompose Unicode characters (e.g., 'é' to 'e' and combining acute accent)
            nfkd_form = unicodedata.normalize('NFD', str(text))
            # Keep only non-spacing marks (remove accents)
            normalized_string = ''.join(
                [c for c in nfkd_form if not unicodedata.combining(c)]
            )
            return normalized_string.lower().strip()
        except Exception as e:
            logger.warning(
                f"Could not normalize text: '{text[:50]}...'. Error: {e}"
            )
            return str(text).lower().strip()

    def extract_skills(self, text: str) -> list:
        """
        Extract skills from a given text using the pre-compiled regex patterns.

        Args:
            text (str): The text from which to extract skills.

        Returns:
            list: A list of unique canonical skill names found in the text.
                  Returns an empty list if input text is None or empty, or no skills are found.
        """
        if not text:
            return []

        normalized_text = self.normalize_text(text)
        if not normalized_text:
            return []

        found_skills = set()

        for skill_name, compiled_patterns in self.regex_patterns.items():
            for pattern in compiled_patterns:
                if pattern.search(normalized_text):
                    found_skills.add(skill_name)
                    break

        return list(found_skills)

    def process_dataframe(
        self, df: pd.DataFrame, text_column: str
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Process a DataFrame to extract skills from a specified text column.

        Args:
            df (pd.DataFrame): The input DataFrame.
            text_column (str): The name of the column containing the text to analyze.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]:
                1. The original DataFrame (or a copy, if modified) without the temporary 'skills_found' column.
                2. A new DataFrame (df_skills) with two columns: the id_column and 'skill',
                   mapping each job ID to an individual extracted skill.

        Raises:
            ValueError: If the text_column or id_column is not found in the DataFrame.
            Exception: Propagates other unexpected errors during processing.
        """
        if text_column not in df.columns:
            raise ValueError(
                f"Text column '{text_column}' not found in DataFrame."
            )

        try:
            logger.info(
                f'Starting skill extraction for DataFrame with {len(df)} rows.'
            )
            tqdm.pandas(desc='Extracting skills')

            df_processed = df.copy()

            df_processed['skills_found'] = df_processed[
                text_column
            ].progress_apply(self.extract_skills)

            skills_data = []
            for index, row in df_processed.iterrows():
                job_id_val = row['job_id']
                extracted_skills_list = row['skills_found']
                try:
                    for skill in extracted_skills_list:
                        if skill:
                            skills_data.append(
                                {'job_id': job_id_val, 'skill': skill}
                            )
                except Exception as e:
                    logger.warning(
                        f'Error processing skills for job_id {job_id_val}: {str(e)}. Skills list: {extracted_skills_list}'
                    )

            df_skills = pd.DataFrame(skills_data)

            # Drop the temporary column from the processed DataFrame copy
            df_processed = df_processed.drop(columns=['skills_found'])

            logger.info(
                f'Skill extraction completed. Found {len(df_skills)} skill entries.'
            )
            return df_processed, df_skills

        except Exception as e:
            logger.error(
                f'An unexpected error occurred during processing: {str(e)}'
            )
            raise e

    def export(self, df, path):
        """
        Export a DataFrame to a CSV file.

        Args:
            df (pd.DataFrame): The DataFrame to export.
            path (str): The file path where the CSV will be saved.

        Raises:
            Exception: If an error occurs during file saving.
        """
        try:
            df.to_csv(path, index=False)
            logger.info(f'Saved processed DataFrame to: {path}')
        except Exception as e:
            logger.error(f'Failed to export DataFrame to {path}: {e}')
            raise e
