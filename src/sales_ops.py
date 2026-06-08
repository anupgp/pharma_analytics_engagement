import pandas as pd
import logging

class SalesOpsAnalyzer:
    def __init__(self, schema_config: dict):
        self.geo = schema_config['geo_description']
        self.brand = schema_config['brand_name']
        self.generic = schema_config['generic_name']
        self.claims = schema_config['total_claims']
        self.cost = schema_config['total_cost']

    def compute_therapeutic_market_share(self, df_cms: pd.DataFrame, target_generic: str) -> pd.DataFrame:
        """
        Analyzes a specific therapeutic molecule category (via generic name matching)
        to determine the market share breakdown of branded vs generic variants across states.
        """
        logging.info(f"Filtering dataset for molecular class signal: {target_generic}")
        
        # Safe string cleaning and filtering for the generic class (e.g., 'Atorvastatin')
        df_filtered = df_cms[df_cms[self.generic].str.upper() == target_generic.upper()].copy()
        
        if df_filtered.empty:
            logging.warning("No data records found matching the designated molecular class identifier.")
            return pd.DataFrame()

        # Enforce numeric constraints on commercial column values
        df_filtered[self.claims] = pd.to_numeric(df_filtered[self.claims], errors='coerce').fillna(0)
        df_filtered[self.cost] = pd.to_numeric(df_filtered[self.cost], errors='coerce').fillna(0)
        
        # Calculate the total class volume per geographical boundary
        geo_totals = df_filtered.groupby(self.geo)[self.claims].sum().reset_index(name='Total_Class_Claims')
        
        # Group by state and specific brand name to see brand-split layers
        brand_summary = df_filtered.groupby([self.geo, self.brand])[self.claims].sum().reset_index()
        
        # Merge datasets to evaluate fractions
        merged = brand_summary.merge(geo_totals, on=self.geo)
        merged['Market_Share_Pct'] = (merged[self.claims] / merged['Total_Class_Claims']) * 100
        
        logging.info("Regional market intelligence parameters successfully calculated.")
        return merged.sort_values(by=[self.geo, 'Market_Share_Pct'], ascending=[True, False])
