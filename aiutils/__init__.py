import os
import json
import tiktoken

# Define the path to the pricing JSON within the package
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
PRICING_FILE = os.path.join(PACKAGE_DIR, 'pricing.json')

# Load the pricing JSON
def load_pricing_data():
    with open(PRICING_FILE, 'r') as pricing_file:
        return json.load(pricing_file)

# Price check function
def pricecheck(response, comparison_model=None):
    pricing_data = load_pricing_data()

    # Extract necessary information from the response
    model_name = response.model
    output_tokens = response.usage.completion_tokens
    input_tokens = response.usage.prompt_tokens

    # Determine the correct model for pricing
    if model_name in pricing_data['models']:
        model_pricing = pricing_data['models'][model_name]
    else:
        if model_name in pricing_data['mapping']:
            mapped_model = pricing_data['mapping'][model_name]
            model_pricing = pricing_data['models'][mapped_model]
        else:
            raise ValueError(f"Model {model_name} not found in pricing data and no mapping exists.")

    # Calculate costs
    input_cost = model_pricing['standard']['input'] * (input_tokens / 1_000_000)
    output_cost = model_pricing['standard']['output'] * (output_tokens / 1_000_000)
    total_cost = input_cost + output_cost
    total_tokens = input_tokens + output_tokens

    # Save outputs as variable 'results'
    results = f"""
    Model used: {model_name}
    Tokens | In: {input_tokens} | Out: {output_tokens} | Total: {total_tokens}
    Cost | In: ${input_cost:.4f} | Out: ${output_cost:.4f}, Total: ${total_cost:.4f}
    """

    # Comparison with another model
    if comparison_model:
        if comparison_model in pricing_data['models']:
            comparison_pricing = pricing_data['models'][comparison_model]
        else:
            if comparison_model in pricing_data['mapping']:
                mapped_comparison_model = pricing_data['mapping'][comparison_model]
                comparison_pricing = pricing_data['models'][mapped_comparison_model]
            else:
                raise ValueError(f"Comparison model {comparison_model} not found in pricing data and no mapping exists.")

        # Calculate comparison costs
        comparison_input_cost = comparison_pricing['standard']['input'] * (input_tokens / 1_000_000)
        comparison_output_cost = comparison_pricing['standard']['output'] * (output_tokens / 1_000_000)
        comparison_total_cost = comparison_input_cost + comparison_output_cost
        cost_difference = total_cost - comparison_total_cost

        if cost_difference < 0:
            comparison = "more expensive"
        elif cost_difference > 0:
            comparison = "cheaper"
        else:
            comparison = "different (same price)"

        # Print the comparison results
        print(f"{comparison_model} Comparison: Input: ${comparison_input_cost:.4f} | Out: ${comparison_output_cost:.4f}, Total: ${comparison_total_cost:.4f}")
        print(f"Cost Difference: {comparison_model} would be ${abs(cost_difference):.4f} {comparison}")

        print(results)

    return results

# Token counting functions
def tokencount_file(input_file, model="gpt-4"):
    # Get the encoding for the specified model
    encoding = tiktoken.encoding_for_model(model)
    
    # Function to read the content of the text file
    def read_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    # Function to count tokens using tiktoken
    def count_tokens(text):
        tokens = encoding.encode(text)
        return len(tokens)
    
    # Extract content from the input file
    content = read_file(input_file)
    
    # Count the tokens in the content
    token_count = count_tokens(content)
    
    return token_count

def tokencount_text(text, model="gpt-4"):
    # Get the encoding for the specified model
    encoding = tiktoken.encoding_for_model(model)
    
    # Function to count tokens using tiktoken
    def count_tokens(text):
        tokens = encoding.encode(text)
        return len(tokens)
    
    # Count the tokens in the text
    token_count = count_tokens(text)
    
    return token_count