import logging
import spacy
import unicodedata
import pandas as pd
import re
from tqdm.auto import tqdm
from spacy.matcher import PhraseMatcher, Matcher
from collections import defaultdict

tqdm.pandas()
logger = logging.getLogger(__name__)

class SkillExtractor():
    def __init__(self, skill_patterns, model="pt_core_news_lg"):
        try:
            self.nlp = spacy.load(model)
            logger.success(f"Successfully loaded spaCy model: {model}")
        except OSError:
            logger.error(f"Model '{model}' not found.")
            raise OSError(f"Model '{model}' not found. Install it with: python -m spacy download {model}")

        self.skill_patterns = skill_patterns
        self.regex_patterns = {}
        self.prepare_regex_patterns()
        
        self.multi_standard_skill_map = defaultdict(set)
        for canonical, patterns in self.skill_patterns.items():
            for pattern in patterns:
                normalized_pattern = pattern.replace(r'\b', '').replace(r'\s+', ' ')
                for special_char in ['+', '*', '?', '[', ']', '(', ')', '.']:
                    normalized_pattern = normalized_pattern.replace(special_char, '')
                self.multi_standard_skill_map[normalized_pattern].add(canonical)

    def prepare_regex_patterns(self):
        """Compile regex patterns for efficient matching"""
        for skill, patterns in self.skill_patterns.items():
            compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            self.regex_patterns[skill] = compiled_patterns
        logger.info(f"Prepared regex patterns for {len(self.regex_patterns)} skills.")

    def normalize_text(self, text):
        """Normalize text by removing accents and converting to lowercase"""
        if not text:
            return ""
        return ''.join(
            c for c in unicodedata.normalize('NFD', str(text))
            if unicodedata.category(c) != 'Mn'
        ).lower().strip()
    
    def extract_skills(self, text):
        """Extract skills from text using regex patterns"""
        if not text:
            return []
        
        normalized_text = self.normalize_text(text)
        found_skills = set()
        
        for skill_name, patterns in self.regex_patterns.items():
            for pattern in patterns:
                if pattern.search(normalized_text):
                    found_skills.add(skill_name)
                    break
                    
        return list(found_skills)
    
    def process_dataframe(self, df, text_column):
        '''
        Processes a DataFrame and returns two DataFrames:
        1. Original DataFrame with job_id
        2. Skills DataFrame with job_id-to-skill mapping
        '''
        try:
            logger.info(f"Starting skill extraction for DataFrame with {len(df)} rows.")
            tqdm.pandas(desc="Extracting skills")

            if text_column not in df.columns:
                raise ValueError(f"Text column '{text_column}' not found in DataFrame.")
            
            df["skills_found"] = df[text_column].progress_apply(self.extract_skills)
            
            skills_data = []
            for job_id, skills in zip(df["job_id"], df["skills_found"]):
                try:
                    for skill in skills:
                        if skill:
                            skills_data.append({"job_id": job_id, "skill": skill})
                except Exception as e:
                    logger.warning(f"Error processing skills for job_id {job_id}: {str(e)}")
            
            df_skills = pd.DataFrame(skills_data)
            df = df.drop(columns=["skills_found"])
            logger.info("Skill extraction completed.")
            return df, df_skills
        
        except Exception as e:
            logger.error(f"An unexpected error occurred during processing: {str(e)}")
            raise e

    def export(self, df, path):
        try:
            df.to_csv(path, index=False)
            logger.info(f"Saved processed DataFrame to: {path}")
        except Exception as e:
            logger.error(f"Failed to export DataFrame to {path}: {e}")
            raise e
            
