from review_agent import (
    analyze_sentiment,
    sentiment_label,
    extract_aspects,
    summarize_reviews,
    get_reviews_for_recipe,
)


def test_positive_sentiment():
    score = analyze_sentiment("This was absolutely delicious, I loved it!")
    assert score > 0
    assert sentiment_label(score) == "positive"
    print("test_positive_sentiment passed")


def test_negative_sentiment():
    score = analyze_sentiment("This was terrible and way too salty.")
    assert score < 0
    assert sentiment_label(score) == "negative"
    print("test_negative_sentiment passed")


def test_neutral_sentiment():
    score = analyze_sentiment("I made this on Tuesday.")
    assert sentiment_label(score) == "neutral"
    print("test_neutral_sentiment passed")


def test_aspect_extraction_finds_taste_and_difficulty():
    reviews = [
        "The taste was amazing, so flavorful!",
        "Super easy to make, done in 10 minutes.",
    ]
    aspects = extract_aspects(reviews)
    assert aspects.get("taste") == "positive"
    assert aspects.get("difficulty") == "positive"
    print("test_aspect_extraction_finds_taste_and_difficulty passed")


def test_aspect_extraction_ignores_unmentioned_aspects():
    reviews = ["It was okay I guess."]
    aspects = extract_aspects(reviews)
    assert "texture" not in aspects  # never mentioned, so shouldn't appear
    print("test_aspect_extraction_ignores_unmentioned_aspects passed")


def test_summary_with_no_reviews():
    summary = summarize_reviews([])
    assert summary == "No reviews available for this recipe yet."
    print("test_summary_with_no_reviews passed")


def test_summary_uses_real_review_text():
    reviews = [
        "This recipe was fantastic and easy to follow.",
        "The kids loved it too, will make again.",
    ]
    summary = summarize_reviews(reviews, max_sentences=1)
    assert any(summary in review or review in summary for review in reviews) or summary in " ".join(reviews)
    print("test_summary_uses_real_review_text passed")


def test_real_recipe_has_reviews():
    # 261429 = "Triple Layer Cookie Bars", confirmed to exist in the real dataset
    reviews = get_reviews_for_recipe("261429")
    assert len(reviews) > 0
    print("test_real_recipe_has_reviews passed")


def test_unknown_recipe_returns_empty_list():
    reviews = get_reviews_for_recipe("this-recipe-does-not-exist")
    assert reviews == []
    print("test_unknown_recipe_returns_empty_list passed")


if __name__ == "__main__":
    test_positive_sentiment()
    test_negative_sentiment()
    test_neutral_sentiment()
    test_aspect_extraction_finds_taste_and_difficulty()
    test_aspect_extraction_ignores_unmentioned_aspects()
    test_summary_with_no_reviews()
    test_summary_uses_real_review_text()
    test_real_recipe_has_reviews()
    test_unknown_recipe_returns_empty_list()
    print("\nAll tests passed!")