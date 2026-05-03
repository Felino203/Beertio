import Toybox.Graphics;
import Toybox.Lang;
import Toybox.WatchUi;

class BeertioGlanceView extends WatchUi.GlanceView {
    private var _model as CalorieModel;
    private var _renderer as FoodIconRenderer;

    function initialize(model as CalorieModel) {
        GlanceView.initialize();
        _model = model;
        _renderer = new FoodIconRenderer();
    }

    function onUpdate(dc as Graphics.Dc) as Void {
        var width = dc.getWidth();
        var height = dc.getHeight();

        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_BLACK);
        dc.clear();

        var iconSize = (height * 0.7).toNumber();
        var iconX = (width * 0.05).toNumber();
        var iconY = ((height - iconSize) / 2).toNumber();

        _renderer.draw(dc, _model.getFoodItem().polygons, iconX, iconY, iconSize, iconSize);

        var units = _model.getUnits();
        var text = units.format("%.1f");

        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_TRANSPARENT);
        var textX = iconX + iconSize + (width * 0.05).toNumber();
        var textY = (height / 2).toNumber();
        dc.drawText(textX, textY, Graphics.FONT_GLANCE, text, Graphics.TEXT_JUSTIFY_LEFT | Graphics.TEXT_JUSTIFY_VCENTER);
    }
}
