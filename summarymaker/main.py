# danai/summarymaker/main.py
"""
Entry point for the summarymaker functionality.
"""

from .config import SummaryConfig
from .filtering.filters import collect_included_files
from .output.tree_generator import TreeGenerator
from .output.summary_generator import SummaryGenerator
from .tcounter import tokencount_text

def generate_summary(config: SummaryConfig) -> None:
    """
    Orchestrates the entire process of:
      1. Determining which files to include or ignore.
      2. Processing files via any configured processors.
      3. Generating a directory tree output.
      4. Generating a combined summary of included file contents.
    
    :param config: A SummaryConfig object with user-defined or default rules.
    """
    # 1. Collect files based on filtering rules
    included_files = collect_included_files(config)

    pre_processed_tokens = 0
    post_processed_tokens = 0


    # 2. Apply all processors in sequence
    for fileinfo in included_files:
        with open(fileinfo.path, "r", encoding="utf-8") as f:
            content = f.read()
            pre_tokens = tokencount_text(content)
            pre_processed_tokens += pre_tokens

        for processor in config.processors:
            content = processor.process(content, fileinfo.path)
            post_tokens = tokencount_text(content)
            post_processed_tokens += post_tokens

        fileinfo.processed_content = content
        if pre_tokens > post_tokens:
            custstring = f"REDUCTION: {pre_tokens - post_tokens}"
            print(f"{post_tokens} in {fileinfo.path} – pre: {pre_tokens}, post: {post_tokens} | {custstring}")
        elif pre_tokens == post_tokens:
            custstring = "N/A"
            print(f"{post_tokens} in {fileinfo.path}")
        else:
            custstring = f"INCREASE: {post_tokens - pre_tokens}"
            print(f"{post_tokens} in {fileinfo.path} – pre: {pre_tokens}, post: {post_tokens} | {custstring}")

        

    print("------")
    print(f"Pre-processed tokens: {post_processed_tokens}")
    print(f"Post-processed tokens: {pre_processed_tokens}")
    print("------")
    print(f"Token reduction: {post_processed_tokens - pre_processed_tokens}")
    
    # 3. Generate and save the directory tree (if enabled)


    if config.generate_tree:
        TreeGenerator.generate(config, included_files)

    # 4. Generate the summary of included file contents (if enabled)
    if config.generate_summarydoc:
        SummaryGenerator.generate(config, included_files)