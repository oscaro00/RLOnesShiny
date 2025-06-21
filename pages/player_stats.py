from shiny import App, reactive, render, ui
from shinywidgets import render_altair, output_widget

player_stats_page = ui.nav_panel(
    'Player Stats',
    'Player stats page context'
)