from shiny import App, reactive, render, ui
import polars as pl
import great_tables as gt
from shinywidgets import render_altair, output_widget
import altair as alt

from helpers.load_data import load_r2_parquet


# Add page title and sidebar
app_ui = ui.page_navbar(
    ui.nav_panel(
        'Home',
        'Home page content',
        output_widget('plot_map_count'),
        ui.output_ui('table_map_count')
    ),
    ui.nav_panel(
        'Game Finder',
        'Game finder page context'
    ),
    ui.nav_panel(
        'Player Stats',
        'Player stats page context'
    ),
    ui.nav_panel(
        'Comparison Tool',
        'Comparison tool page context'
    ),
    ui.nav_panel(
        'Player Settings',
        'Player settings page context'
    ),
    
    title = 'RL Ones',
    id = 'rl_ones_navbar',
    sidebar = ui.sidebar('this is sidebar content', id = 'sidebar')
)


def server(input, output, session):
    df_games = load_r2_parquet('games.parquet')
    df_groups = load_r2_parquet('groups.parquet')
    df_player_settings = load_r2_parquet('player_settings.parquet')
    df_player_stats = load_r2_parquet('player_stats.parquet')
    df_players = load_r2_parquet('players.parquet')

    df_map_count = (
        df_games
        .group_by('map_name')
        .len()
    )

    @render_altair
    def plot_map_count():
        return alt.Chart(df_map_count).mark_bar().encode(
            x='map_name',
            y='len'
        )

    @render.ui
    def table_map_count():
        return gt.GT(df_map_count)


app = App(app_ui, server)
