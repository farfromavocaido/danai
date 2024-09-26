import tiktoken
from .json_manager import check_for_update

def load_pricing_data():
    """
    Load the pricing data, checking if an update is needed.
    If the pricing data is outdated, prompt the user to update.
    """
    return check_for_update()

def pricecheck(response, comparison_model=None):
    """
    Calculate the cost of tokens generated by an OpenAI model based on the pricing data.

    Parameters:
    response: The response object from the OpenAI API.
    comparison_model: An optional model name for cost comparison.

    Returns:
    A string detailing the model used, tokens consumed, and the total cost.
    """
    pricing_data = load_pricing_data()

    model_name = response.model
    output_tokens = response.usage.completion_tokens
    input_tokens = response.usage.prompt_tokens

    if model_name in pricing_data['models']:
        model_pricing = pricing_data['models'][model_name]
    else:
        if model_name in pricing_data['mapping']:
            mapped_model = pricing_data['mapping'][model_name]
            model_pricing = pricing_data['models'][mapped_model]
        else:
            raise ValueError(f"Model {model_name} not found in pricing data and no mapping exists.")

    input_cost = model_pricing['standard']['input'] * (input_tokens / 1_000_000)
    output_cost = model_pricing['standard']['output'] * (output_tokens / 1_000_000)
    total_cost = input_cost + output_cost
    total_tokens = input_tokens + output_tokens

    results = f"""
    Model used: {model_name}
    Tokens | In: {input_tokens} | Out: {output_tokens} | Total: {total_tokens}
    Cost | In: ${input_cost:.4f} | Out: ${output_cost:.4f}, Total: ${total_cost:.4f}
    """

    if comparison_model:
        if comparison_model in pricing_data['models']:
            comparison_pricing = pricing_data['models'][comparison_model]
        else:
            if comparison_model in pricing_data['mapping']:
                mapped_comparison_model = pricing_data['mapping'][comparison_model]
                comparison_pricing = pricing_data['models'][mapped_comparison_model]
            else:
                raise ValueError(f"Comparison model {comparison_model} not found in pricing data and no mapping exists.")

        comparison_input_cost = comparison_pricing['standard']['input'] * (input_tokens / 1_000_000)
        comparison_output_cost = comparison_pricing['standard']['output'] * (output_tokens / 1_000_000)
        comparison_total_cost = comparison_input_cost + comparison_output_cost
        cost_difference = total_cost - comparison_total_cost

        comparison = "cheaper" if cost_difference > 0 else "more expensive" if cost_difference < 0 else "the same price"

        print(f"{comparison_model} Comparison: Input: ${comparison_input_cost:.4f} | Out: ${comparison_output_cost:.4f}, Total: ${comparison_total_cost:.4f}")
        print(f"Cost Difference: {comparison_model} would be ${abs(cost_difference):.4f} {comparison}")

    return results

def tokencount_file(input_file, model="gpt-4"):
    """
    Count the number of tokens in a text file using the specified OpenAI model.

    Parameters:
    input_file: The file path to a text file.
    model: The model name for which to count tokens (default is 'gpt-4').

    Returns:
    The token count for the input file.
    """
    encoding = tiktoken.encoding_for_model(model)

    def read_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    content = read_file(input_file)
    token_count = len(encoding.encode(content))

    return token_count

def tokencount_text(text, model="gpt-4"):
    """
    Count the number of tokens in a given text string using the specified OpenAI model.

    Parameters:
    text: The input text string.
    model: The model name for which to count tokens (default is 'gpt-4').

    Returns:
    The token count for the input text.
    """
    encoding = tiktoken.encoding_for_model(model)
    token_count = len(encoding.encode(text))

    return token_count