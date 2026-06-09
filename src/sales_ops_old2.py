# from bokeh.plotting import figure, show
# from bokeh.models import ColumnDataSource, CustomJS, Select, HoverTool
# from bokeh.layouts import column, row
# from bokeh.transform import factor_cmap
# from bokeh.palettes import Category10_6  # swapped Blue6 for Category10_6
# import bokeh.io
# import pandas as pd
# import numpy as np
# import logging
# import json

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# class SalesOpsAnalyzer:
#     def __init__(self, schema_config: dict):
#         """Initializes the analyzer with the central YAML schema configuration."""
#         self.geo = schema_config['geo_description']
#         self.brand = schema_config['brand_name']
#         self.generic = schema_config['generic_name']
#         self.claims = schema_config['total_claims']
#         self.cost = schema_config['total_cost']



from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, CustomJS, Select, HoverTool
from bokeh.layouts import column, row
from bokeh.transform import factor_cmap
from bokeh.palettes import Category10_6
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

    def compute_global_metrics_from_file_one_drug(self, file_path: str, target_generic: str) -> pd.DataFrame:
        """Streams a massive file in chunks to extract and aggregate market share metrics."""
        logging.info(f"🔄 Starting global stream aggregation for molecule: {target_generic}")
        chunk_summaries = []
            
        for chunk in pd.read_csv(file_path, chunksize=100000):
            filtered_chunk = chunk[chunk[self.generic].astype(str).str.upper() == target_generic.upper()].copy()
            if filtered_chunk.empty:
                continue
            
            filtered_chunk[self.claims] = pd.to_numeric(filtered_chunk[self.claims], errors='coerce').fillna(0)
            filtered_chunk[self.cost] = pd.to_numeric(filtered_chunk[self.cost], errors='coerce').fillna(0.0)
            
            chunk_agg = filtered_chunk.groupby([self.geo, self.brand, self.generic]).agg(
                Claims_Sum=(self.claims, 'sum'),
                Cost_Sum=(self.cost, 'sum')
            ).reset_index()
            chunk_summaries.append(chunk_agg)
            
        if not chunk_summaries:
            return pd.DataFrame()
        
        master_summary = pd.concat(chunk_summaries, ignore_index=True)
        final_aggregation = master_summary.groupby([self.geo, self.brand, self.generic]).agg(
            Total_Claims=('Claims_Sum', 'sum'),
            Total_Cost=('Cost_Sum', 'sum')
        ).reset_index()
        
        geo_totals = final_aggregation.groupby(self.geo)['Total_Claims'].sum().reset_index(name='Total_Class_Claims')
        final_metrics = final_aggregation.merge(geo_totals, on=self.geo)
        final_metrics['Market_Share_Pct'] = (final_metrics['Total_Claims'] / final_metrics['Total_Class_Claims']) * 100
        
        return final_metrics.rename(columns={'Total_Claims': self.claims, 'Total_Cost': self.cost})


    def compute_global_metrics_from_file(self, file_path: str) -> pd.DataFrame:
        """
        Streams the ENTIRE multi-gigabyte dataset file in chunks to aggregate and calculate
        market share metrics for EVERY drug molecule simultaneously without running out of RAM.
        """
        logging.info("🔄 Starting complete global stream reduction for ALL molecules...")
        chunk_summaries = []
        
        # Stream the full file in blocks while forcing str data types to suppress DtypeWarnings
        for chunk in pd.read_csv(file_path, chunksize=150000, dtype=str):
            # Clean categories to remove white-space padding anomalies
            chunk[self.geo] = chunk[self.geo].astype(str).str.strip()
            chunk[self.generic] = chunk[self.generic].astype(str).str.strip()
            chunk[self.brand] = chunk[self.brand].astype(str).str.strip()
            
            # Enforce explicit numeric constraints
            chunk[self.claims] = pd.to_numeric(chunk[self.claims], errors='coerce').fillna(0)
            chunk[self.cost] = pd.to_numeric(chunk[self.cost], errors='coerce').fillna(0.0)
            
            # Compress rows immediately within the current chunk boundaries
            chunk_agg = chunk.groupby([self.geo, self.brand, self.generic]).agg(
                Claims_Sum=(self.claims, 'sum'),
                Cost_Sum=(self.cost, 'sum')
            ).reset_index()
            
            chunk_summaries.append(chunk_agg)
            
        if not chunk_summaries:
            logging.error("❌ No valid data rows identified in file stream.")
            return pd.DataFrame()
            
        logging.info("Merging chunk blocks into the master reduction framework...")
        master_summary = pd.concat(chunk_summaries, ignore_index=True)
        
        # Combine duplicates across chunk intersections
        final_aggregation = master_summary.groupby([self.geo, self.brand, self.generic]).agg(
            Total_Claims=('Claims_Sum', 'sum'),
            Total_Cost=('Cost_Sum', 'sum')
        ).reset_index()
        
        logging.info("Deriving relative market share indicators...")
        class_totals = final_aggregation.groupby([self.geo, self.generic])['Total_Claims'].sum().reset_index(name='Total_Class_Claims')
        final_metrics = final_aggregation.merge(class_totals, on=[self.geo, self.generic])
        
        final_metrics['Market_Share_Pct'] = np.where(
            final_metrics['Total_Class_Claims'] > 0,
            (final_metrics['Total_Claims'] / final_metrics['Total_Class_Claims']) * 100,
            0.0
        )
        
        logging.info("✅ Global metrics compiled across the complete dataset for ALL drugs.")
        return final_metrics.rename(columns={'Total_Claims': self.claims, 'Total_Cost': self.cost})

    def generate_interactive_dashboard_global(self, df_insights: pd.DataFrame):
        """Builds a foolproof, cascading interactive bar chart dashboard panel."""
        logging.info("Initializing cascading bar chart panel...")

        df_active = df_insights[df_insights[self.claims] > 0].copy()
        if df_active.empty:
            print("❌ Input dataframe contains no active rows with claims > 0.")
            return

        # Map territories to active drugs to prevent empty selections
        valid_map_json = {}
        for geo_val, group_df in df_active.groupby(self.geo):
            valid_map_json[str(geo_val)] = sorted(list(group_df[self.generic].unique()))

        # 🚀 THE CRUCIAL FIX: Extract safe default string values out of the index arrays
        available_geos = sorted(list(valid_map_json.keys()))
        default_geo = 'National' if 'National' in available_geos else available_geos[0]
        
        default_drugs = valid_map_json[default_geo]
        default_drug = default_drugs[0] if default_drugs else ""

        print(f"📊 Display Initialized: Territory -> '{default_geo}' | Target Drug Class -> '{default_drug}'")

        # Slice the initial clean data frame view safely using individual strings
        initial_df = df_active[(df_active[self.geo] == default_geo) & (df_active[self.generic] == default_drug)].sort_values(by='Market_Share_Pct', ascending=False)
        initial_brands = initial_df[self.brand].tolist()

        master_source = ColumnDataSource(df_active)
        visible_source = ColumnDataSource(initial_df)

        # Construct clean Bar Chart
        p = figure(
            x_range=initial_brands if initial_brands else ["None"], height=420, width=750,
            title="Therapeutic Brand Market Share Representation",
            toolbar_location="above", tools="pan,wheel_zoom,box_zoom,reset,save"
        )

        p.vbar(
            x=self.brand, top='Market_Share_Pct', width=0.5, 
            source=visible_source, line_color="white",
            fill_color=factor_cmap(self.brand, palette=Category10_6, factors=initial_brands if initial_brands else ["None"])
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
        p.xaxis.major_label_orientation = 0.3
        p.xgrid.grid_line_color = None

        # Build Select Menus
        geo_select = Select(title="Select Territory:", value=default_geo, options=available_geos)
        drug_select = Select(title="Select Generic Class:", value=default_drug, options=default_drugs)

        # JavaScript Cascading Logic for Bar Updates
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
            
            for (let key in vis_data) {{
                vis_data[key] = [];
            }}
            
            const unique_brands = [];
            
            for (let i = 0; i < data['{self.geo}'].length; i++) {{
                if (data['{self.geo}'][i] === current_geo && data['{self.generic}'][i] === current_drug) {{
                    for (let key in vis_data) {{
                        vis_data[key].push(data[key][i]);
                    }}
                    unique_brands.push(data['{self.brand}'][i]);
                }}
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


    def generate_interactive_dashboard_one_drug(self, df_insights: pd.DataFrame):
        """Builds a foolproof, cascading interactive bar chart dashboard panel."""
        logging.info("Initializing cascading bar chart panel...")

        df_active = df_insights[df_insights[self.claims] > 0].copy()
        if df_active.empty:
            print("❌ Input dataframe is empty.")
            return

        # Map territories to active drugs to prevent empty selections
        valid_map_json = {}
        for geo_val, group_df in df_active.groupby(self.geo):
            valid_map_json[str(geo_val)] = list(group_df[self.generic].unique())

        available_geos = sorted(list(valid_map_json.keys()))
        default_geo = 'National' if 'National' in available_geos else available_geos[0]
        default_drugs = sorted(valid_map_json[default_geo])
        default_drug = default_drugs[0] if default_drugs else ""

        # Slice initial view
        initial_df = df_active[(df_active[self.geo] == default_geo) & (df_active[self.generic] == default_drug)].sort_values(by='Market_Share_Pct', ascending=False)
        initial_brands = initial_df[self.brand].tolist()

        master_source = ColumnDataSource(df_active)
        visible_source = ColumnDataSource(initial_df)

        p = figure(
            x_range=initial_brands, height=400, width=750,
            title="Therapeutic Brand Market Share Representation",
            toolbar_location="above", tools="pan,wheel_zoom,box_zoom,reset,save"
        )

        # 🚀 FIX 2: Bind Category10_6 to factor_cmap
        p.vbar(
            x=self.brand, top='Market_Share_Pct', width=0.5, 
            source=visible_source, line_color="white",
            fill_color=factor_cmap(self.brand, palette=Category10_6, factors=initial_brands)
        )
        
        # Add interactive tools
        hover = HoverTool()
        hover.tooltips = [
            ("Brand Name", f"@{self.brand}"),
            ("Market Share %", "@Market_Share_Pct{0.00}%"),
            ("Prescription Count", f"@{self.claims}{{,}}"),
            ("Financial Cost", f"@{self.cost}{{$0,0.00}}")
        ]
        p.add_tools(hover)

        # Polish graph layouts
        p.y_range.start = 0
        p.y_range.end = 105
        p.yaxis.axis_label = "Relative Market Share (%)"
        p.xaxis.major_label_orientation = 0.3
        p.xgrid.grid_line_color = None

        # Build Select Menus
        geo_select = Select(title="Select Territory:", value=default_geo, options=available_geos)
        drug_select = Select(title="Select Generic Class:", value=default_drug, options=default_drugs)

        # JavaScript Cascading Logic for Bar Updates
        callback_code = f"""
            const data = master_source.data;
            const vis_data = visible_source.data;
            const valid_combos = {json.dumps(valid_map_json)};
            
            const current_geo = geo_widget.value;
            let current_drug = drug_widget.value;
            
            const allowed_drugs = valid_combos[current_geo].sort();
            drug_widget.options = allowed_drugs;
            
            if (!allowed_drugs.includes(current_drug)) {{
                current_drug = allowed_drugs[0];
                drug_widget.value = current_drug;
            }}
            
            for (let key in vis_data) {{
                vis_data[key] = [];
            }}
            
            const unique_brands = [];
            
            for (let i = 0; i < data['{self.geo}'].length; i++) {{
                if (data['{self.geo}'][i] === current_geo && data['{self.generic}'][i] === current_drug) {{
                    for (let key in vis_data) {{
                        vis_data[key].push(data[key][i]);
                    }}
                    unique_brands.push(data['{self.brand}'][i]);
                }}
            }}
            
            // Push axis factors update directly
            x_range.factors = unique_brands;
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
        
