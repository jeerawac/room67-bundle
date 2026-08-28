"""Model fit + evaluation: pandas and scikit-learn only, no Spark and no
I/O, so it runs on a GitHub runner exactly as it runs on the cluster."""

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


def fit_and_evaluate(pdf, test_size: float = 0.2, random_state: int = 42):
    """Fit fare_amount ~ trip_distance, return (model, rmse, train_df,
    test_df, predictions) for a held-out split. train_df comes back for the
    row count train_demo.py logs and the input_example it registers
    alongside the model; test_df/predictions come back so train_demo.py can
    plot them (predicted vs actual) without re-running the split or the
    model.
    """
    train_df, test_df = train_test_split(pdf, test_size=test_size, random_state=random_state)

    model = LinearRegression().fit(train_df[["trip_distance"]], train_df["fare_amount"])

    predictions = model.predict(test_df[["trip_distance"]])
    rmse = mean_squared_error(test_df["fare_amount"], predictions) ** 0.5

    return model, rmse, train_df, test_df, predictions
