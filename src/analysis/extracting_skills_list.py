import logging
import spacy
import unicodedata
import pandas as pd
from tqdm.auto import tqdm
from spacy.matcher import PhraseMatcher
from collections import defaultdict

tqdm.pandas()
logger = logging.getLogger(__name__)

class SkillExtractor():
    def __init__(self, skill_list, standard_skill_map=None, model="pt_core_news_lg"):
        try:
            self.nlp = spacy.load(model)
            logger.success(f"Successfully loaded spaCy model: {model}")
        except OSError:
            logger.error(f"Model '{model}' not found.")
            raise OSError(f"Model '{model}' not found. Install it with: python -m spacy download {model}")

        self.skill_list = list(set([self.normalize_text(s) for s in skill_list]))
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self.prepare_matcher()

        self.multi_standard_skill_map = defaultdict(set)
        if standard_skill_map:
            for canonical, variants in standard_skill_map.items():
                for variant in variants:
                    normalized = self.normalize_text(variant)
                    self.multi_standard_skill_map[normalized].add(canonical)

    def prepare_matcher(self):
        skill_patterns = [self.nlp.make_doc(skill) for skill in self.skill_list]
        self.matcher.add("SKILL", skill_patterns)
        logger.info(f"Prepared matcher with {len(skill_patterns)} skill patterns.")

    def normalize_text(self, text):
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        ).lower().strip()
    
    def standardize_skills(self, skills):
        standardized = set()
        for skill in skills:
            matches = self.multi_standard_skill_map.get(skill, {skill})
            standardized.update(matches)
        return list(standardized)

    def extract_skills(self, text):
        try:
            doc = self.nlp(text)
            matches = self.matcher(doc)
            raw_skills = {self.normalize_text(doc[start:end].text) for _, start, end in matches}
            skills = self.standardize_skills(raw_skills)
            logger.debug(f"Extracted skills: {skills}")
            return skills
        except Exception as e:
            logger.error(f"Failed to extract skills from text: {e}")
            return []
    
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
            normalized_to_canonical = {}
            for variants, canonicals in self.multi_standard_skill_map.items():
                for canonical in canonicals:
                    normalized_to_canonical[variants] = canonical

            df_skills["skill"] = df_skills["skill"].map(lambda x: normalized_to_canonical.get(x, x))
            df = df.drop(columns=["skills_found"])
            logger.info("Skill extraction completed.")
            return df, df_skills
        
        except Exception as e:
            logger.error(f"An unexpected error occurred during processing: {str(e)}")

    def export(self, df, path):
        try:
            df.to_csv(path, index=False)
            logger.info(f"Saved processed DataFrame to: {path}")
        except Exception as e:
            logger.error(f"Failed to export DataFrame to {path}: {e}")
            
