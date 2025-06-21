from shiny import App, reactive, render, ui
from shinywidgets import render_altair, output_widget

game_finder_page = ui.nav_panel(
    'Game Finder',
    'Game finder page context'
)