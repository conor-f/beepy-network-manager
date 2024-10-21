from beepy_web_radio.main import TemplateApp


def test_sample_add_method():
    app = TemplateApp()
    assert app.sample_add_method(2, 3) == 5
    assert app.sample_add_method(-1, 1) == 0
    assert app.sample_add_method(0, 0) == 0
