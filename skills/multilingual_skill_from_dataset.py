import json
import yaml
import re


def jsonl_to_yaml(input_file, output_file):
    # Read the JSONL file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    # Create the YAML structure
    yaml_data = {
        'created_by': 'rhelai_bu',
        'seed_examples': [],
        'task_description': 'To train the language model to respond in the same language used in the question or prompt.'
    }

    # Add each question-answer pair to the seed_examples
    for item in data:
        try:
            example = {
                'question': item['question'],
                'answer': item['answer']
            }
            yaml_data['seed_examples'].append(example)
        except KeyError:
            print(f"Skipping item: {item}")

    # Write to YAML file manually with proper formatting
    with open(output_file, 'w', encoding='utf-8') as f:
        # Add document start marker
        f.write("---\n")
        # Add created_by with proper indentation
        f.write("created_by: rhelai_bu\n")
        # Add seed_examples with proper indentation
        f.write("seed_examples:\n")

        # Add each example with proper indentation
        for example in yaml_data['seed_examples']:
            f.write("  - question: ")
            # Properly quote the question if needed
            question = example['question']
            if re.search(r'[:\{\}\[\],&*#?|<>=!%@`\n]', question):
                # Replace double quotes with single quotes and then quote the string
                escaped_question = question.replace('"', "'")
                f.write(f"\"{escaped_question}\"\n")
            else:
                f.write(f"{question}\n")

            f.write("    answer: ")
            # Properly quote the answer if needed
            answer = example['answer']
            if re.search(r'[:\{\}\[\],&*#?|<>=!%@`\n]', answer):
                # Replace double quotes with single quotes and then quote the string
                escaped_answer = answer.replace('"', "'")
                f.write(f"\"{escaped_answer}\"\n")
            else:
                f.write(f"{answer}\n")

        # Add task_description with proper indentation and pipe character
        f.write("task_description: |\n")
        f.write(
            "  To train the language model to respond in the same language used in the question or prompt.\n")


if __name__ == "__main__":
    input_file = "multilingual_qa_dataset.jsonl"  # Input file path
    output_file = "multilingual_skill.yaml"       # Output file path
    jsonl_to_yaml(input_file, output_file)
    print(f"Conversion complete. YAML file saved to {output_file}")
