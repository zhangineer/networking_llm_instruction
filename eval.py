import json
import ast
import csv
import os
import argparse
import sys

from typing import Dict, List
from utils.base_client import BaseACIClient
from utils.conversation import Conversation
from utils.logger_config import create_logger

LOGGER = create_logger('logs/eval.log', __name__)


class EvalDataManager:
    def __init__(self, input_file: json):
        self.input_file = input_file
        self.eval_data = self.read_json()

    def read_json(self) -> Dict:
        with open(self.input_file, 'r') as file:
            return json.load(file)

    def validate_test_data(self):
        aci_client = BaseACIClient()
        aci_client.initiate_ssh_session()
        for user_answer in self.eval_data:  # this is to validate whether any of the answers returns an empty result
            self.test_user_answer(user_answer['completion'].strip() + ' -o json', aci_client)

    @staticmethod
    def test_user_answer(cmd, aci_client):
        aci_response = aci_client.send_cmd(cmd)
        if "No Mos found" in aci_response:
            print("No Mos Found, cmd executed: ", cmd)
        else:
            print(ast.literal_eval(aci_response)['totalCount'])


def write_to_csv(data, csv_file):
    # Specify the CSV file to append to

    # Creating header
    header = ['Total'] + [f'Q{i}' for i in range(1, len(data))]

    # Check if the file exists and is empty
    file_exists = os.path.isfile(csv_file)
    file_empty = os.stat(csv_file).st_size == 0 if file_exists else True

    # Open the CSV file in append mode
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)

        # If the file is newly created or empty, write the header
        if file_empty:
            writer.writerow(header)

        # Determine the number of rows to write based on the length of the lists
        num_rows = len(next(iter(data.values())))

        # Iterate through each index of the lists
        for i in range(num_rows):
            # Extract the score for each question at the current index
            row = [scores[i] for scores in data.values()]
            # Write the row to the CSV file
            writer.writerow(row)

    print(f"Data appended to {csv_file}.")


def send_to_chatgpt(questions, instructions):
    with open(instructions, 'r') as f:
        full_instructions = f.readlines()

    print ("sending request to openAI")
    conversation = Conversation(system_prompt=f"{full_instructions}", model="gpt-4-1106-preview", tool_choice=None, max_tokens=4000)

    conversation.add_user_message(message=f"answer the following questions line by line, do not include any quotes, {questions}")
    conversation.send_completion_request()
    total_cost = 0
    if conversation.model == "gpt-4-0613":
        cost = round(int(conversation.usage["total_tokens"]) / 1000 * 0.03, 2)
        total_cost += cost
        LOGGER.info(f"using gpt-4-0613, this run cost: {total_cost} with {conversation.usage['total_tokens']} tokens")
    elif conversation.model == "gpt-4-1106-preview":
        cost = round(int(conversation.usage["total_tokens"]) / 1000 * 0.01, 2)
        total_cost += cost
        print(f"using gpt-4-1106-preview, this run cost: {total_cost} with {conversation.usage['total_tokens']} tokens")
        LOGGER.info(f"using gpt-4-1106-preview, this run cost: {total_cost} with {conversation.usage['total_tokens']} tokens")

    LOGGER.info(f"Response from chatGPT\n: {conversation.response['content']}")
    chatgpt_answers = [line.strip() for line in conversation.response['content'].splitlines() if line.strip()]
    return chatgpt_answers


def compare_dicts(dict1, dict2):
    if dict1.keys() != dict2.keys():
        return False
    for key in dict1:
        if not compare(dict1[key], dict2[key]):
            return False
    return True


def compare_lists(list1, list2):
    if len(list1) != len(list2):
        return False
    matched_indices = set()
    for item1 in list1:
        match_found = False
        for i, item2 in enumerate(list2):
            if i not in matched_indices and compare(item1, item2):
                matched_indices.add(i)
                match_found = True
                break
        if not match_found:
            return False
    return True


def compare(value1, value2):
    if type(value1) != type(value2):
        return False
    if isinstance(value1, dict) and isinstance(value2, dict):
        return compare_dicts(value1, value2)
    elif isinstance(value1, list) and isinstance(value2, list):
        return compare_lists(value1, value2)
    else:
        return value1 == value2


