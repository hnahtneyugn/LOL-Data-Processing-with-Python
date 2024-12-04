#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash import Dash, _dash_renderer
from dash import callback
from dash.dependencies import Input, Output, ClientsideFunction
from dash_iconify import DashIconify

import json
import ast
import numpy as np
import pandas as pd
import scipy
import plotly.express as px
import plotly.figure_factory as ff
import dash_mantine_components as dmc
_dash_renderer._set_react_version("18.2.0")

champion_ban_pick_rate = pd.read_csv('csv/champion_ban_pick_rate.csv', index_col=0)
champion_winrate = pd.read_csv('csv/champion_winrate.csv', index_col=0)
full_champion_data = pd.read_csv('csv/full_champion_data.csv', index_col=0)
champion_role_winrate = pd.read_csv('csv/champion_role_winrate.csv', index_col=0)
champion_role_pickrate = pd.read_csv('csv/champion_role_pickrate.csv', index_col=0)
game_duration = pd.read_csv('csv/game_duration.csv')
game_time_graph = pd.read_csv('csv/game_time_graph.csv', index_col=0)
main_role = pd.read_csv('csv/main_role.csv', index_col=0)
sub_role = pd.read_csv('csv/sub_role.csv', index_col=0)
winrate_objective = pd.read_csv('csv/winrate_objective.csv', index_col=0)
tier_list = pd.read_csv('csv/tier_list_data.csv', index_col=0)

with open("cleandata/tier_list.json", 'r') as file:
    detailed_tier_list = json.load(file)
with open("dragon_data/reversed_item_list.json", 'r') as file:
    reversed_item_list = json.load(file)

winrate_objective_color = ["#4B0082",  "#0000FF", "#008080", "#008000", "#8b0000", "#FFA500", "#FF0000", "#808080", "#000000"]
winrate_role_color = ["#4B0082", "#008080", "#8b0000", "#FF0000", "#000000"]
pickrate_role_color = ["#0000FF", "#008000", "#FFA500", "#808080", "#000000"]
highest_winrate_color = ["#8b0000", "#D08B64", "#536D8A", "#A65E7B", "#84974D"]
highest_pickrate_color = ["#FF0000", "#AC735D", "#6874A0", "#9C5F84", "#808080"]
tier_list_color = ["#1c4b73", "#ffaf85", "#1e9c92", "#8e3164", "#9a9596"]
ultimate_tier_list_color = {"S": "#FF0000", "A": "#D4AF37", "B": "#FF7900", "C": "#90EE90", "D": "#7BB369"}
winrate_role_bin = [2.27, 2.55, 2.32, 0.83, 1.12]

rows = [
    dmc.TableTr(
        [
            dmc.TableTd(tier, style={"width": "100px", "textAlign": "center", "backgroundColor": ultimate_tier_list_color[tier]}),
            dmc.TableTd(
                dmc.Group(
                    children=[
                        dmc.ActionIcon(
                            children=dmc.Image(src=f"/assets/champion_icons/{champion}.png"),
                            id=champion,
                            size="xl",
                            variant="transparent",
                            style={"width": "75px", "height": "75px"}
                        )
                        for champion in champions                     
                    ],
                    gap=0.5,
                ),
                style={"backgroundColor": "#1A1A1A"}
            ),
        ]
    )
    for tier, champions in detailed_tier_list.items()
]

head = dmc.TableThead(
    dmc.TableTr(
        [
            dmc.TableTh("Tier"),
            dmc.TableTh("Champion"),
        ]
    )
)
body = dmc.TableTbody(rows)
caption = dmc.TableCaption("Tier List of Champions")

table = dmc.Table([head, body, caption])


champion_winrate_fig = ff.create_distplot(
    hist_data=[champion_winrate['0']],
    bin_size=1.2,
    group_labels=["Winrate"],
    show_hist=True,
    show_rug=False,
)

