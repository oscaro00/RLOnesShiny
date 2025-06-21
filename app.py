from shiny import App, reactive, render, ui
from shinywidgets import render_altair, output_widget
import shinyswatch
import polars as pl
import polars.selectors as cs
import great_tables as gt
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
    sidebar = ui.sidebar('this is sidebar content', id = 'sidebar'),
    theme = shinyswatch.theme.superhero
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
    @render.data_frame
    def latest_10_camera_settings():
        df_latest_camera = (
            df_player_settings
            .join(df_players, left_on='player_id', right_on='id', how='inner')
            .filter(pl.col('name') == input.player_select())
            .sort(by='date', descending=True)
            .select('fov', 'height', 'pitch', 'distance', 'stiffness', 'swivel_speed', 'transition_speed', 'steering_sensitivity')
            .with_columns(cs.float().round(2))
            .unique()
            .limit(10)
            
        )

        return render.DataGrid(df_latest_camera.rename({col: col.replace('_', ' ') for col in df_latest_camera.columns}))

    @render.data_frame
    def all_camera_settings():
        df_camera = (
            df_player_settings
            .join(df_players, left_on='player_id', right_on='id', how='inner')
            .filter(pl.col('name') == input.player_select())
            .sort(by='date', descending=True)
            .select(pl.col('id').alias('game id'), 'fov', 'height', 'pitch', 'distance', 'stiffness', 'swivel_speed', 'transition_speed', 'steering_sensitivity')
        )

        return render.DataGrid(df_camera.rename({col: col.replace('_', ' ') for col in df_camera.columns}))

    @render.ui
    def vb_count_unique_camera_settings():
        camera_svg = ui.HTML('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="100%" fill="currentColor" class="bi bi-camera" viewBox="0 0 16 16"><path d="M15 12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h1.172a3 3 0 0 0 2.12-.879l.83-.828A1 1 0 0 1 6.827 3h2.344a1 1 0 0 1 .707.293l.828.828A3 3 0 0 0 12.828 5H14a1 1 0 0 1 1 1zM2 4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-1.172a2 2 0 0 1-1.414-.586l-.828-.828A2 2 0 0 0 9.172 2H6.828a2 2 0 0 0-1.414.586l-.828.828A2 2 0 0 1 3.172 4z"/><path d="M8 11a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5m0 1a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7M3 6.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0"/></svg>')
        
        df_total_camera = (
            df_player_settings
            .join(df_players, left_on='player_id', right_on='id', how='inner')
            .filter(pl.col('name') == input.player_select())
            .sort(by='date', descending=True)
            .select('fov', 'height', 'pitch', 'distance', 'stiffness', 'swivel_speed', 'transition_speed', 'steering_sensitivity')
            .unique()
            .select(pl.len())
        )

        # https://shiny.posit.co/py/components/outputs/value-box/
        return ui.value_box(
            'Number of distinct camera settings',
            f'{df_total_camera.item()}',
            showcase=camera_svg
        )

    @render.ui
    def vb_pct_series_camera_chg():
        wrench_svg = ui.HTML('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="100%" fill="currentColor" class="bi bi-wrench-adjustable" viewBox="0 0 16 16"><path d="M16 4.5a4.5 4.5 0 0 1-1.703 3.526L13 5l2.959-1.11q.04.3.041.61"/><path d="M11.5 9c.653 0 1.273-.139 1.833-.39L12 5.5 11 3l3.826-1.53A4.5 4.5 0 0 0 7.29 6.092l-6.116 5.096a2.583 2.583 0 1 0 3.638 3.638L9.908 8.71A4.5 4.5 0 0 0 11.5 9m-1.292-4.361-.596.893.809-.27a.25.25 0 0 1 .287.377l-.596.893.809-.27.158.475-1.5.5a.25.25 0 0 1-.287-.376l.596-.893-.809.27a.25.25 0 0 1-.287-.377l.596-.893-.809.27-.158-.475 1.5-.5a.25.25 0 0 1 .287.376M3 14a1 1 0 1 1 0-2 1 1 0 0 1 0 2"/></svg>')
        
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
            f'{df_pct_camera_chg.item() * 100}%',
            showcase=wrench_svg
        )
    
    @render.ui
    def vb_latest_settings_data():
        calendar_svg = ui.HTML('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="100%" fill="currentColor" class="bi bi-calendar" viewBox="0 0 16 16"><path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5M1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4z"/></svg>')
        
        df_latest_date = (
            df_player_settings
            .join(df_players, left_on='player_id', right_on='id', how='inner')
            .filter(pl.col('name') == input.player_select())
            .select(pl.col('date'))
            .max()
        )

        # https://shiny.posit.co/py/components/outputs/value-box/
        return ui.value_box(
            'Date of latest data',
            f'{str(df_latest_date.item()).split(' ')[0]}',
            showcase=calendar_svg
        )


app = App(app_ui, server)
