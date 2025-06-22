from shiny import App, reactive, render, ui
from shinywidgets import render_altair, output_widget

game_finder_page = ui.nav_panel(
    'Game Finder',
    ui.h1('Game Finder'),
    ui.p('Search for games that match specific criteria')
)