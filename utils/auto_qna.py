#!/usr/bin/env python3

# Command-line Arguments
# --input, -i: Input YAML file with contexts(required)
# --output, -o: Output YAML file(required)
# --model, -m: Ollama model to use(default: "llama3")
# --domain, -d: Domain value for template(default: "example-domain")
# --commit, -c: Commit ID for template(default: "main")
# --docs-path, -p: Docs path pattern(default: "docs/*.md")
# --base-url, -u: Base URL for Ollama API(default: "http://localhost:11434/v1")

import yaml
import argparse
import json
import os
from openai import OpenAI
from jinja2 import Template, Environment, BaseLoader


def load_yaml_file(file_path):
    """Load YAML file with contexts"""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def generate_qa_pairs(client, context, num_pairs=3, model="qwen2.5:latest"):
    """Generate question-answer pairs from a given context using Ollama LLM"""

    system_prompt = """
    You are an expert at creating question-answer pairs from context.
    Generate exactly {num_pairs} question-answer pairs from the provided context.
    Each question should ask about different aspects of the context.
    Make questions clear, specific, and based only on information in the context.
    Each question should be in the original language of the context.
    Answer in full sentences.
    
    Return your response in the following JSON format:
    {{
        "qa_pairs": [
            {{
                "question": "First question about the context?",
                "answer": "Answer to the first question based on the context."
            }},
            ...
        ]
    }}
    """

    user_prompt = f"""
    Context:
    {context}
    
    Generate {num_pairs} question-answer pairs from this context in the specified JSON format.
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt.format(
                    num_pairs=num_pairs)},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )

        # Parse the JSON response
        result = json.loads(response.choices[0].message.content)
        return result["qa_pairs"]
    except Exception as e:
        print(f"Error generating QA pairs: {e}")
        # Return empty pairs in case of error
        return [{"question": f"Error generating question {i+1}",
                 "answer": f"Error generating answer {i+1}"} for i in range(num_pairs)]


def yaml_multiline_format(text):
    """Format text to be safely included in YAML as a multiline string"""
    if not text:
        return ""

    # If the text contains a colon, newlines, or other special YAML characters,
    # format it as a literal block scalar with proper indentation
    if ':' in text or '\n' in text or '{' in text or '}' in text or '[' in text or ']' in text:
        # Use literal block scalar (|) with preset indentation (-2)
        # and strip trailing newlines (+)
        return "|\n      " + text.replace("\n", "\n      ")
    return text


def fill_template(context_data, qa_data, template_str, domain="example-domain",
                  commit_id="main", docs_path="docs/*.md"):
    """Fill the Jinja template with context and QA data"""

    # Create a custom Jinja2 environment with filters
    env = Environment(loader=BaseLoader())
    env.filters['yaml_safe'] = yaml_multiline_format
    template = env.from_string(template_str)

    # Create a dictionary with all the values to fill in the template
    template_data = {
        "domain": domain,
        "commit_id": commit_id,
        "docs_path": docs_path,
        "doc_outline": "Generated document outline"
    }

    # Add context data
    for i, (key, value) in enumerate(context_data.items(), 1):
        if key.startswith('c'):
            template_data[key] = value

    # Add QA data
    for context_num in range(1, 6):
        context_key = f"c{context_num}"
        if context_key in context_data:
            qa_pairs = qa_data.get(context_key, [])
            for i, qa_pair in enumerate(qa_pairs[:3], 1):
                template_data[f"{context_key}q{i}"] = qa_pair.get(
                    "question", f"Missing question {i}")
                template_data[f"{context_key}a{i}"] = qa_pair.get(
                    "answer", f"Missing answer {i}")

    # Fill the template
    return template.render(template_data)


def main():
    parser = argparse.ArgumentParser(
        description="Generate QA pairs from context using Ollama LLM")
    parser.add_argument("--input", "-i", required=True,
                        help="Input YAML file with contexts")
    parser.add_argument("--output", "-o", required=True,
                        help="Output YAML file")
    parser.add_argument("--model", "-m", default="qwen2.5:latest",
                        help="Ollama model to use (default: qwen2.5:latest)")
    parser.add_argument(
        "--domain", "-d", default="example-domain", help="Domain value for template")
    parser.add_argument("--commit", "-c", default="main",
                        help="Commit ID for template")
    parser.add_argument("--docs-path", "-p", default="docs/*.md",
                        help="Docs path pattern for template")
    parser.add_argument(
        "--base-url", "-u", default="http://localhost:11434/v1", help="Base URL for Ollama API")

    args = parser.parse_args()

    # Load the YAML file with contexts
    contexts = load_yaml_file(args.input)

    # Initialize OpenAI client to connect to Ollama
    client = OpenAI(base_url=args.base_url, api_key="ollama")

    # Generate QA pairs for each context
    qa_data = {}
    for context_key, context_text in contexts.items():
        if context_key.startswith('c') and context_text:
            print(f"Generating QA pairs for {context_key}...")
            qa_data[context_key] = generate_qa_pairs(
                client, context_text, model=args.model)

    # Template string - updated to handle multiline content safely
    template_str = """---
