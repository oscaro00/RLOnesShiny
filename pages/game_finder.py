from shiny import App, reactive, render, ui
from shinywidgets import render_altair, output_widget

game_finder_page = ui.nav_panel(
    'Game Finder',
    ui.h1('Game Finder'),
    ui.p('Search for games that match specific criteria'),
    ui.row(
        ui.output_ui('group_multi_selectize')
    ),
    ui.row(
        ui.card(
            ui.card_header('Games matching the filters'),
            ui.output_data_frame('df_matching_games'),
            height='600px'
        ),
    )
)