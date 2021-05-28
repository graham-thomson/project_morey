import numpy as np
import pandas as pd


def apply_metric_functions(df):
    for metric_name, func in metrics_dict.items():
        df = df.merge(
            pd.Series(df.apply(func, axis=1), name=metric_name),
            left_index=True,
            right_index=True,
        )
    return df


metrics_dict = {
    "average_cost_per_point": lambda row: np.divide(
        row["salary"], row["total_points"], where=row["total_points"] != 0.0
    ),
    "bmi": lambda row: np.divide(
        np.divide(
            row["weight_lbs"], row["height_inches"], where=row["height_inches"] != 0.0
        ),
        row["height_inches"],
        where=row["height_inches"] != 0.0,
    )
    * 703,
}

rename_dict = {"z_score": "total_points_z_score"}
