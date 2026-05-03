import Toybox.Lang;

class FoodItem {
    var id as String;
    var displayName as String;
    var caloriesPerUnit as Number;
    var polygons as Array;

    function initialize(id as String, displayName as String, caloriesPerUnit as Number, polygons as Array) {
        self.id = id;
        self.displayName = displayName;
        self.caloriesPerUnit = caloriesPerUnit;
        self.polygons = polygons;
    }
}