champion_winrate_fig.update_layout(
    title = "Distribution of Champion Win Rates",
    title_x=0.5,
    xaxis_title = "Win Rates (%)",
    yaxis_title = "Distribution",
    template="simple_white"
)

champion_banpickrate_fig = ff.create_distplot(
    hist_data=[champion_ban_pick_rate['0']],
    bin_size=2.2,
    group_labels=["Ban/Pick Rate"],
    show_hist=True,
    show_rug=False,
    colors=['red']
)

champion_banpickrate_fig.update_layout(
    title = "Distribution of Champion Ban/Pick Rates",
    title_x=0.5,
    xaxis_title = "Ban/Pick Rates (%)",
    yaxis_title = "Distribution",
    template="simple_white"
)

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=dmc.styles.ALL
)
app.title = "LOL Analysis Project Data Visualization"

server = app.server
app.config.suppress_callback_exceptions = True

app.layout = dmc.MantineProvider(
    forceColorScheme="light",
    children=[
        dmc.Title("League of Legends Data Visualization and Analysis", id='dashboard-title', size="h3", style={"textAlign": "center"}),
        dmc.Blockquote(
            "You must play League of Legends!",
            cite="- Albert Einstein didn't say that!",
            icon=DashIconify(icon="codicon:flame", width=30),
            color="red",
            style={"backgroundColor": "#f8d7da"}
        ),
        dmc.Divider(variant="solid", size="md", style={"marginTop": "10px", "marginBottom": "10px"}),
        dmc.Grid([
            dmc.GridCol([
                dmc.Title("Winrate by Objectives", id="winrate-objective-title", size="h5", style={"fontWeight": "bold", "fontStyle": "italic", "textDecoration": "underline"}),
                dmc.RadioGroup(
                    id='winrate-objective-radio', 
                    value=winrate_objective.columns[4], 
                    size='sm',
                    style={"flexWrap": "wrap", "width": "100%"},
                    children=
                        dmc.Group(
                            children=[dmc.GridCol(dmc.Radio(i, value=i, color=winrate_objective_color[winrate_objective.columns.get_loc(i) % len(winrate_objective_color)]), span="auto") for i in winrate_objective.columns]
                            ), 
                ),
                dash_table.DataTable(
                    id='winrate-objective-table', 
                    data=winrate_objective.reset_index().to_dict('records'), 
                    style_table={'overflowX': 'auto'},
                    style_cell={ 'textAlign': 'center', "padding": "10px"},
                    style_header={'fontWeight': 'bold','textAlign': 'center'}
                )
            ], span=6),
            dmc.GridCol([
                dmc.LineChart(
                    id='winrate-objective-linechart',
                    h=500,
                    data=winrate_objective.reset_index().to_dict('records'),
                    dataKey="index",
                    series=[
                        {"name": objective, 
                         "color": winrate_objective_color[i % len(winrate_objective_color)],
                        } 
                         for i, objective in enumerate(winrate_objective.columns)
                    ],
                    curveType="linear",
                    tickLine="xy",
                    xAxisLabel="Rank",
                    yAxisLabel="Winrate (%)",
                    xAxisProps={"angle": "30", "dy": 15}
                )
            ], span=6, style={"paddingTop": "120px"})
        ]),

        dmc.Divider(variant="solid", size="md", style={"marginTop": "10px", "marginBottom": "10px"}),
        dmc.Title("Distribution of Win Rates and Ban/Pick Rates", id="winrate-title", size="h5", style={"fontWeight": "bold", "fontStyle": "italic", "textDecoration": "underline"}),
        dmc.Grid([
            dmc.GridCol([
                dcc.Graph(figure=champion_winrate_fig, id="winrate-fig")
            ], span=6),
            dmc.GridCol([
                dcc.Graph(figure=champion_banpickrate_fig, id="banpickrate-fig")
            ], span=6),
        ]),

        dmc.Divider(variant="solid", size="md", style={"marginTop": "10px", "marginBottom": "10px"}),
        dmc.Grid([
            dmc.GridCol([
                dmc.Title("Distribution of Win Rates at Each Lane", id="roles-winrate-title", size="h5", style={"fontWeight": "bold", "fontStyle": "italic", "textDecoration": "underline"}), 
                dmc.RadioGroup(
                    id="roles-winrate-radio",
                    value = champion_role_winrate.columns[0],
                    size = "sm",
                    style={"flexWrap": "wrap", "width": "100%"},
                    children=
                        dmc.Group(
                            children=[dmc.GridCol(dmc.Radio(i, value=i, color=winrate_role_color[champion_role_winrate.columns.get_loc(i) % len(winrate_role_color)]), span="auto") for i in champion_role_winrate.columns]
                        ), 
                ),
                dash_table.DataTable(
                    id='role-winrate-table', 
                    data=champion_role_winrate.round(4).reset_index().to_dict('records'), 
                    page_size = 12,
                    style_table={'overflowX': 'auto'},
                    style_cell={ 'textAlign': 'center', "padding": "10px"},
                    style_header={'fontWeight': 'bold','textAlign': 'center'}
                ), 
            ], span=6),
            dmc.GridCol([
                dcc.Graph(figure={}, id='role-winrate-fig', style={'height': '700px'})
            ], span=6)
        ]),

        dmc.Divider(variant="solid", size="md", style={"marginTop": "10px", "marginBottom": "10px"}),
        dmc.Grid([
            dmc.GridCol([
                dcc.Graph(figure={}, id='role-pickrate-fig', style={'height': '700px'})
            ], span=6),
            dmc.GridCol([
                dmc.Title("Distribution of Pick Rates at Each Lane", id="roles-pickrate-title", size="h5", style={"fontWeight": "bold", "fontStyle": "italic", "textDecoration": "underline"}), 
                dmc.RadioGroup(
                    id="roles-pickrate-radio",
                    value = champion_role_pickrate.columns[4],
                    size = "sm",
                    style={"flexWrap": "wrap", "width": "100%"},
                    children=
                        dmc.Group(
                            children=[dmc.GridCol(dmc.Radio(i, value=i, color=pickrate_role_color[champion_role_pickrate.columns.get_loc(i) % len(pickrate_role_color)]), span="auto") for i in champion_role_pickrate.columns]
                        ), 
                ),
                dash_table.DataTable(
                    id='role-pickrate-table', 
                    data=champion_role_pickrate.round(4).reset_index().to_dict('records'), 
                    page_size = 12,
                    style_table={'overflowX': 'auto'},
                    style_cell={ 'textAlign': 'center', "padding": "10px"},
                    style_header={'fontWeight': 'bold','textAlign': 'center'}
                ), 
            ], span=6)
        ]),

        dmc.Divider(variant="solid", size="md", style={"marginTop": "10px", "marginBottom": "10px"}),
        dmc.Grid([
            dmc.GridCol([
                dmc.Title("Highest Winrate Champions", id="highest-winrate-title", size="h5", style={"fontWeight": "bold", "fontStyle": "italic", "textDecoration": "underline"}),
                dmc.RadioGroup(
                    id="highest-winrate-radio",
                    value = champion_role_winrate.columns[1],
                    size = "sm",
                    style={"flexWrap": "wrap", "width": "100%"},
                    children=
                        dmc.Group(
                            children=[dmc.GridCol(dmc.Radio(i, value=i, color=highest_winrate_color[champion_role_winrate.columns.get_loc(i) % len(highest_winrate_color)]), span="auto") for i in champion_role_winrate.columns]
                        ), 
                ),
                dash_table.DataTable(
                    id= "highest-winrate-table",
                    data= champion_role_winrate.round(4).reset_index().to_dict('records'),
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                    style_cell={ 'textAlign': 'center', "padding": "10px"},
                    style_header={'fontWeight': 'bold','textAlign': 'center'}
                ),
            ], span=2),

            dmc.GridCol([
                dcc.Graph(figure={}, id="highest-winrate-barchart", style={'height': '700px'})
            ], span = 10)
        ]),

        dmc.Divider(variant="solid", size="md", style={"marginTop": "10px", "marginBottom": "10px"}),
        dmc.Grid([
            dmc.GridCol([
                dmc.Title("Highest Pickrate Champions", id="highest-pickrate-title", size="h5", style={"fontWeight": "bold", "fontStyle": "italic", "textDecoration": "underline"}),
                dmc.RadioGroup(
                    id="highest-pickrate-radio",
                    value = champion_role_pickrate.columns[4],
                    size = "sm",
                    style={"flexWrap": "wrap", "width": "100%"},
                    children=
                        dmc.Group(
                            children=[dmc.GridCol(dmc.Radio(i, value=i, color=highest_pickrate_color[champion_role_pickrate.columns.get_loc(i) % len(highest_pickrate_color)]), span="auto") for i in champion_role_pickrate.columns]
                        ), 
                ),
                dash_table.DataTable(
                    id= "highest-pickrate-table",
                    data= champion_role_pickrate.round(4).reset_index().to_dict('records'),
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                    style_cell={ 'textAlign': 'center', "padding": "10px"},
                    style_header={'fontWeight': 'bold','textAlign': 'center'}
                ),
            ], span=2),

            dmc.GridCol([
                dcc.Graph(figure={}, id="highest-pickrate-barchart", style={'height': '700px'})
            ], span = 10)
        ]),

        dmc.Divider(variant="solid", size="md", style={"marginTop": "10px", "marginBottom": "10px"}),
        dmc.Grid([
            dmc.GridCol([
                dmc.Title("Number of Matches by Duration", id="game-duration-title", size="h5", style={"fontWeight": "bold", "fontStyle": "italic", "textDecoration": "underline"}),
                dcc.Graph(figure=px.bar(game_duration, x="Duration", y="NumberOfMatches", color_discrete_sequence=['#9D2C00'], template="simple_white").update_layout(xaxis = dict(tickmode="linear", dtick=1)), id="game-duration-barchart", style={'height': '700px'})
            ], span=12)
        ]),

        dmc.Divider(variant="solid", size="md", style={"marginTop": "10px", "marginBottom": "10px"}),
        dmc.Grid([
            dmc.GridCol([
                dmc.Title("Number of Matches by Hour in the day", id="game-time-title", size="h5", style={"fontWeight": "bold", "fontStyle": "italic", "textDecoration": "underline"}),
                dcc.Graph(figure=px.bar(game_time_graph, x=game_time_graph.index, y="NumberOfMatches", color_discrete_sequence=['#F9E858'], template="simple_white").update_layout(xaxis = dict(tickmode="linear", dtick=1)), id="game-time-barchart", style={'height': '700px'})
            ], span=12)
        ]),

        dmc.Divider(variant="solid", size="md", style={"marginTop": "10px", "marginBottom": "10px"}),
        dmc.Grid([
            dmc.GridCol([
                dmc.Title("Tier List Percentage", id="tier-list-percentage-title", size="h5", style={"fontWeight": "bold", "fontStyle": "italic", "textDecoration": "underline"}),
                dcc.Graph(figure=px.pie(tier_list, names=tier_list.index, values=tier_list["Number of Champions"], color_discrete_sequence=tier_list_color ,title="Tier List Distribution").update_layout(legend=dict(font = dict(size = 16))), id="tier-list-chart", style={'height': '700px'})
            ])
        ]),
        
        dmc.Divider(variant="solid", size="md", style={"marginTop": "10px", "marginBottom": "10px"}),
        dmc.Title("Main Role and Sub Role Popularity", id="main-sub-role-title", size="h5", style={"fontWeight": "bold", "fontStyle": "italic", "textDecoration": "underline"}),
        dmc.Grid([
            dmc.GridCol([
                dcc.Graph(figure=px.line_polar(main_role.reset_index(), theta=main_role.reset_index()["index"], r=main_role["Chosen"], line_close=True).update_traces(fill="toself").update_layout(polar=dict(radialaxis=dict(range=[900, 1300]))))
            ], span=6),

            dmc.GridCol([
                dcc.Graph(figure=px.line_polar(sub_role.reset_index(), theta=sub_role.reset_index()["index"], r=sub_role["Chosen"], line_close=True).update_traces(fill = "toself", fillcolor = "rgba(255, 0, 0, 0.3)").update_layout(polar=dict(radialaxis=dict(range=[800, 1800]))))
            ], span=6),
        ]),

        dmc.Divider(variant="solid", size="md", style={"marginTop": "10px", "marginBottom": "10px"}),
        dmc.Grid([
            dmc.GridCol([
                dmc.Title("The Ultimate Tier List", id="ultimate-tier-list-title", size="h5", style={"fontWeight": "bold", "fontStyle": "italic", "textDecoration": "underline"}),
                dmc.Table(
                    [head, body, caption],
                    id="ultimate-tier-list-table",
                    highlightOnHover=True,
                    withRowBorders=True,
                    withColumnBorders=True,
                    borderColor="black"
                )
            ], span=6),
            dmc.GridCol([
                html.Div(id="clicked-icon-id", style={"fontSize": "20px", "fontWeight": "bold"}),
                html.Audio(id="audio-player-1", controls=False, autoPlay=True, style={"display": "none"}),
                html.Audio(id="audio-player-2", controls=False, autoPlay=True, style={"display": "none"}),
            ], id="ultimate-tier-list-detail", span=6)
        ])
    ]
)

