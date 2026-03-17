from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging

logger = logging.getLogger("sentiment")

analyzer = SentimentIntensityAnalyzer()


def analyse_sentiment(article_text):
    """
    Analyses the sentiment of the given article text,
    returning a dictionary with a polarity score and a categorical label.
    """
    if not isinstance(article_text, str):
        raise TypeError("Input must be a string")

    if not article_text:
        return {"polarity": 0.0, "label": "neutral"}

    logger.info("Analysing sentiment for text of length %d", len(article_text))

    scores = analyzer.polarity_scores(article_text)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    logger.info("Sentiment result: %s (%.4f)", label, compound)

    return {"polarity": round(compound, 4), "label": label}


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    print(
        analyse_sentiment(
            """Stacey Solomon praises £22 Amazon Essentials cardigan she owns in 'every colour'TV personality Stacey Solomon has shared her love for the £22 Amazon Essentials long cardigan that she owns in 'every colour'LifestyleGrace Salmon Shopping Writer11:57, 17 Mar 2026This article contains affiliate links, we will receive a commission on any sales we generate from it. Learn moreView 2 ImagesStacey Solomon has this Amazon cardigan in 'every colour'(Image: Instagram @staceysolomon)Stacey Solomon has once more showcased her penchant for budget-friendly wardrobe essentials, and this snug cardigan is a prime example. The television personality revealed she's snapped up the Amazon Essentials Women's Oversized-Fit Long Cardigan With Pockets in "every colour", and at a mere £22, it's hardly surprising.As part of Amazon's own-brand Essentials collection, the cardigan prioritises both comfort and adaptability. Its generous, oversized silhouette delivers a casual, easygoing vibe, whilst the extended length makes it brilliant for throwing over loungewear, denim and basic tees.The convenient front pockets add a functional touch, making it spot-on for hectic days when you're rushing about. Crafted from a plush cotton-blend knit, it's airy enough for springtime yet remains toasty when temperatures dip. Available in numerous shades, it's a closet essential you'll find yourself grabbing time and time again.READ MORE: Debenhams 'lovely and solid' 4-piece garden furniture set gets massive £441 discount for springREAD MORE: Princess Andre wears her 'simple yet striking' Swarovski necklace on repeat and it's now on sale for £52View 2 ImagesThere are multiple colours available from khaki to cream(Image: Amazon / Instagram @staceysolomon)Stacey's far from alone in her admiration for this knitwear piece. An Amazon customer raved, "Everything i'm looking for in a cardigan, pockets/longer length/shawl collar. It's cotton blended with some synthetic fibres so not completly synthetic(bonus). Ive just received this item so haven't washed it yet but I think the mixture of fibres will help maintain the cardigans shape after washing.", reports the Mirror.Another satisfied customer shared: "Very happy with the quality and cost of this long cardigan. Looks really good on and so ideal for colder days in Autumn and winter instead of wearing a coat. Good fit in term so sizing and very wearable. Would highly recommend."A third reviewer praised: "This cardigan is very thick and warm. Quite boxy shaped and so comfortable. The fabric is lovely and soft and it seems well made. ".Article continues belowThat said, the primary complaint amongst buyers centred on the generous proportions. One customer remarked: "Cozy texture but quite bulky. Added unwanted size."Hunting for more snuggly knitwear and coatigans? Boden has slashed over £75 off its Jacquard Coatigan, reducing the price from £169 to £84.50. Meanwhile, The White Company has cut 50% off the Cosy Rolled Edge Lounge Cardigan, now £70 down from £140."""
        )
    )