def eval_chatgpt_answers(eval_qa, answers, scores, client) -> Dict:
    """

    :param eval_qa:
    :param answers:
    :param scores:
    :param client:
    :return:
    """
    correct_count = 0
    total = 0
    for index, (user_answer, chatgpt_answer) in enumerate(zip(eval_qa, answers), 1):
        question = f"Q{index}. {user_answer['prompt']}"
        LOGGER.info(f"Question: {question}")
        LOGGER.info(f"correct answer cmd: {user_answer['completion'].strip()}")
        LOGGER.info(f"gpt answer cmd: {chatgpt_answer.strip()}")

        print(f"Question: {question}")
        print(f"correct answer cmd: {user_answer['completion'].strip()}")
        print(f"gpt answer cmd: {chatgpt_answer.strip()}")

        total += 1

        # if the cmd is 100% matched, we do not need to execute it.
        if user_answer['completion'].strip() == chatgpt_answer.strip():
            LOGGER.info("command is 100% matched")
            correct_count += 1
            if question in scores.keys():
                scores[question].append(1)
            else:
                scores[question] = [1]
        else:
            correct_cmd_output = client.send_cmd(user_answer['completion'].strip() + ' -o json')
            chatgpt_cmd_output = client.send_cmd(chatgpt_answer.strip() + ' -o json')
            LOGGER.info(f"correct cmd output: {correct_cmd_output}")
            LOGGER.info(f"chatGPT cmd output: {chatgpt_cmd_output}")

            if 'No Mos found' in correct_cmd_output:
                LOGGER.warning("Correct CLI returned no Mos, "
                               "double check to ensure that the CLI command is correct and that the object exists")
                print("Correct CLI returned no Mos")
                continue

            if 'No Mos found' in chatgpt_cmd_output:
                LOGGER.info("No Mos found")
                print("No Mos found returned")
                chatgpt_cmd_output = '{"No Mos found"}'
            else:  # catch all remaining errors
                LOGGER.info("Malformed response")
                try:
                    ast.literal_eval(chatgpt_cmd_output)
                except (SyntaxError, ValueError):
                    chatgpt_cmd_output = '{"error"}'

            if compare(ast.literal_eval(chatgpt_cmd_output), ast.literal_eval(correct_cmd_output)):
                LOGGER.info("commands doesn't match, but answer is correct")
                correct_count += 1
                if question in scores.keys():
                    scores[question].append(1)
                else:
                    scores[question] = [1]
            elif 'error' in chatgpt_cmd_output:
                LOGGER.info("incorrect syntax")
                print("incorrect syntax")
                if question in scores.keys():
                    scores[question].append(-1)
                else:
                    scores[question] = [-1]
            else:
                LOGGER.info("incorrect result, but syntax was correct")
                print("incorrect")
                if question in scores.keys():
                    scores[question].append(0)
                else:
                    scores[question] = [0]

    correction_rate = correct_count / total * 100
    scores["Total"].append(round(correction_rate, 2))
    print(f"correct count: {correct_count}")
    print(f"Total: {total}")
    print(f"correction rate: {round(correction_rate,2)}")
    return scores


def main():
    parser = argparse.ArgumentParser(description="Run evaluation with different instructions and collect results")

    # Create a mutually exclusive group
    group = parser.add_mutually_exclusive_group()

    # Add arguments to the group
    group.add_argument('--few_shot', action='store_true', help='Use settings for few-shot instructions.')
    group.add_argument('--zero_shot', action='store_true', help='Use settings for zero-shot instructions.')
    group.add_argument('--tuned', action='store_true', help='Use settings for a tuned instructions.')

    # Add non-exclusive argument
    parser.add_argument('--iteration', type=int, default=1, help='Number of iterations to run (default is 1).')

    # Parse the arguments
    args = parser.parse_args()

    # Conditional file assignments based on the input arguments
    if args.few_shot:
        csv_file = 'results/few_shot_results.csv'
        instruction = 'instructions/few_shot.md'
    elif args.zero_shot:
        csv_file = 'results/zero_shot_results.csv'
        instruction = 'instructions/zero_shot.md'
    elif args.tuned:
        csv_file = 'results/tuned_results.csv'
        instruction = 'instructions/tuned.md'
    else:
        sys.exit("You must provide at least one mode to run")
    # Show the number of iterations
    print("Number of iterations:", args.iteration)

    eval_manager = EvalDataManager('dataset/qa_data.json')
    # eval_manager.validate_test_data()

    questions = [data['prompt']+"?" for data in eval_manager.eval_data]

    for _ in range(args.iteration):
        total_score = {"Total": []}
        gpt_answers = send_to_chatgpt(questions, instruction)
        aci_client = BaseACIClient()
        aci_client.initiate_ssh_session()
        total_score = eval_chatgpt_answers(eval_qa=eval_manager.eval_data,
                                           answers=gpt_answers,
                                           scores=total_score,
                                           client=aci_client)
        aci_client.close_session()
        write_to_csv(total_score, csv_file)
        LOGGER.info(total_score)
        print(total_score)


if __name__ == "__main__":
    main()