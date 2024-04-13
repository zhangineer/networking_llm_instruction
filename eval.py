import re
from dataset.aci_moquery_test_examples import examples
import json
from utils.base_client import BaseACIClient
from utils.conversation import Conversation
import ast
from utils.logger_config import create_logger
LOGGER = create_logger('logs/eval.log', __name__)

# "gpt-4-0613" costs 0.03 per 1000 tokens


def parse_input_to_json(text):
    """
    Parses the input text containing pairs of prompts and completions
    and returns them as a list of tuples.

    :param text: str, input text containing prompts and completions
    :return: list of tuples (prompt, completion)
    """
    # Regular expression to match the pattern:
    # * <prompt>?
    # <completion>
    pattern = r"\*\s(.*?)\?\n(.*?)(?=\n\*\s|\Z)"

    matches = re.findall(pattern, text, re.DOTALL)

    # Convert matches to a list of dictionaries
    data_list = [{"prompt": prompt, "completion": completion} for prompt, completion in matches]
    return data_list


def update_json_all(json_file_path):
    parsed_json_data = parse_input_to_json(examples)
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(parsed_json_data, file, indent=4)


def read_json(json_file_path):
    with open(json_file_path, 'r') as file:
        return json.load(file)


def moquery_to_rest(moquery_cmd):
    """
    Translates a moquery command to REST API syntax.

    :param moquery_cmd: str, the moquery command
    :return: str, REST API URL
    """
    # Extract the class and options from the moquery command
    # Extract the class from the moquery command
    d_option_match = re.search(r"-d\s([^\s]+)", moquery_cmd)
    if d_option_match:
        # Use the -d option value as the base URL
        base_url = f"/mo/{d_option_match.group(1)}"
    else:
        class_match = re.search(r"-c\s(\w+)", moquery_cmd)
        base_url = "class/"
        if class_match:
            base_url += f"{class_match.group(1)}.json"

    # Extract the options following -x
    options = []
    parts = re.split(r"-x\s", moquery_cmd)[1:]  # Split by -x and ignore the first part (moquery -c ...)
    for part in parts:
        # Check for quoted and unquoted parts
        cleaned_part = re.sub(r"'", "", part).strip()
        if " " in cleaned_part:
            options.extend(cleaned_part.split())
        else:
            options.append(cleaned_part)

    # Concatenate options to the base URL
    if options:
        base_url += "?"
        base_url += '&'.join(options)

    return base_url


def read_text_file(text_file_path):
    with open (text_file_path, 'r') as f:
        return f.readlines()


with open("instructions/full_instructions.md", 'r') as f:
    full_instructions = f.readlines()


def test_user_answer(cmd, aci_client):
    aci_response = aci_client.send_cmd(cmd)
    if "No Mos found" in aci_response:
        print("No Mos Found, cmd executed: ", cmd)
    else:
        print(ast.literal_eval(aci_response)['totalCount'])


def compare_results(correction_rate, save_point):
    saved_data = read_json(save_point)

eval_json = "dataset/testing_all.json"
EVAL_DATA = read_json(eval_json)


def send_to_chatgpt():
    print ("sending request to openAI")
    conversation = Conversation(system_prompt=f"{full_instructions}", model="gpt-4-1106-preview", tool_choice=None, max_tokens=4000)

    # conversation = Conversation(system_prompt=f"{full_instructions}", model="gpt-4-0613", tool_choice=None,
    #                             max_tokens=256)
    moquery_questions = [data['prompt']+"?" for data in EVAL_DATA]
    conversation.add_user_message(message=f"answer the following questions line by line, do not include any quotes, {moquery_questions}")
    conversation.send_completion_request()
    total_cost = 0
    if conversation.model == "gpt-4-0613":
        cost = round(int(conversation.usage["total_tokens"]) / 1000 * 0.03, 2)
        total_cost += cost
        LOGGER.info(f"using gpt-4-0613, this run cost: {total_cost} with {conversation.usage['total_tokens']} tokens")
    elif conversation.model == "gpt-4-1106-preview":
        cost = round(int(conversation.usage["total_tokens"]) / 1000 * 0.01, 2)
        total_cost += cost
        LOGGER.info(f"using gpt-4-1106-preview, this run cost: {total_cost} with {conversation.usage['total_tokens']} tokens")
    # for command in (ast.literal_eval(conversation.response['content'])):
    #     print (command)
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


def eval_chatgpt_answers(answers, scores, client):
    correct_count = 0
    total = 0
    for index, (user_answer, chatgpt_answer) in enumerate(zip(EVAL_DATA, answers), 1):
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

            if 'No Mos found' in chatgpt_cmd_output:
                LOGGER.info("No Mos found")
                print("No Mos found returned")
                chatgpt_cmd_output = '{"No Mos found"}'
            else: # catch all remaining errors
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


def update_test_data():
    aci_client = BaseACIClient()
    aci_client.initiate_ssh_session()
    update_json_all("dataset/testing_all.json")


def validate_test_data():
    aci_client = BaseACIClient()
    aci_client.initiate_ssh_session()
    user_answers = read_json("dataset/testing_all.json")
    for user_answer in user_answers: # this is to validate whether any of the answers returns an empty result
        test_user_answer(user_answer['completion'].strip() + ' -o json', aci_client)


def write_to_csv(data):
    import csv
    import os

    # Specify the CSV file to append to
    csv_file_path = 'results/result.csv'

    # Creating header
    header = ['Total'] + [f'Q{i}' for i in range(1, len(data))]

    # Check if the file exists and is empty
    file_exists = os.path.isfile(csv_file_path)
    file_empty = os.stat(csv_file_path).st_size == 0 if file_exists else True

    # Open the CSV file in append mode
    with open(csv_file_path, mode='a', newline='') as file:
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

    print(f"Data appended to {csv_file_path}.")


if __name__ == "__main__":
    update_test_data()
    validate_test_data()
    for _ in range(1):
        total_score = {"Total": []}
        gpt_answers = send_to_chatgpt()
        aci_client = BaseACIClient()
        aci_client.initiate_ssh_session()
        total_score = eval_chatgpt_answers(gpt_answers, total_score, aci_client)
        aci_client.close_session()
        write_to_csv(total_score)
        LOGGER.info(total_score)
        print(total_score)