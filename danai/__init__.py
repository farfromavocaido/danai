import tiktoken
from .json_manager import check_for_update
from openai import OpenAI
import datetime
import os
import mimetypes
import pkgutil
import base64
import json
import inspect

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
    
    # Check if cached tokens are available
    if hasattr(response.usage, 'prompt_tokens_details') and hasattr(response.usage.prompt_tokens_details, 'cached_tokens'):
        cached_tokens = response.usage.prompt_tokens_details.cached_tokens
    else:
        cached_tokens = None

    if cached_tokens is not None:
        # Subtract cached tokens from the input tokens
        original_input_tokens = input_tokens
        input_tokens = input_tokens - cached_tokens
    else:
        original_input_tokens = input_tokens
        input_tokens = input_tokens

    # Determine the correct model for pricing
    if model_name in pricing_data['models']:
        model_pricing = pricing_data['models'][model_name]
    else:
        if model_name in pricing_data['mapping']:
            mapped_model = pricing_data['mapping'][model_name]
            model_pricing = pricing_data['models'][mapped_model]
        else:
            raise ValueError(f"Model {model_name} not found in pricing data and no mapping exists.")

    # Calculate costs for the selected model
    input_cost = model_pricing['standard']['input'] * (input_tokens / 1_000_000)
    original_input_cost = model_pricing['standard']['input'] * (original_input_tokens / 1_000_000)
    output_cost = model_pricing['standard']['output'] * (output_tokens / 1_000_000)
    if cached_tokens is not None:
        cached_tokens_cost = model_pricing['standard']['input'] * (cached_tokens / 1_000_000)
    total_cost = input_cost + output_cost
    total_cost_without_cache = original_input_cost + output_cost
    total_tokens = original_input_tokens + output_tokens
    cached_saving = original_input_cost - input_cost

    # Cached tokens string:
    if cached_tokens is not None:
        cached_tokens_str = f"""
        Cost with caching: ${original_input_cost:.4f} - ${cached_saving:.4f} = ${input_cost:.4f} (saved ${cached_tokens_cost:.4f})
        Total cost would have been ${total_cost_without_cache:.4f} without caching.
        """
    else:
        cached_tokens_str = ""

    # Base results string
    results = f"""
    Model used: {model_name}
    Tokens | In: {original_input_tokens} | Out: {output_tokens} | Total: {total_tokens}
    Cost | In: ${input_cost:.4f} | Out: ${output_cost:.4f}, Total: ${total_cost:.4f}
    {cached_tokens_str}
    """

    # Comparison with another model, if provided
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

        comparison = "cheaper" if cost_difference > 0 else "more expensive" if cost_difference < 0 else "the same price"

        # Add comparison information to the results string
        comparison_results = f"""
        {comparison_model} Comparison:
        Input: ${comparison_input_cost:.4f} | Out: ${comparison_output_cost:.4f}, Total: ${comparison_total_cost:.4f}
        Cost Difference: {comparison_model} would be ${abs(cost_difference):.4f} {comparison}
        """
        
        # Append comparison results to the main results string
        results += comparison_results

    return results

