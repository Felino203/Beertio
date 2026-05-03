import Toybox.Graphics;
import Toybox.Lang;

class FoodIconRenderer {
    function draw(dc as Graphics.Dc, polygons as Array, x as Number, y as Number, width as Number, height as Number) as Void {
        for (var i = 0; i < polygons.size(); i++) {
            var polygon = polygons[i] as Dictionary;
            var color = polygon[:color] as Number;
            var normalizedPoints = polygon[:points] as Array;

            var scaledPoints = scalePoints(normalizedPoints, x, y, width, height);

            dc.setColor(color, Graphics.COLOR_TRANSPARENT);
            dc.fillPolygon(scaledPoints);
        }
    }

    private function scalePoints(normalizedPoints as Array, x as Number, y as Number, width as Number, height as Number) as Array {
        var result = new Array[normalizedPoints.size()];
        for (var i = 0; i < normalizedPoints.size(); i++) {
            var point = normalizedPoints[i] as Array;
            var px = x + ((point[0] as Float) * width).toNumber();
            var py = y + ((point[1] as Float) * height).toNumber();
            result[i] = [px, py];
        }
        return result;
    }
}
