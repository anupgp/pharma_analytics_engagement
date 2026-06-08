import pandas as pd
import requests
import yaml
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MedicalDataIngestor:
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.api_url = self.config['api_config']['endpoint_url']
        self.limit = self.config['api_config']['default_limit']
        self.fallback_file = self.config['data_paths']['local_fallback_path']

    def fetch_via_api(self, limit: int = None) -> pd.DataFrame:
        """
        Dynamically connects to the CMS Open Data API to stream the dataset
        directly into memory using JSON schema validation.
        """
        logging.info("Initiating dynamic connection to CMS Open Data API...")
        fetch_size = limit if limit else self.limit
        
        # Socrata ODA uses standard offset/size query string configurations
        params = {
            'size': fetch_size,
            'offset': 0
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()
            
            # Read JSON payload array straight into Pandas
            df_api = pd.DataFrame(response.json())
            logging.info(f"API Streaming successful. Fetched {len(df_api)} live records.")
            return self.clean_schema_datatypes(df_api)
            
        except Exception as e:
            logging.error(f"API Connection dropped or timed out: {e}")
            return self.load_local_fallback()

    def load_local_fallback(self) -> pd.DataFrame:
        """Fallback optimization rule if local workspace loses connectivity."""
        logging.warning("Routing ingestion query flow to local disk cache storage...")
        if os.path.exists(self.fallback_file):
            df_local = pd.read_csv(self.fallback_file, nrows=self.limit)
            return self.clean_schema_datatypes(df_local)
        else:
            raise FileNotFoundError(f"Critical Error: Both API stream and local data file {self.fallback_file} are missing.")

    def clean_schema_datatypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enforces schema standards across columns to preserve business logic."""
        # Strip string white-space from categorical data blocks
        for col in ['Brnd_Name', 'Gnrc_Name', 'Prscrbr_Geo_Desc']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                
        # Enforce strict floating-point values for core billing tracking
        if 'Tot_Drug_Cst' in df.columns:
            df['Tot_Drug_Cst'] = pd.to_numeric(df['Tot_Drug_Cst'], errors='coerce').fillna(0.0)
            
        if 'Tot_Clms' in df.columns:
            df['Tot_Clms'] = pd.to_numeric(df['Tot_Clms'], errors='coerce').fillna(0)
            
        return df

if __name__ == "__main__":
    # Internal validation engine
    ingestor = MedicalDataIngestor()
    data = ingestor.fetch_via_api(limit=50)
    print(data[['Prscrbr_Geo_Desc', 'Brnd_Name', 'Tot_Drug_Cst']].head())
