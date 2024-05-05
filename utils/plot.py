import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List


class ScoreCalc:
    """
    Class to return results for a given data frame
    """
    def __init__(self, dataframe: pd):
        self.df = dataframe

    def get_value_total_count(self, value: int, start_col: str = None, end_col: str = None) -> int:
        """
        This function retrieves the total count of a given specific value across the specified column range
        :param value: an integer value
        :param start_col: starting column number, a string
        :param end_col: ending column number, a string

        Returns: a dictionary as follows {"count":123, "percent": 0.1}
        """
        if start_col and end_col:
            # Ensure the columns exist to avoid KeyError
            if start_col in self.df.columns and end_col in self.df.columns:
                selected_columns = self.df.loc[:, start_col:end_col]
            else:
                raise ValueError("One or both column names are invalid.")
        else:
            selected_columns = self.df

        return round(selected_columns.eq(value).sum().sum() / selected_columns.size * 100, 2)

    def get_score_percentage(self, result: int, score: int) -> float:
        """
        This function calculates the total count of a value for a given score.
        For example: I want to know how many questions was answered correctly 100 times
        :param result: result can be 1 ( correct ), 0 ( incorrect ) or -1 ( invalid )
        :param score: the score to calculate percentage on, such as 100
        :return: the percentage of that score
        """
        final_score = 0
        column_sums = [self.df[column].eq(result).sum().sum() for column in self.df.columns if column.startswith('Q')]
        for column_sum in column_sums:
            if column_sum >= score:
                final_score += 1

        return round(final_score/len(self.df.columns)*100, 2)

    def get_question_total_score(self, result):
        return [self.df[column].eq(result).sum().sum() for column in self.df.columns if column.startswith('Q')]


class PlotResults:
    def __init__(self, **kwargs):
        self.dfs = kwargs.values()
        self.tuned_df = kwargs['tuned']
        # instantiate a list of objects for each dataframes
        self.score_calcs = [ScoreCalc(df) for df in self.dfs]
        self.difficulty_map = {
            'low': ('Q1', 'Q10'),
            'medium': ('Q11', 'Q52'),
            'high': ('Q53', 'Q72')
        }
        self.result_values_map = {
            'invalid': -1,  # invalid syntax
            'incorrect': 0,  # incorrect but syntax is correct
            'correct': 1
        }

    def get_result_stats_summarized(self, difficulty: str, result_value: int) -> Dict:
        if result_value not in self.result_values_map.values():
            raise ValueError(f"Result Value must be one of 1 (correct), 0 (incorrect), -1 (invalid syntax), "
                             f"received {result_value}")
        if difficulty.lower() not in self.difficulty_map.keys():
            raise ValueError("Difficulty must be one of 'low', 'medium', or 'high'")
        questions_range = self.difficulty_map[difficulty.lower()]
        return {f"{difficulty}_{result_value}":
                [score_calc.get_value_total_count(result_value, *questions_range) for score_calc in self.score_calcs]}

    def get_totalscore_mean_values(self) -> Dict:
        """
        :return: a list of mean values for each data frame's 'Total' column
        """
        return {"mean_score": [round(score_calc.df['Total'].mean(), 2) for score_calc in self.score_calcs]}

    def get_totalscore_percentage_values(self, result, score):
        return {f"score_{score}_percentage": [score_calc.get_score_percentage(result, score)
                                              for score_calc in self.score_calcs]}

    def get_all_questions_total(self, result):
        """
        Get the total score for individual questions. each question can have a score of 1 (correct)
        :return: a list of scores individual questions
        """
        tuned_df_calc = ScoreCalc(self.tuned_df)
        return {"question_total_score": tuned_df_calc.get_question_total_score(result)}


def plot_datasets(datasets, title, categories: List, xaxis_title='Categories', yaxis_title='Values'):
    """
    Plots a grouped bar chart for datasets with a simpler dictionary structure.

    Args:
    datasets (list of dicts): Each dictionary contains one description key and a list of values.
    title (str): Title of the plot.
    xaxis_title (str): Title for the X-axis.
    yaxis_title (str): Title for the Y-axis.
    """
    fig = go.Figure()

    for dataset in datasets:
        description, values = next(iter(dataset.items()))  # Unpack the first (and only) item
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            text=values,  # Set the bar texts to be the values
            textposition='outside',  # Position the text outside of bars
            name=description  # Use the key in the dict as the trace name
        ))

    # Update the layout for a clear and readable bar chart
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        xaxis=dict(
            tickfont=dict(
                size=15  # Set font size for x-axis category labels
            )
        )
    )

    fig.show()


if __name__ == "__main__":
    zero_shot_df = pd.read_csv("results/zero_shot_results.csv")
    few_shot_df = pd.read_csv("results/few_shot_results.csv")
    tuned_df = pd.read_csv("results/tuned_results.csv")

    plot_results = PlotResults(**{"zero_shot": zero_shot_df, "few_shot": few_shot_df, "tuned": tuned_df})
    compare_categories = ['zero_shot', 'few_shot', 'tuned']
    for result_value in plot_results.result_values_map.values():
        datasets = [plot_results.get_result_stats_summarized(difficulty=difficulty, result_value=result_value)
                    for difficulty in ['low', 'medium', 'high']]
        if result_value == -1:
            title = 'Percentage of invalid syntax for each difficulty'
        elif result_value == 0:
            title = 'Percentage of incorrect answers for each difficulty'
        else:
            title = 'Percentage of correct answers for each difficulty'
        plot_datasets(datasets=datasets, categories=compare_categories, title=title)

    # Plots the total score data
    totalscore_datasets = [plot_results.get_totalscore_mean_values(), plot_results.get_totalscore_percentage_values(1, 100)]
    plot_datasets(datasets=totalscore_datasets, categories=compare_categories, title='Total Score Data')

    tuned_questions_totalscore_datasets = [plot_results.get_all_questions_total(result=1)] # result = 1 implies that the answer is correct

    # plot individual question score for tuned instructions.
    question_categories = [f'Q{i}' for i in range(1, 73)]
    plot_datasets(datasets=tuned_questions_totalscore_datasets,
                  categories=question_categories,
                  xaxis_title='Questions',
                  title='Individual Question Score With Tuned Instructions')

    # plot invalid syntax score with tuned instructions for individual question
    tuned_questions_totalscore_datasets = [plot_results.get_all_questions_total(result=-1)] # result = -1 implies invalid syntax

    question_categories = [f'Q{i}' for i in range(1, 73)]
    plot_datasets(datasets=tuned_questions_totalscore_datasets,
                  categories=question_categories,
                  xaxis_title='Questions',
                  title='Individual Question Invalid Syntax Score With Tuned Instructions')