@app.callback(
    [Output("clicked-icon-id", "children"), Output("audio-player-1", "src"), Output("audio-player-2", "src")],
    [Input(champion, "n_clicks") for champion in full_champion_data.index],
)
def display_clicked_icon(*n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "No champion chosen yet!", None, None
    else:
        clicked_id = ctx.triggered[0]["prop_id"].split(".")[0]
        champion_info = full_champion_data.reset_index()[full_champion_data.reset_index()["index"] == clicked_id].iloc[0]
        core_items = ast.literal_eval(champion_info["core_items"])
        main_roles = ast.literal_eval(champion_info["main_roles"])
        winrate = champion_info["winrate"]
        banpickrate = champion_info["ban_pick_rate"]

        item_images = []
        for item in core_items:
            item_id = reversed_item_list.get(item) 
            if item_id:
                item_images.append(dmc.Image(src=f"/assets/item_icons/{item_id}.png"))
                
        role_images = []
        for role in main_roles:
            role_images.append(dmc.Image(src=f"/assets/lane_icons/{role}.png", style={"width": "75px", "height": "75px"}))
                               
        children = dmc.Stack([
            dmc.Text(clicked_id, fw=700, td="underline", size="xl"),
            dmc.Group([
                dmc.Stack([dmc.Text("Core Items:", fw=700), dmc.Group(children=item_images, align="center")]),
                dmc.Stack([dmc.Text("Main Roles:", fw=700), dmc.Group(children=role_images)]),
                dmc.Stack([dmc.Text("Win Rate:", fw=700), dmc.Text(f"{winrate}%")]),
                dmc.Stack([dmc.Text("Ban/Pick Rate:", fw=700), dmc.Text(f"{banpickrate}%")]),
                dmc.Stack([
                    dmc.Text("Visit link for more:", fw=700),
                    dmc.Anchor(f"{clicked_id} Wiki", href=f"https://leagueoflegends.fandom.com/wiki/{clicked_id}/LoL", style={"color": "red"})
                ]),
            ], gap="xl"),
            dmc.Image(src=f"assets/champion_images/{clicked_id}_0.jpg")
        ])

        audio_src_1 = f"/assets/audio/{clicked_id}_Select_SFX.ogg"
        audio_src_2 = f"/assets/audio/{clicked_id}_Select.ogg"

        return children, audio_src_1, audio_src_2

@app.callback(
    Output("winrate-objective-linechart", "series"),
    Input("winrate-objective-radio", "value"),
)
def update_linechart(objective):
    return [{"name": objective, "color": winrate_objective_color[winrate_objective.columns.get_loc(objective) % len(winrate_objective_color)]}]

@app.callback(
    Output("role-winrate-fig", "figure"),
    Input("roles-winrate-radio", "value"),
)
def update_winrate_graph(col_chosen):
    fig1 = ff.create_distplot(
        hist_data=[(champion_role_winrate[col_chosen]*100).dropna().to_list()],
        bin_size=winrate_role_bin[champion_role_winrate.columns.get_loc(col_chosen)],
        group_labels=["Winrate in " + col_chosen + " Role"],
        show_hist=True,
        show_rug=False,
        colors=[winrate_role_color[champion_role_winrate.columns.get_loc(col_chosen) % len(winrate_role_color)]]
    )
    
    fig1.update_layout(
        title = "Distribution of Champion Win Rates in Each Lane",
        title_x=0.5,
        xaxis_title = "Win Rates (%)",
        yaxis_title = "Distribution",
        template="simple_white"
    )

    return fig1

@app.callback(
    Output("role-pickrate-fig", "figure"),
    Input("roles-pickrate-radio", "value"),
)
def update_pickrate_graph(col_chosen):
    fig2 = ff.create_distplot(
        hist_data=[(champion_role_pickrate[col_chosen]*100).dropna().to_list()],
        bin_size = 1,
        group_labels=["Pickrate in " + col_chosen + " Role"],
        show_hist=True,
        show_rug=False,
        colors=[pickrate_role_color[champion_role_pickrate.columns.get_loc(col_chosen) % len(pickrate_role_color)]]
    )
    
    fig2.update_layout(
        title = "Distribution of Champion Pick Rates in Each Lane",
        title_x=0.5,
        xaxis_title = "Pick Rates (%)",
        yaxis_title = "Distribution",
        template="simple_white"
    )

    return fig2

@app.callback(
    Output("highest-winrate-table", "data"),
    Input("highest-winrate-radio", "value")
)
def update_highest_winrate_table(col_chosen):
    return champion_role_winrate.round(4).reset_index()[["index", col_chosen]].nlargest(20, col_chosen).to_dict('records')

@app.callback(
    Output("highest-pickrate-table", "data"),
    Input("highest-pickrate-radio", "value")
)
def update_highest_pickrate_table(col_chosen):
    return champion_role_pickrate.round(4).reset_index()[["index", col_chosen]].nlargest(20, col_chosen).to_dict('records')

@app.callback(
    Output("highest-winrate-barchart", "figure"),
    Input("highest-winrate-radio", "value")
)
def update_highest_winrate_barchart(col_chosen):
    fig3 = px.bar((champion_role_winrate[col_chosen].round(4) * 100).reset_index().nlargest(20, col_chosen), x="index", y=col_chosen, color_discrete_sequence=[highest_winrate_color[champion_role_winrate.columns.get_loc(col_chosen) % len(highest_winrate_color)]])

    fig3.update_layout(
        title = "Champions with Highest Winrate in " + col_chosen,
        title_x=0.5,
        xaxis_title = "Champion Name",
        yaxis_title  = "Win Rates (%)",
        template = "simple_white"
    )

    return fig3

@app.callback(
    Output("highest-pickrate-barchart", "figure"),
    Input("highest-pickrate-radio", "value")
)
def update_highest_pickrate_barchart(col_chosen):
    fig4 = px.bar((champion_role_pickrate[col_chosen].round(4) * 100).reset_index().nlargest(20, col_chosen), x="index", y=col_chosen, color_discrete_sequence=[highest_pickrate_color[champion_role_pickrate.columns.get_loc(col_chosen) % len(highest_pickrate_color)]])

    fig4.update_layout(
        title = "Champions with Highest Pickrate in " + col_chosen,
        title_x=0.5,
        xaxis_title = "Champion Name",
        yaxis_title  = "Pick Rates (%)",
        template = "simple_white"
    )

    return fig4


if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host="127.0.0.1")

