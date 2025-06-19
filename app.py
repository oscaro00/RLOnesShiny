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
        ui.h1('Explore RLCS 1v1 Statistics'),
        ui.tags.ol(
            ui.tags.li('Find games that match specific criteria'),
            ui.tags.li('Dive into player statistics'),
            ui.tags.li('Compare players head to head'),
            ui.tags.li('Check player camera settings')
        ),
        ui.p('All data comes from ', ui.a('Ballchasing', href='https://ballchasing.com/group/1v1-events-spqzm3tx17', target='_blank')),
        ui.h3('All data comes from '),
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
        ui.h1('Player Settings'),
        ui.output_ui('player_selectize'),
        ui.h3('Camera Settings'),
        ui.output_ui('latest_10_camera_settings'),
        ui.h3('Car Selection')
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

    ## Common helpers
    @render.ui
    def player_selectize():
        lst_players = (
            df_players
            .select('name')
            .sort('name')
            .get_column('name')
            .to_list()
        )
        dict_players = {name : name for name in lst_players}

        return ui.input_selectize(
            'player_select',
            'Select a player:',
            dict_players,
            selected = 'ApparentlyJack'
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

    ## Player settings
    @render.ui
    def latest_10_camera_settings():
        df_latest_camera = (
            df_player_settings
            .join(df_players, left_on='player_id', right_on='id', how='inner')
            .filter(pl.col('name') == input.player_select())
            .sort(by='date', descending=True)
            .select('fov', 'height', 'pitch', 'distance', 'stiffness', 'swivel_speed', 'transition_speed', 'steering_sensitivity')
            .unique()
            .limit(10)
        )

        return (
            gt.GT(df_latest_camera)
            .tab_header(title='10 most recent distinct camera settings', subtitle='Sorted by most recent games')
            .tab_source_note(source_note='Less than 10 rows indicates less than 10 distinct camera settings in the data')
        )


app = App(app_ui, server)