def tokencount_file(input_file, model="gpt-4o"):
    """
    Count the number of tokens in a text file using the specified OpenAI model.

    Parameters:
    input_file: The file path to a text file.
    model: The model name for which to count tokens (default is 'gpt-4o').

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


def tokencount_text(text, model="gpt-4o"):
    """
    Count the number of tokens in a given text string using the specified OpenAI model.

    Parameters:
    text: The input text string.
    model: The model name for which to count tokens (default is 'gpt-4o').

    Returns:
    The token count for the input text.
    """
    encoding = tiktoken.encoding_for_model(model)
    token_count = len(encoding.encode(text))

    return token_count

def quick_q(prompt,model="gpt-4o-mini"):

    client = OpenAI()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )

    return response

def quickprint(prompt,model="gpt-4o-mini"):

    response = quick_q(prompt,model=model)

    # set timestamp in yymmddHHMM format
    timestamp = datetime.datetime.now().strftime("%y%m%d%H%M")

    response_text = response.choices[0].message.content
    print(response_text)

    # Check if 'qq' directory exists, if not create it
    try:
        os.mkdir("qq")
    except FileExistsError:
        pass

    with open(f"qq/qq_{timestamp}.txt", "w") as f:
        f.write(response_text)
    
    cost = pricecheck(response)
    print(cost)

def printsetup():
    # Create 'summaries' directory if it doesn't exist
    try:
        os.mkdir("summaries")
    except FileExistsError:
        pass

    # Get the content of 'printer_template.py' from inside the package
    template = pkgutil.get_data(__name__, 'printer_template.py').decode('utf-8')

    # Write the content to 'summaries/printer.py'
    with open("summaries/printer.py", "w") as f:
        f.write(template)

    print("Setup complete. 'summaries/printer.py' created.")

# Function to print the directory contents while ignoring certain directories, files, extensions, and non-readable files
# Function to check if a file is binary or not
def is_binary_file(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        return True  # If we can't guess the type, assume it's binary
    return not mime_type.startswith('text')

# Function to print the directory contents while ignoring certain directories, files, extensions, and binary/non-readable files
def print_directory_contents(directory, output_dir, ignore_dirs, ignore_files, ignore_extensions):
    output_path = os.path.join(output_dir, 'summary.md')
    with open(output_path , 'w') as f:
        # Walk through the directory
        for root, dirs, files in os.walk(directory):
            # Modify dirs in-place to exclude ignored directories globally
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            # Loop through each file in the current directory
            for name in files:
                # Skip files in ignore_files list or those with ignored extensions
                if name in ignore_files or any(name.endswith(ext) for ext in ignore_extensions):
                    continue

                # Get the full file path
                file_path = os.path.join(root, name)

                # Skip binary files and non-readable files
                if is_binary_file(file_path) or not os.access(file_path, os.R_OK):
                    continue

                # Write the file name and its contents to summary.md
                f.write(f'## {file_path}\n\n```\n')
                with open(file_path, 'r') as file:
                    tokens = tokencount_file(file_path)
                    print(f'{tokens} tokens in {file_path}')
                    f.write(file.read())
                f.write('\n```\n')
    total_tokens = tokencount_file(output_path)
    print(f'Total tokens in directory: {total_tokens}')
        

        

def generate_directory_tree(directory, ignore_dirs, prefix="", is_last=True):
    tree = []
    
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        # Sort dirs and files for consistent output
        dirs[:] = sorted(dirs)
        file_count = len(files)
        dir_count = len(dirs)

        # Loop through each directory in the current level
        for i, d in enumerate(dirs):
            dir_path = os.path.join(root, d)
            is_last_dir = (i == dir_count - 1) and (file_count == 0)

            # Check if the directory is in the ignore list
            if d in ignore_dirs:
                # Include the directory in the tree but omit its contents
                tree.append(f'{prefix}{"└── " if is_last_dir else "├── "}{d}')
                tree.append(f'{prefix}    ├── //contents omitted//')
            else:
                # Include the directory and continue traversing
                tree.append(f'{prefix}{"└── " if is_last_dir else "├── "}{d}/')
                # Recurse into the directory
                tree += generate_directory_tree(os.path.join(root, d), ignore_dirs, prefix + ("    " if is_last_dir else "│   "), is_last_dir)

        # Loop through each file in the current directory
        sorted_files = sorted(files)
        for j, name in enumerate(sorted_files):
            is_last_file = (j == file_count - 1)
            tree.append(f'{prefix}{"└── " if is_last_file else "├── "}{name}')
        
        break  # Stop walking deeper into the directory (handle each directory individually in recursion)
    
    return tree

# Function to print the directory tree in standard format
def print_directory_tree(directory, output_dir, ignore_dirs):
    tree = generate_directory_tree(directory, ignore_dirs)
    with open(f'{output_dir}/tree.md', 'w') as f:
        f.write(f"{directory}/\n")
        f.write("\n".join(tree))
        f.write("\n")

def join_summaries(output_directory):
    with open(os.path.join(output_directory, "full_summary.md"), "a") as f:
        f.write("# Directory Tree\n\n")
        with open(os.path.join(output_directory, "tree.md")) as tree_file:
            f.write(tree_file.read())
        f.write("\n\n# Directory Contents\n\n")
        with open(os.path.join(output_directory, "summary.md")) as contents_file:
            f.write(contents_file.read())

def jsonsave(response, filename=None, directory="outputs", overwrite=False, pretty=True, price=True):
    """
    Parse the response and save it as a JSON file.

    Args:
        response: The response object containing the parsed content.
        filename (str): Optional. The filename to save the content. If not provided, a timestamped filename will be generated.
        directory (str): The directory to save the output files.
        overwrite (bool): Whether to overwrite the file if it exists. If False, a timestamp will be appended to avoid overwriting.
        pretty (bool): Whether to pretty-print the JSON content with indentation.
        price (bool): Whether to calculate and display the cost of the response.
    """

    # Extract parsed content and convert to JSON string
    if pretty:
        content = response.choices[0].message.parsed.model_dump_json(indent=4)  # Pretty print JSON with 4-space indentation
    else:
        content = response.choices[0].message.parsed.model_dump_json()  # Default compact JSON

    extension = ".json"

    # Generate filename if not provided
    if not filename:
        timecode = response.created
        timestamp = datetime.datetime.fromtimestamp(timecode).strftime('%y%m%d-%H%M')
        filename = f"output-{timestamp}{extension}"
    else:
        filename = f"{filename}{extension}"

    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Determine file path and handle file existence
    file_path = os.path.join(directory, filename)
    
    if not overwrite and os.path.exists(file_path):
        # Append current timestamp before the extension if file exists
        timestamp_now = datetime.datetime.now().strftime('%y%m%d-%H%M')
        filename_no_ext, _ = os.path.splitext(filename)
        filename = f"{filename_no_ext}-{timestamp_now}{extension}"
        file_path = os.path.join(directory, filename)

    # Write content to file
    try:
        with open(file_path, "w") as file:
            file.write(content)
        print(f"Content successfully written to {file_path}")
    except Exception as e:
        print(f"Failed to write content: {e}")

    if price:
        cost = pricecheck(response)
        print(cost)
    
    # Return the file path for further use
    return 


def oai_image(image_path):
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode('utf-8')
    
    if image_path.endswith('.png'):
        format = 'png'
    elif image_path.endswith('.jpg') or image_path.endswith('.jpeg'):
        format = 'jpeg'

    
    content = {
        'type': 'image_url',
        'image_url': {
            'url': f"data:image/{format};base64,{base64_image}"
        }
    }

    # convert content to json
    content = json.dumps(content)

    return content

def ainspect(obj, obj_name=None, show_type=True, indent_level=4):
    # Set the formatting template. You can adjust this as needed.
    # Options: 
    # format_str = "{name} = {value} ({type})" -> name = value (type)
    # format_str = "{value} | {name} ({type})" -> value | name (type)
    # format_str = "{name} ({type}): {value}" -> name (type): value
    format_str = "{name} || {type} || {value}" if show_type else "{name} || {value}"

    # Get the name of the variable if obj_name is not provided
    if obj_name is None:
        # Retrieve the variable name from the caller's local variables
        frame = inspect.currentframe().f_back
        obj_name = [name for name, val in frame.f_locals.items() if val is obj][0]

    # Define indentation for nested attributes
    indent = " " * indent_level

    # Check if the object has a __dict__ attribute to handle class instances
    if hasattr(obj, "__dict__"):
        # Iterate through the attributes in the object's __dict__
        for attr, value in obj.__dict__.items():
            # Get the type string based on show_type
            type_info = type(value).__name__ if show_type else ""

            # Prepare formatted string for the current line
            formatted_line = format_str.format(
                name=f"{obj_name}.{attr}",
                value=repr(value),
                type=type_info
            )
            
            # Print formatted line or go deeper for nested structures
            if hasattr(value, "__dict__") or isinstance(value, list):
                print(f"{indent}{formatted_line.split(' = ')[0]}:")  # Show attribute name only
                ainspect(value, f"{obj_name}.{attr}", show_type, indent_level + 1)
            else:
                print(f"{indent}{formatted_line}")
    
    # Check if the object is a list (for nested list attributes like choices)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            # Recursively call ainspect for each item in the list
            print(f"{indent}{obj_name}[{index}]:")
            ainspect(item, f"{obj_name}[{index}]", show_type, indent_level + 1)
    
    else:
        # For simple types, directly print them using format_str
        type_info = type(obj).__name__ if show_type else ""
        formatted_line = format_str.format(name=obj_name, value=repr(obj), type=type_info)
        print(f"{indent}{formatted_line}")
