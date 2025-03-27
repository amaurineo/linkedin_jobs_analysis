import logging
from pathlib import Path
from datetime import datetime

_LOG_TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')

def setup_logging(log_dir: str = 'logs') -> None:
    '''
    Set up basic logging configuration for the project
    '''
    # Prevent multiple configurations
    if logging.getLogger().hasHandlers():
        return
    
    log_file = f'{_LOG_TIMESTAMP}_pipeline.log'
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path / log_file),
            logging.StreamHandler()
        ]
    )
    
    # Adding SUCCESS level logging
    SUCCESS_LEVEL = logging.INFO + 5
    logging.addLevelName(SUCCESS_LEVEL, 'SUCCESS')
    
    def success(self, message, *args, **kwargs):
        if self.isEnabledFor(SUCCESS_LEVEL):
            self._log(SUCCESS_LEVEL, message, args, **kwargs)
    
    logging.Logger.success = success

# setup_logging()
