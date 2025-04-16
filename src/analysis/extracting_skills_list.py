import logging
import spacy
from tqdm.auto import tqdm
from spacy.matcher import PhraseMatcher

tqdm.pandas()
logger = logging.getLogger(__name__)

class SkillExtractor():
    def __init__(self, skill_list, model="pt_core_news_lg"):
        # Load spaCy language model
        try:
            self.nlp = spacy.load(model)
            logger.success(f"Successfully loaded spaCy model: {model}")
        except OSError:
            logger.error(f"Model '{model}' not found.")
            raise OSError(f"Model '{model}' not found. Install it with: python -m spacy download {model}")

        # Deduplicate and prepare skills
        self.skill_list = list(set([s.lower().strip() for s in skill_list]))
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self.prepare_matcher()

    def prepare_matcher(self):
        skill_patterns = [self.nlp.make_doc(skill) for skill in self.skill_list]
        self.matcher.add("SKILL", skill_patterns)
        logger.info(f"Prepared matcher with {len(skill_patterns)} skill patterns.")

    def extract_skills(self, text):
        try:
            doc = self.nlp(text)
            matches = self.matcher(doc)
            skills = list({doc[start:end].text.lower().strip() for _, start, end in matches})
            logger.debug(f"Extracted skills: {len(skills)} from text")
            return skills
        except Exception as e:
            logger.error(f"Failed to extract skills from text: {e}")
            return []
    
    def process_dataframe(self, df, text_column, output_format="list"):
        '''
        Processes a DataFrame and appends skill info.
        output_format: "list" for list column, "boolean" for one-hot encoded columns
        '''
        logger.info(f"Starting skill extraction for DataFrame with {len(df)} rows.")
        tqdm.pandas(desc="Extracting skills")
        df["skills_found"] = df[text_column].progress_apply(self.extract_skills)

        if output_format == "boolean":
            logger.info("Converting skills to boolean columns.")
            for skill in self.skill_list:
                df[skill] = df["skills_found"].apply(lambda x: skill in x)
            df.drop(columns="skills_found", inplace=True)

        logger.success("Skill extraction completed.")
        return df

    def export(self, df, path):
        try:
            df.to_csv(path, index=False)
            logger.info(f"Saved processed DataFrame to: {path}")
        except Exception as e:
            logger.error(f"Failed to export DataFrame to {path}: {e}")
