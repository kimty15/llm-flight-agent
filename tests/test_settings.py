from config.settings import Settings


def test_settings_defaults_describe_trip_planner():
    settings = Settings(_env_file=None)

    assert settings.product_name == "Nha Trang Trip Planner Agent"
    assert settings.default_location == "Nha Trang, Việt Nam"
    assert settings.food_max_results == 5
    assert settings.search_language == "vi"
    assert settings.search_country == "vn"
    assert settings.google_domain == "google.com.vn"
