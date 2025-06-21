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
    
    @render.data_frame
    def all_cars_used():
        df_cars = (
            df_player_settings
            .join(df_games, on='id', how='inner')
            .join(df_players, left_on='player_id', right_on='id', how='inner')
            .filter(pl.col('name') == input.player_select())
            .sort('date')
            .select('group_id', pl.col('id').alias('game id'), 'car_name')
        )

        return render.DataGrid(df_cars.rename({col: col.replace('_', ' ') for col in df_cars.columns}), width='90%')

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
            showcase=camera_svg,
            height='150px'
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
            showcase=wrench_svg,
            height='150px'
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
            showcase=calendar_svg,
            height='150px'
        )

    @render.ui
    def vb_count_unique_cars():
        car_svg = ui.HTML('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="100%" fill="currentColor" class="bi bi-car-front" viewBox="0 0 16 16"><path d="M4 9a1 1 0 1 1-2 0 1 1 0 0 1 2 0m10 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0M6 8a1 1 0 0 0 0 2h4a1 1 0 1 0 0-2zM4.862 4.276 3.906 6.19a.51.51 0 0 0 .497.731c.91-.073 2.35-.17 3.597-.17s2.688.097 3.597.17a.51.51 0 0 0 .497-.731l-.956-1.913A.5.5 0 0 0 10.691 4H5.309a.5.5 0 0 0-.447.276"/><path d="M2.52 3.515A2.5 2.5 0 0 1 4.82 2h6.362c1 0 1.904.596 2.298 1.515l.792 1.848c.075.175.21.319.38.404.5.25.855.715.965 1.262l.335 1.679q.05.242.049.49v.413c0 .814-.39 1.543-1 1.997V13.5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5v-1.338c-1.292.048-2.745.088-4 .088s-2.708-.04-4-.088V13.5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5v-1.892c-.61-.454-1-1.183-1-1.997v-.413a2.5 2.5 0 0 1 .049-.49l.335-1.68c.11-.546.465-1.012.964-1.261a.8.8 0 0 0 .381-.404l.792-1.848ZM4.82 3a1.5 1.5 0 0 0-1.379.91l-.792 1.847a1.8 1.8 0 0 1-.853.904.8.8 0 0 0-.43.564L1.03 8.904a1.5 1.5 0 0 0-.03.294v.413c0 .796.62 1.448 1.408 1.484 1.555.07 3.786.155 5.592.155s4.037-.084 5.592-.155A1.48 1.48 0 0 0 15 9.611v-.413q0-.148-.03-.294l-.335-1.68a.8.8 0 0 0-.43-.563 1.8 1.8 0 0 1-.853-.904l-.792-1.848A1.5 1.5 0 0 0 11.18 3z"/></svg>')
        
        df_total_cars = (
            df_player_settings
            .join(df_players, left_on='player_id', right_on='id', how='inner')
            .filter(pl.col('name') == input.player_select())
            .select('car_name')
            .unique()
            .select(pl.len())
        )

        # https://shiny.posit.co/py/components/outputs/value-box/
        return ui.value_box(
            'Number of distinct cars',
            f'{df_total_cars.item()}',
            showcase=car_svg,
            height='150px'
        )

    @render.ui
    def vb_pct_series_car_chg():
        gas_svg = ui.HTML('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="100%" fill="currentColor" class="bi bi-fuel-pump" viewBox="0 0 16 16"><path d="M3 2.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 .5.5v5a.5.5 0 0 1-.5.5h-5a.5.5 0 0 1-.5-.5z"/><path d="M1 2a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v8a2 2 0 0 1 2 2v.5a.5.5 0 0 0 1 0V8h-.5a.5.5 0 0 1-.5-.5V4.375a.5.5 0 0 1 .5-.5h1.495c-.011-.476-.053-.894-.201-1.222a.97.97 0 0 0-.394-.458c-.184-.11-.464-.195-.9-.195a.5.5 0 0 1 0-1q.846-.002 1.412.336c.383.228.634.551.794.907.295.655.294 1.465.294 2.081v3.175a.5.5 0 0 1-.5.501H15v4.5a1.5 1.5 0 0 1-3 0V12a1 1 0 0 0-1-1v4h.5a.5.5 0 0 1 0 1H.5a.5.5 0 0 1 0-1H1zm9 0a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v13h8z"/></svg>')
        
        df_pct_camera_chg = (
            df_player_settings
            .join(df_games, on='id', how='inner')
            .join(df_players, left_on='player_id', right_on='id', how='inner')
            .filter(pl.col('name') == input.player_select())
            .select('group_id', 'car_name')
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
            'Percent of series with a car change',
            f'{df_pct_camera_chg.item() * 100}%',
            showcase=gas_svg,
            height='150px'
        )
    
    @render.ui
    def vb_most_used_car():
        arrow_svg = ui.HTML('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="100%" fill="currentColor" class="bi bi-arrow-counterclockwise" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 3a5 5 0 1 1-4.546 2.914.5.5 0 0 0-.908-.417A6 6 0 1 0 8 2z"/><path d="M8 4.466V.534a.25.25 0 0 0-.41-.192L5.23 2.308a.25.25 0 0 0 0 .384l2.36 1.966A.25.25 0 0 0 8 4.466"/></svg>')
        
        df_reliable_car = (
            df_player_settings
            .join(df_players, left_on='player_id', right_on='id', how='inner')
            .filter(pl.col('name') == input.player_select())
            .group_by('car_name')
            .agg(
                pl.col('car_name').count().alias('cnt_car')
            )
            .sort('cnt_car', descending=True)
            .select('car_name')
            .limit(1)
        )

        # https://shiny.posit.co/py/components/outputs/value-box/
        return ui.value_box(
            'Most used car',
            f'{df_reliable_car.item()}',
            showcase=arrow_svg,
            height='150px'
        )

app = App(app_ui, server)
