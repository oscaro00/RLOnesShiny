from shiny import App, reactive, render, ui
from shinywidgets import render_altair, output_widget

comparison_tool_page = ui.nav_panel(
    'Comparison Tool',
    'Comparison tool page context'
)