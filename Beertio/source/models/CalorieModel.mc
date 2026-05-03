import Toybox.ActivityMonitor;
import Toybox.Lang;

class CalorieModel {
    private var _foodItem as FoodItem;

    function initialize(foodItem as FoodItem) {
        _foodItem = foodItem;
    }

    function getCaloriesBurned() as Number {
        var info = ActivityMonitor.getInfo();
        if (info != null && info.calories != null) {
            return info.calories as Number;
        }
        return 0;
    }

    function getUnits() as Float {
        var calories = getCaloriesBurned();
        if (_foodItem.caloriesPerUnit == 0) {
            return 0.0f;
        }
        return calories.toFloat() / _foodItem.caloriesPerUnit.toFloat();
    }

    function getFoodItem() as FoodItem {
        return _foodItem;
    }
}
