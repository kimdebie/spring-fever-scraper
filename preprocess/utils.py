import os
import zipfile
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
from striprtf.striprtf import rtf_to_text


def read_from_csv(filename: os.PathLike) -> pd.DataFrame:
    return pd.read_csv(filename).astype('str')


def read_from_zip(zip_file_path: os.PathLike) -> pd.DataFrame:
    zip_path = Path(zip_file_path)
    output_dir = zip_path.parent / zip_path.stem
    os.makedirs(output_dir, exist_ok=True)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

    parsed_rtfs = []
    rtf_files = [f for f in os.listdir(output_dir)
                 if f.endswith('.rtf')]
    for file in rtf_files:
        with open(output_dir / file, 'r') as rtf_file:
            rtf_content = rtf_file.read()
            try:
                text = rtf_to_text(rtf_content)
            except Exception as e:
                print(f"Error extracting text from {file}: {e}")
                continue
            parsed_rtfs.append(parse_rtf(text))

    return pd.DataFrame(parsed_rtfs)


def parse_rtf(
        rtf_text: str,
        start_text: Optional[str] = 'Body',
        end_text: Optional[str] = 'Classification'
) -> Dict[str, str]:
    text_split = [text.strip() for text in rtf_text.split("\n") if text]
    title = text_split[0]
    source = text_split[1]
    date = text_split[2]

    content_start = text_split.index(start_text) + 1 if start_text in text_split else 0
    content_end = text_split.index(end_text) if end_text in text_split else len(text_split)

    text = " ".join(text_split[content_start:content_end])

    return {
        'title': title,
        'source': source,
        'date': date,
        'text': text
    }
