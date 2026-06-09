from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, CustomJS, Select, HoverTool
from bokeh.layouts import column, row
from bokeh.palettes import Category20
from bokeh.transform import cumsum
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

    def compute_global_metrics_from_file(self, file_path: str, target_generic: str) -> pd.DataFrame:
        """
        Streams a massive, multi-gigabyte file in chunks to aggregate and calculate
        market share metrics across the entire dataset without exhausting system RAM.
        """
        logging.info(f"🔄 Starting global stream aggregation for molecule: {target_generic}")
        
        chunk_summaries = []
        
        # Stream the full un-sampled file in manageable 100,000-row blocks
        for chunk in pd.read_csv(file_path, chunksize=100000):
            # 1. Immediate data reduction: keep only the targeted generic drug rows
            filtered_chunk = chunk[chunk[self.generic].astype(str).str.upper() == target_generic.upper()].copy()
            
            if filtered_chunk.empty:
                continue
                
            # 2. Enforce explicit numeric constraints
            filtered_chunk[self.claims] = pd.to_numeric(filtered_chunk[self.claims], errors='coerce').fillna(0)
            filtered_chunk[self.cost] = pd.to_numeric(filtered_chunk[self.cost], errors='coerce').fillna(0.0)
            
            # 3. Aggregate this localized block immediately to reduce memory footprint
            chunk_agg = filtered_chunk.groupby([self.geo, self.brand]).agg(
                Claims_Sum=(self.claims, 'sum'),
                Cost_Sum=(self.cost, 'sum')
            ).reset_index()
            
            chunk_summaries.append(chunk_agg)
            
        if not chunk_summaries:
            logging.warning("❌ No matching records identified in the global file stream.")
            return pd.DataFrame()
            
        # 4. Consolidate all the lightweight block summaries into a master frame
        master_summary = pd.concat(chunk_summaries, ignore_index=True)
        
        # 5. Re-aggregate to combine records split across different chunks
        final_aggregation = master_summary.groupby([self.geo, self.brand]).agg(
            Total_Claims=('Claims_Sum', 'sum'),
            Total_Cost=('Cost_Sum', 'sum')
        ).reset_index()
        
        # 6. Compute final relative performance metrics
        geo_totals = final_aggregation.groupby(self.geo)['Total_Claims'].sum().reset_index(name='Total_Class_Claims')
        final_metrics = final_aggregation.merge(geo_totals, on=self.geo)
        
        final_metrics['Market_Share_Pct'] = (final_metrics['Total_Claims'] / final_metrics['Total_Class_Claims']) * 100
        
        # Rename column to match schema references in the dashboard
        final_metrics = final_metrics.rename(columns={
            'Total_Claims': self.claims,
            'Total_Cost': self.cost
        })
        
        logging.info("✅ Global metrics successfully computed across the complete dataset.")
        return final_metrics.sort_values(by=[self.geo, 'Market_Share_Pct'], ascending=[True, False])

    def generate_interactive_dashboard(self, df_insights: pd.DataFrame):

        """
        Builds a cascading dynamic dashboard panel using configuration-driven schema mapping keys.
        """
        logging.info("Initializing cascading selector pipeline with Pie Chart transformations...")

        # 🚀 CHANGE THESE LINES HERE: Force dropdown maps to use the config mappings
        # Instead of 'df_insights['Tot_Clms'] > 0', use the dynamic key:
        df_active = df_insights[df_insights[self.claims] > 0].copy()

        # Build a complete map of valid states and their active generic medications using configuration mapping keys
        valid_map = df_active.groupby(self.geo)[self.generic].to_dict() if hasattr(df_active.groupby(self.geo)[self.generic], 'to_dict') else df_active.groupby(self.geo).apply(lambda x: list(x[self.generic].unique())).to_dict()
        valid_map_json = {k: list(v) for k, v in valid_map.items()}

        # Extract sorting parameters dynamically
        available_geos = sorted(list(valid_map_json.keys()))
        default_geo = 'National' if 'National' in available_geos else available_geos[0]
        default_drugs = sorted(valid_map_json[default_geo])
        default_drug = default_drugs[0] if default_drugs else ""
        
        # Format initial dataset block to draw a 100% Pie Chart structure
        initial_df = df_active[(df_active[self.geo] == default_geo) & (df_active[self.generic] == default_drug)].copy()
        
        # Calculate localized market share percentages explicitly
        total_class_claims = initial_df[self.claims].sum()
        if total_class_claims > 0:
            initial_df['Share_Pct'] = (initial_df[self.claims] / total_class_claims) * 100
        else:
            initial_df['Share_Pct'] = 0.0

        # Translate percentages to radian angles for Bokeh
        initial_df['angle'] = (initial_df['Share_Pct'] / 100) * 2 * np.pi
        
        # Assign dynamic colors to pie slices
        colors = list(Category20[20]) if len(initial_df) <= 20 else list(Category20[20]) * (len(initial_df)//20 + 1)
        initial_df['color'] = colors[:len(initial_df)]

        master_source = ColumnDataSource(df_active)
        visible_source = ColumnDataSource(initial_df)

        # Construct the Pie Chart Workspace
        p = figure(
            height=450, width=700, 
            title="Therapeutic Brand Market Share Representation",
            toolbar_location="above",
            tools="pan,wheel_zoom,reset,save",
            x_range=(-1.2, 1.2), y_range=(-1.2, 1.2)
        )

        p.wedge(
            x=0, y=0, radius=0.8,
            start_angle=cumsum('angle', include_zero=True),
            end_angle=cumsum('angle'),
            line_color="white", fill_color='color', 
            legend_field=self.brand, source=visible_source
        )

        # Add interactive tooltip elements
        hover = HoverTool()
        hover.tooltips = [
            ("Brand Variant", f"@{self.brand}"),
            ("Market Share %", "@Share_Pct{0.00}%"),
            ("Prescription Count", f"@{self.claims}{{,}}"),
            ("Financial Cost", f"@{self.cost}{{$0,0.00}}")
        ]
        p.add_tools(hover)

        # Hide layout grids for a clean appearance
        p.axis.axis_label = None
        p.axis.visible = False
        p.grid.grid_line_color = None
        p.legend.label_text_font_size = "9pt"
        p.legend.location = "right"

        # Construct the Select Dropdowns
        geo_select = Select(title="Select Territory:", value=default_geo, options=available_geos)
        drug_select = Select(title="Select Generic Class:", value=default_drug, options=default_drugs)

        # Cascading Filter JavaScript Code
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
            
            let matching_indices = [];
            let total_claims_sum = 0;
            
            for (let i = 0; i < data['{self.geo}'].length; i++) {{
                if (data['{self.geo}'][i] === current_geo && data['{self.generic}'][i] === current_drug) {{
                    matching_indices.push(i);
                    total_claims_sum += parseFloat(data['{self.claims}'][i]) || 0;
                }}
            }}
            
            for (let key in vis_data) {{
                vis_data[key] = [];
            }}
            
            const color_palette = {json.dumps(colors)};
            
            for (let idx = 0; idx < matching_indices.length; idx++) {{
                let i = matching_indices[idx];
                let current_claims = parseFloat(data['{self.claims}'][i]) || 0;
                let current_share = total_claims_sum > 0 ? (current_claims / total_claims_sum) * 100 : 0;
                let current_angle = (current_share / 100) * 2 * Math.PI;
                
                vis_data['{self.geo}'].push(data['{self.geo}'][i]);
                vis_data['{self.brand}'].push(data['{self.brand}'][i]);
                vis_data['{self.generic}'].push(data['{self.generic}'][i]);
                vis_data['{self.claims}'].push(current_claims);
                vis_data['{self.cost}'].push(parseFloat(data['{self.cost}'][i]) || 0);
                vis_data['Share_Pct'].push(current_share);
                vis_data['angle'].push(current_angle);
                vis_data['color'].push(color_palette[idx % color_palette.length]);
            }}
            
            visible_source.change.emit();
        """

        custom_callback = CustomJS(
            args=dict(
                master_source=master_source,
                visible_source=visible_source,
                geo_widget=geo_select,
                drug_widget=drug_select
            ),
            code=callback_code
        )

        geo_select.js_on_change('value', custom_callback)
        drug_select.js_on_change('value', custom_callback)

        dashboard_layout = column(
            row(geo_select, drug_select, width=700),
            p
        )

        # Force render inline within the active Jupyter environment
        bokeh.io.output_notebook()
        show(dashboard_layout)

