import pandas as pd
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px

# Load data
file_path = r"C:\Users\Abdul Basit\Desktop\Stuff\Survey Report 1.xlsx"
xls = pd.ExcelFile(file_path)
data = pd.read_excel(xls, sheet_name="Worksheet")

# Extract necessary columns
contacts = data[['Mobile', 'Name']].dropna().drop_duplicates()

dashboard = dash.Dash(__name__)

dashboard.layout = html.Div([
    html.H1("Family Members Dashboard"),
    dcc.Dropdown(
        id='contact-dropdown',
        options=[{'label': str(mob), 'value': mob} for mob in contacts['Mobile'].unique()],
        placeholder="Select a Contact"
    ),
    html.H3("Family Members"),
    html.Ul(id='family-list'),
    html.H3("Family Member Details"),
    dash_table.DataTable(
    id='family-details',
    columns=[{"name": col, "id": col} for col in data.columns],
    style_table={'width': '100%', 'overflowX': 'auto'},
    style_data={'whiteSpace': 'normal'},
    fixed_columns={'headers': True, 'data': 1}
),
    
    html.H3("Verification Summary"),
    dash_table.DataTable(
    id='verification-summary',
    style_table={'width': '100%', 'overflowX': 'auto'},
    style_data={'whiteSpace': 'normal'},
    fixed_columns={'headers': True, 'data': 1}
),

    
    html.H3("Data Analysis"),
    dcc.Dropdown(
        id='analysis-dropdown',
        options=[
            {'label': 'Gender Distribution', 'value': 'gender'},
            {'label': 'Age Distribution', 'value': 'age'},
            {'label': 'Livestock Ownership', 'value': 'livestock'},
            {'label': 'Land Ownership', 'value': 'land'}
        ],
        placeholder="Select Analysis Type"
    ),
    dcc.Graph(id='analysis-graph'),
    
    html.H3("Verification Analysis"),
    dcc.Dropdown(
        id='verification-dropdown',
        options=[{'label': col, 'value': col} for col in data.columns if 'Status' in col],
        placeholder="Select a Column to Analyze Verification"
    ),
    dcc.Graph(id='verification-graph'),
    html.Div(id='verification-counts')
])

@dashboard.callback(
    Output('family-list', 'children'),
    Input('contact-dropdown', 'value')
)
def update_family_list(selected_contact):
    if selected_contact is None:
        return []
    members = data[data['Mobile'] == selected_contact]['Name'].dropna().unique()
    return [html.Li(member) for member in members]

@dashboard.callback(
    Output('family-details', 'data'),
    Input('contact-dropdown', 'value')
)
def show_family_details(selected_contact):
    if selected_contact is None:
        return []
    details = data[data['Mobile'] == selected_contact]
    return details.to_dict('records')

@dashboard.callback(
    Output('verification-summary', 'data'),
    Input('contact-dropdown', 'value')
)
def update_verification_summary(selected_contact):
    if selected_contact is None:
        return []
    
    member_data = data[data['Mobile'] == selected_contact]
    status_columns = [col for col in data.columns if 'Status' in col]
    
    summary = []
    for name in member_data['Name'].unique():
        member_rows = member_data[member_data['Name'] == name]
        verified_count = (member_rows[status_columns] == 'Verified').sum().sum()
        unverified_count = (member_rows[status_columns] == 'Unverified').sum().sum()
        summary.append({
            'Name': name,
            'Verified': verified_count,
            'Unverified': unverified_count
        })
    
    return summary

@dashboard.callback(
    Output('analysis-graph', 'figure'),
    Input('analysis-dropdown', 'value')
)
def update_analysis_graph(selected_analysis):
    if selected_analysis == 'gender':
        fig = px.histogram(data, x='Gender', title='Gender Distribution')
    elif selected_analysis == 'age':
        fig = px.histogram(data, x='DOB', title='Age Distribution')
    elif selected_analysis == 'livestock':
        fig = px.bar(data, x='Name', y='Total Cows', title='Livestock Ownership')
    elif selected_analysis == 'land':
        fig = px.pie(data, names='Does the family own any agricultural land presently?', title='Land Ownership')
    else:
        fig = px.scatter(title="Select an analysis option")
    return fig

@dashboard.callback(
    [Output('verification-graph', 'figure'),
     Output('verification-counts', 'children')],
    Input('verification-dropdown', 'value')
)
def update_verification_graph(selected_column):
    if not selected_column:
        return px.scatter(title="Select a column to analyze verification"), ""
    
    verified_counts = data[selected_column].value_counts().reset_index()
    verified_counts.columns = ['Status', 'Count']
    fig = px.bar(verified_counts, x='Status', y='Count', title=f'Verification Status in {selected_column}')

    counts_text = "<br>".join([f"{row['Status']}: {row['Count']}" for _, row in verified_counts.iterrows()])
    return fig, html.Div([html.H4("Verification Counts"), html.P(counts_text)])

dashboard.run_server(debug=True, port=8060)