version: 3
domain: {{domain}}
created_by: rhelai_bu
seed_examples:
  - context: {{ c1|yaml_safe }}
    questions_and_answers:
      - question: {{ c1q1|yaml_safe }}
        answer: {{ c1a1|yaml_safe }}
      - question: {{ c1q2|yaml_safe }}
        answer: {{ c1a2|yaml_safe }}
      - question: {{ c1q3|yaml_safe }}
        answer: {{ c1a3|yaml_safe }}

  - context: {{ c2|yaml_safe }}
    questions_and_answers:
      - question: {{ c2q1|yaml_safe }}
        answer: {{ c2a1|yaml_safe }}
      - question: {{ c2q2|yaml_safe }}
        answer: {{ c2a2|yaml_safe }}
      - question: {{ c2q3|yaml_safe }}
        answer: {{ c2a3|yaml_safe }}

  - context: {{ c3|yaml_safe }}
    questions_and_answers:
      - question: {{ c3q1|yaml_safe }}
        answer: {{ c3a1|yaml_safe }}
      - question: {{ c3q2|yaml_safe }}
        answer: {{ c3a2|yaml_safe }}
      - question: {{ c3q3|yaml_safe }}
        answer: {{ c3a3|yaml_safe }}

  - context: {{ c4|yaml_safe }}
    questions_and_answers:
      - question: {{ c4q1|yaml_safe }}
        answer: {{ c4a1|yaml_safe }}
      - question: {{ c4q2|yaml_safe }}
        answer: {{ c4a2|yaml_safe }}
      - question: {{ c4q3|yaml_safe }}
        answer: {{ c4a3|yaml_safe }}

  - context: {{ c5|yaml_safe }}
    questions_and_answers:
      - question: {{ c5q1|yaml_safe }}
        answer: {{ c5a1|yaml_safe }}
      - question: {{ c5q2|yaml_safe }}
        answer: {{ c5a2|yaml_safe }}
      - question: {{ c5q3|yaml_safe }}
        answer: {{ c5a3|yaml_safe }}

document_outline: {{ doc_outline|yaml_safe }}
document:
  repo: https://github.com/williamcaban/multilingual-lab.git
  commit: {{commit_id}}
  patterns:
    - {{docs_path}}
"""

    # Fill the template
    filled_template = fill_template(
        contexts,
        qa_data,
        template_str,
        domain=args.domain,
        commit_id=args.commit,
        docs_path=args.docs_path
    )

    # Write the filled template to the output file
    with open(args.output, 'w') as file:
        file.write(filled_template)

    print(f"Generated YAML file: {args.output}")


if __name__ == "__main__":
    main()
