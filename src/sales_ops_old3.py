from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, CustomJS, Select, HoverTool
from bokeh.layouts import column, row
import bokeh.io
import pandas as pd
import numpy as np
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SalesOpsAnalyzer:
    def __init__(self, schema_config: dict):
        """Initializes the analyzer with the central YAML schema configuration."""
        self.geo = schema_config['geo_description']
        self.brand = schema_config['brand_name']
        self.generic = schema_config['generic_name']
        self.claims = schema_config['total_claims']
        self.cost = schema_config['total_cost']

    def compute_global_metrics_from_file(self, file_path: str) -> pd.DataFrame:
        """
        Streams the ENTIRE multi-gigabyte dataset file in chunks to aggregate and calculate
        market share metrics for EVERY drug molecule simultaneously without running out of RAM.
        """
        logging.info("🔄 Starting complete global stream reduction for ALL molecules...")
        chunk_summaries = []
        
        for chunk in pd.read_csv(file_path, chunksize=150000, dtype=str):
            chunk[self.geo] = chunk[self.geo].astype(str).str.strip()
            chunk[self.generic] = chunk[self.generic].astype(str).str.strip()
            chunk[self.brand] = chunk[self.brand].astype(str).str.strip()
            
            chunk[self.claims] = pd.to_numeric(chunk[self.claims], errors='coerce').fillna(0)
            chunk[self.cost] = pd.to_numeric(chunk[self.cost], errors='coerce').fillna(0.0)
            
            chunk_agg = chunk.groupby([self.geo, self.brand, self.generic]).agg(
                Claims_Sum=(self.claims, 'sum'),
                Cost_Sum=(self.cost, 'sum')
            ).reset_index()
            
            chunk_summaries.append(chunk_agg)
            
        if not chunk_summaries:
            logging.error("❌ No valid data rows identified in file stream.")
            return pd.DataFrame()
            
        master_summary = pd.concat(chunk_summaries, ignore_index=True)
        
        final_aggregation = master_summary.groupby([self.geo, self.brand, self.generic]).agg(
            Total_Claims=('Claims_Sum', 'sum'),
            Total_Cost=('Cost_Sum', 'sum')
        ).reset_index()
        
        class_totals = final_aggregation.groupby([self.geo, self.generic])['Total_Claims'].sum().reset_index(name='Total_Class_Claims')
        final_metrics = final_aggregation.merge(class_totals, on=[self.geo, self.generic])
        
        final_metrics['Market_Share_Pct'] = np.where(
            final_metrics['Total_Class_Claims'] > 0,
            (final_metrics['Total_Claims'] / final_metrics['Total_Class_Claims']) * 100,
            0.0
        )
        
        return final_metrics.rename(columns={'Total_Claims': self.claims, 'Total_Cost': self.cost})

    def generate_interactive_dashboard(self, df_insights: pd.DataFrame):
        """Builds a foolproof, cascading interactive bar chart dashboard panel."""
        logging.info("Initializing cascading bar chart panel...")

        df_active = df_insights[df_insights[self.claims] > 0].copy()
        if df_active.empty:
            print("❌ Input dataframe contains no active rows.")
            return

        # Map territories to active drugs
        valid_map_json = {}
        for geo_val, group_df in df_active.groupby(self.geo):
            valid_map_json[str(geo_val)] = sorted(list(group_df[self.generic].unique()))

        available_geos = sorted(list(valid_map_json.keys()))
        
        # Determine starting territory
        default_geo = 'National' if 'National' in available_geos else available_geos

        # Focus on the highest volume molecule at startup
        df_geo_slice = df_active[df_active[self.geo] == default_geo]
        top_drug_series = df_geo_slice.groupby(self.generic)[self.claims].sum().sort_values(ascending=False)
        
        default_drug = str(top_drug_series.index[0]) if not top_drug_series.empty else valid_map_json[default_geo][0]
        default_drugs = valid_map_json[default_geo]

        print(f"📊 Dashboard active view -> Territory: '{default_geo}' | High-Signal Drug Family: '{default_drug}'")
        
        # Build initial sorted display view
        initial_df = df_geo_slice[df_geo_slice[self.generic] == default_drug].sort_values(by='Market_Share_Pct', ascending=False)
        initial_brands = initial_df[self.brand].tolist()

        master_source = ColumnDataSource(df_active)
        visible_source = ColumnDataSource(initial_df)

        p = figure(
            x_range=initial_brands if initial_brands else ["None"], height=450, width=800,
            title="Therapeutic Brand Market Share Representation",
            toolbar_location="above", tools="pan,wheel_zoom,box_zoom,reset,save"
        )

        p.vbar(
            x=self.brand, top='Market_Share_Pct', width=0.6, 
            source=visible_source, line_color="white", fill_color="#1f77b4"
        )

        hover = HoverTool()
        hover.tooltips = [
            ("Brand Name", f"@{self.brand}"),
            ("Market Share %", "@Market_Share_Pct{0.00}%"),
            ("Prescription Count", f"@{self.claims}{{,}}"),
            ("Financial Cost", f"@{self.cost}{{$0,0.00}}")
        ]
        p.add_tools(hover)

        p.y_range.start = 0
        p.y_range.end = 105
        p.yaxis.axis_label = "Relative Market Share (%)"
        p.xaxis.major_label_orientation = 0.5
        p.xgrid.grid_line_color = None

        geo_select = Select(title="Select Territory:", value=default_geo, options=available_geos)
        drug_select = Select(title="Select Generic Class:", value=default_drug, options=default_drugs)

        # 🚀 THE DEFINITIVE JAVASCRIPT MATCHING FIX: 
        # Enforces case-insensitive, whitespace-trimmed string evaluation (.trim().toUpperCase())
        callback_code = f"""
            const data = master_source.data;
            const vis_data = visible_source.data;
            const valid_combos = {json.dumps(valid_map_json)};
            
            const current_geo = geo_widget.value;
            let current_drug = drug_widget.value;
            
            const allowed_drugs = valid_combos[current_geo];
            drug_widget.options = allowed_drugs;
            
            if (!allowed_drugs.includes(current_drug)) {{
                current_drug = allowed_drugs[0] || "";
                drug_widget.value = current_drug;
            }}
            
            // Normalize target parameters for safety matching
            const target_geo_clean = current_geo.trim().toUpperCase();
            const target_drug_clean = current_drug.trim().toUpperCase();
            
            let temp_records = [];
            for (let i = 0; i < data['{self.geo}'].length; i++) {{
                const current_row_geo = String(data['{self.geo}'][i]).trim().toUpperCase();
                const current_row_drug = String(data['{self.generic}'][i]).trim().toUpperCase();
                
                // Safe lookup matches
                if (current_row_geo === target_geo_clean && current_row_drug === target_drug_clean) {{
                    temp_records.push({{
                        geo: data['{self.geo}'][i],
                        brand: data['{self.brand}'][i],
                        generic: data['{self.generic}'][i],
                        claims: parseFloat(data['{self.claims}'][i]) || 0,
                        cost: parseFloat(data['{self.cost}'][i]) || 0,
                        share: parseFloat(data['Market_Share_Pct'][i]) || 0
                    }});
                }}
            }}
            
            temp_records.sort((a, b) => b.share - a.share);
            
            for (let key in vis_data) {{
                vis_data[key] = [];
            }}
            
            const unique_brands = [];
            for (let i = 0; i < temp_records.length; i++) {{"
                vis_data['{self.geo}'].push(temp_records[i].geo);
                vis_data['{self.brand}'].push(temp_records[i].brand);
                vis_data['{self.generic}'].push(temp_records[i].generic);
                vis_data['{self.claims}'].push(temp_records[i].claims);
                vis_data['{self.cost}'].push(temp_records[i].cost);
                vis_data['Market_Share_Pct'].push(temp_records[i].share);
                unique_brands.push(temp_records[i].brand);
            }}
            
            x_range.factors = unique_brands.length > 0 ? unique_brands : ["None"];
            visible_source.change.emit();
        """

        custom_callback = CustomJS(
            args=dict(master_source=master_source, visible_source=visible_source,
                      geo_widget=geo_select, drug_widget=drug_select, x_range=p.x_range),
            code=callback_code
        )

        geo_select.js_on_change('value', custom_callback)
        drug_select.js_on_change('value', custom_callback)

        dashboard_layout = column(row(geo_select, drug_select, width=750), p)
        show(dashboard_layout)
