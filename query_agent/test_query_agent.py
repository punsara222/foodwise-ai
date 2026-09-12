from query_agent import extract_constraints

def test_basic_query():
    result = extract_constraints("high-protein dinner under 500 calories, no dairy")
    assert result["max_calories"] == 500
    assert "dairy-free" in result["diet"]
    assert result["min_protein"] == "high"
    assert result["meal_type"] == "dinner"
    print("test_basic_query passed")

def test_multi_diet():
    result = extract_constraints("vegan breakfast, gluten-free")
    assert "vegan" in result["diet"]
    assert "gluten-free" in result["diet"]
    assert "max_prep_time_minutes" not in result  # regression test for the "breakfast" bug
    print("test_multi_diet passed")

def test_bulking_vs_cutting():
    bulk = extract_constraints("high calorie bulking meal with lots of protein")
    cut = extract_constraints("cutting diet, low calorie, low fat dinner")
    assert "min_calories" in bulk
    assert "max_calories" in cut
    print("test_bulking_vs_cutting passed")

def test_health_condition_mapping():
    result = extract_constraints("heart-healthy dinner, low sodium, I have high blood pressure")
    assert result["health_flag"] == "heart-healthy"
    assert result["max_sodium"] == "low"
    print("test_health_condition_mapping passed")

if __name__ == "__main__":
    test_basic_query()
    test_multi_diet()
    test_bulking_vs_cutting()
    test_health_condition_mapping()
    print("\nAll tests passed!")