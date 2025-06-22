from shiny import ui

player_settings_page = ui.nav_panel(
    'Player Settings',
    ui.h1('Player Settings'),
    ui.output_ui('player_selectize'),
    ui.h3('Camera Settings'),
    ui.row(
        ui.column(4, ui.output_ui('vb_count_unique_camera_settings')),
        ui.column(4, ui.output_ui('vb_pct_series_camera_chg')),
        ui.column(4, ui.output_ui('vb_latest_settings_data'))
    ),
    ui.row(
        ui.column(
            6,
            ui.card(
                ui.card_header('Latest 10 distinct camera settings'),
                ui.output_data_frame('latest_10_camera_settings'),
                height='400px'
            ),
        ),
        ui.column(
            6,
            ui.card(
                ui.card_header('All camera settings'),
                ui.output_data_frame('all_camera_settings'),
                height='400px'
            ),
        )
    ),
    ui.h3('Car Selection'),
    ui.row(
        ui.column(4, ui.output_ui('vb_count_unique_cars')),
        ui.column(4, ui.output_ui('vb_pct_series_car_chg')),
        ui.column(4, ui.output_ui('vb_most_used_car'))
    ),
    ui.row(
        ui.column(
            9,
            ui.card(
                ui.card_header('Cars used by series and game'),
                ui.output_data_frame('all_cars_used'),
                height='400px'
            ),
        ),
    )
)
