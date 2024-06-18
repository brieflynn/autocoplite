import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
pd.options.mode.chained_assignment = None
import sys

class AutocopLite:
    """
    tools for processing summary csv files obtained from rocm profile data RPD files 
    this class provides methods for formatting the csv data, creating standalone single plots of single traces or comparative plots provided multiple trace csv files (two max)
    specify as input the name of the input csv file obtained from lucid drop down menu or other, the architecture (rocm or nvidia) and the name of the output html file
    download the html file and view in your browser

    see commented out examples below
    """
    def __init__(self, color_map=None):
        # Set the default color map if none is provided
        if color_map is None:
            self.color_map = {
                'GEMMs': '#072AC8',
                'RCCL/NCCL': '#1E96FC',
                'Elementwise': '#A2D6F9',
                'Reduce': '#FCF300',   
                'Misc': '#FFC600',      
                'Nvidia': '#8C564B',    
                'ROCm': '#E377C2'     
            }
        else:
            self.color_map = color_map

    def process_file(self, csv_file, architecture):

        def insert_string_every_n_chars(s, n, insert_str='<br>'):
            return insert_str.join(s[i:i+n] for i in range(0, len(s), n))

        # Load the dataset and check if the headers are correct
        df = pd.read_csv(csv_file)
        expected_columns = ['Operation','Total calls','Total duration','Average','Percentage']
        rpd_columns = ['Name','TotalCalls','TotalDuration','Ave','Percentage']

        if list(df.columns) == expected_columns:
            pass
        elif list(df.columns) == rpd_columns:
            df.columns = expected_columns
        else:
            df.columns = expected_columns
        
        # Identify operations
        gemms, nccl, e, r, attn, dm, smax = [], [], [], [], [], [], []
        for c in df.Operation.to_list():
            if "nccl" in c or "rccl" in c:
                nccl.append(c)
            elif c.startswith('Cijk') or "gemm" in c:
                gemms.append(c)
            elif "elementwise" in c:
                e.append(c)
            elif "reduce" in c:
                r.append(c)
            elif "attn" in c or "attention" in c or "Attention" in c or "Flash" in c or "flash" in c:
                attn.append(c)
            elif "Device" in c or "Memcpy" in c or "Host" in c:
                dm.append(c)
            elif "Softmax" in c or "softmax" in c:
                smax.append(c)
        
        # Create a dataframe for GEMMs, NCCL, Elementwise, Reduce, Attention, and Data Management operations
        plot_df = df.copy()
        _gemms = plot_df[plot_df['Operation'].isin(gemms)]
        _gemms['Category'] = 'GEMMs'
        _nccl = plot_df[plot_df['Operation'].isin(nccl)]
        _nccl['Category'] = 'RCCL/NCCL'
        ele = plot_df[plot_df['Operation'].isin(e)]
        ele['Category'] = 'Elementwise'
        red = plot_df[plot_df['Operation'].isin(r)]
        red['Category'] = 'Reduce'
        _attn = plot_df[plot_df['Operation'].isin(attn)]
        _attn['Category'] = 'Attention'
        _dm = plot_df[plot_df['Operation'].isin(dm)]
        _dm['Category'] = 'Data_Management'
        _smax = plot_df[plot_df['Operation'].isin(smax)]
        _smax['Category'] = 'Softmax'
        
        combined_df = pd.concat([_gemms, _nccl, ele, red, _attn, _dm, _smax])
        
        # Handle operations not included in the above categories
        all_operations = gemms + nccl + e + r + attn + dm + smax
        others = plot_df[~plot_df['Operation'].isin(all_operations)]
        others['Category'] = 'Misc'
        combined_df = pd.concat([combined_df, others])
        
        combined_df['Arch'] = architecture
        combined_df = combined_df[combined_df['Percentage'] > 0]
        
        # add breakpoints in long strings 
        combined_df['Operation'] = combined_df['Operation'].apply(insert_string_every_n_chars, n=40)
        
        return combined_df
   
    def process_and_plot(self, csv_file, architecture, output_html, value_metric='Percentage'):
        df = self.process_file(csv_file, architecture)
        
        # Create sunburst plot using the specified value metric
        fig = px.sunburst(df, path=['Arch', 'Category', 'Operation'], 
            values=value_metric,
            color='Category',
            color_discrete_map=self.color_map,  # Use custom color mapping
            title=f'Sunburst Plot for {csv_file} ({architecture})'
        )
        fig.write_html(output_html)

    # Can specify total duration instead of percentage by updating the value_metric arg of process_and_compare method with 'Total Duration'
    def process_and_compare(self, csv_file1, arch1, csv_file2, arch2, output_html, value_metric='Percentage'):
        df1 = self.process_file(csv_file1, arch1)
        df2 = self.process_file(csv_file2, arch2)
        
        # Calculate the sums for the deltas for the value difference pie plot
        df1_summary = df1.groupby('Category')[value_metric].sum().reset_index()
        df2_summary = df2.groupby('Category')[value_metric].sum().reset_index()
        delta_df = pd.merge(df1_summary, df2_summary, on='Category', suffixes=('_1', '_2'))
        delta_df['Delta'] = delta_df[f'{value_metric}_1'] - delta_df[f'{value_metric}_2']
        delta_df['Delta'] = delta_df['Delta'].abs()
        delta_df = delta_df[delta_df['Delta'] >= 1.0] 
        print(delta_df)
        
        fig = make_subplots(rows=1, cols=3, specs=[[{'type': 'domain'}, {'type': 'domain'}, {'type':'domain'}]],
                    subplot_titles=(f'{csv_file1}<br>{arch1}', f'{csv_file2}<br>{arch2}', f'Differences between<br>{csv_file1} and {csv_file2}'))

        # Plot two sunburst charts side by side and then the value difference plot
        fig.add_trace(px.sunburst(df1, path=['Arch', 'Category', 'Operation'], values=value_metric, color='Category', color_discrete_map=self.color_map).data[0], 1, 1)
        fig.add_trace(px.sunburst(df2, path=['Arch', 'Category', 'Operation'], values=value_metric, color='Category', color_discrete_map=self.color_map).data[0], 1, 2)
        fig.add_trace(go.Pie(labels=delta_df['Category'], values=delta_df['Delta'], marker=dict(colors=[self.color_map[k] for k in delta_df['Category']]), name='Delta Pie'), 1, 3)
        
        # Adjust layout and export to html
        fig.update_layout(height=800, width=1600)
        fig.write_html(output_html)
