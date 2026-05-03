import Toybox.Lang;

module FoodItemRegistry {
    function getItem(id as String) as FoodItem {
        if (id.equals("beer")) {
            return new FoodItem("beer", "Beer", 150, BeerIconData.getPolygons());
        }
        // Default fallback to beer
        return new FoodItem("beer", "Beer", 150, BeerIconData.getPolygons());
    }
}
