import Toybox.Application;
import Toybox.Lang;
import Toybox.WatchUi;

class BeertioApp extends Application.AppBase {
    private var _model as CalorieModel?;

    function initialize() {
        AppBase.initialize();
    }

    function onStart(state as Dictionary?) as Void {
        var itemId = AppSettings.getSelectedItemId();
        var foodItem = FoodItemRegistry.getItem(itemId);
        _model = new CalorieModel(foodItem);
    }

    function onStop(state as Dictionary?) as Void {
    }

    function getInitialView() as [Views] or [Views, InputDelegates] {
        return [new BeertioView(_model as CalorieModel)];
    }

    function getGlanceView() as [GlanceView] or [GlanceView, GlanceViewDelegate] or Null {
        return [new BeertioGlanceView(_model as CalorieModel)];
    }
}

function getApp() as BeertioApp {
    return Application.getApp() as BeertioApp;
}