import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Timer;
import Toybox.WatchUi;

class BeertioView extends WatchUi.View {
    private var _model as CalorieModel;
    private var _renderer as FoodIconRenderer;
    private var _timer as Timer.Timer?;

    function initialize(model as CalorieModel) {
        View.initialize();
        _model = model;
        _renderer = new FoodIconRenderer();
    }

    function onShow() as Void {
        _timer = new Timer.Timer();
        _timer.start(method(:onTimerUpdate), Constants.UPDATE_INTERVAL_MS, true);
    }

    function onTimerUpdate() as Void {
        WatchUi.requestUpdate();
    }

    function onUpdate(dc as Graphics.Dc) as Void {
        var width = dc.getWidth();
        var height = dc.getHeight();

        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_BLACK);
        dc.clear();

        var iconSize = (width * 0.5).toNumber();
        var iconX = ((width - iconSize) / 2).toNumber();
        var iconY = (height * 0.15).toNumber();

        _renderer.draw(dc, _model.getFoodItem().polygons, iconX, iconY, iconSize, iconSize);

        var units = _model.getUnits();
        var text = units.format("%.1f");

        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
        var textY = iconY + iconSize + (height * 0.05).toNumber();
        dc.drawText(width / 2, textY, Graphics.FONT_LARGE, text, Graphics.TEXT_JUSTIFY_CENTER);
    }

    function onHide() as Void {
        if (_timer != null) {
            _timer.stop();
            _timer = null;
        }
    }
}
