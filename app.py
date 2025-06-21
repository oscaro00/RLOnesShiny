from shiny import App, reactive, render, ui
import polars as pl
import great_tables as gt
from shinywidgets import render_altair, output_widget
import altair as alt

from helpers.load_data import load_r2_parquet

from pages.home import home_page
from pages.game_finder import game_finder_page
from pages.player_stats import player_stats_page
from pages.comparison_tool import comparison_tool_page
from pages.player_settings import player_settings_page

# Add page title and sidebar
app_ui = ui.page_navbar(
    # put the style sheet on pages to avoid removing the header and sidebar formatting
    #ui.tags.link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'),
    
    home_page,
    game_finder_page,
    player_stats_page,
    comparison_tool_page,
    player_settings_page,
    
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

    @render.ui
    def all_camera_settings():
        df_camera = (
            df_player_settings
            .join(df_players, left_on='player_id', right_on='id', how='inner')
            .filter(pl.col('name') == input.player_select())
            .sort(by='date', descending=True)
            .select(pl.col('id').alias('game id'), 'fov', 'height', 'pitch', 'distance', 'stiffness', 'swivel_speed', 'transition_speed', 'steering_sensitivity')
        )

        return (
            gt.GT(df_camera)
            .tab_header(title='All camera settings', subtitle='Sorted by most recent games')
        )

    @render.ui
    def vb_pct_series_camera_chg():
        df_pct_camera_chg = (
            df_player_settings
            .join(df_games, on='id', how='inner')
            .join(df_players, left_on='player_id', right_on='id', how='inner')
            .filter(pl.col('name') == input.player_select())
            .select('group_id', 'fov', 'height', 'pitch', 'distance', 'stiffness', 'swivel_speed', 'transition_speed', 'steering_sensitivity')
            .group_by('group_id')
            .agg(
                pl.struct(pl.all().exclude('group_id')).n_unique().alias('distinct_combinations')
            )
            .with_columns(
                pl.when(pl.col('distinct_combinations') > 1).then(1).otherwise(0).alias('mid_series_switch_flag')
            )
            .select('mid_series_switch_flag')
            .mean()
        )

        # https://shiny.posit.co/py/components/outputs/value-box/
        return ui.value_box(
            'Percent of series with a camera setting change',
            df_pct_camera_chg.item()
        )


app = App(app_ui, server)
