from shiny import App, reactive, render, ui
from shinywidgets import render_altair, output_widget

home_page = ui.nav_panel(
    'Home',
    # ui.tags.link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'),
    ui.h1('Explore RLCS 1v1 Statistics', class_='bg-gray-300'),
    ui.tags.ol(
        ui.tags.li('Find games that match specific criteria'),
        ui.tags.li('Dive into player statistics'),
        ui.tags.li('Compare players head to head'),
        ui.tags.li('Check player camera settings')
    ),
    ui.p('All data comes from ', ui.a('Ballchasing', href='https://ballchasing.com/group/1v1-events-spqzm3tx17', target='_blank')),
    output_widget('plot_map_count'),
    ui.output_ui('table_map_count')
)