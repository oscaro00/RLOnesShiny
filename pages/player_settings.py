from shiny import App, reactive, render, ui
from shinywidgets import render_altair, output_widget

player_settings_page = ui.nav_panel(
    'Player Settings',
    ui.h1('Player Settings'),
    ui.output_ui('player_selectize'),
    ui.h3('Camera Settings'),
    ui.output_ui('vb_pct_series_camera_chg'),
    ui.output_ui('latest_10_camera_settings'),
    ui.output_ui('all_camera_settings'),
    ui.h3('Car Selection')
)

# win rate after a camera change