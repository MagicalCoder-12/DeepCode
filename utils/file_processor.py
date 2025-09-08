"""
File processing utilities for handling paper files and related operations.
"""

import json
import os
import re
from typing import Dict, List, Optional, Union


class FileProcessor:
    """
    A class to handle file processing operations including path extraction and file reading.
    """

    @staticmethod
    def extract_file_path(file_info: Union[str, Dict]) -> Optional[str]:
        """
        Extract paper directory path from the input information.

        Args:
            file_info: Either a JSON string or a dictionary containing file information

        Returns:
            Optional[str]: The extracted paper directory path or None if not found
        """
        try:
            # Handle direct file path input
            if isinstance(file_info, str):
                # Check if it's a file path (existing or not)
                if file_info.endswith(
                    (".md", ".pdf", ".txt", ".docx", ".doc", ".html", ".htm")
                ):
                    # It's a file path, return the directory
                    return os.path.dirname(os.path.abspath(file_info))
                elif os.path.exists(file_info):
                    if os.path.isfile(file_info):
                        return os.path.dirname(os.path.abspath(file_info))
                    elif os.path.isdir(file_info):
                        return os.path.abspath(file_info)

                # Try to parse as JSON
                try:
                    info_dict = json.loads(file_info)
                except json.JSONDecodeError:
                    # Try to extract JSON from text
                    info_dict = FileProcessor.extract_json_from_text(file_info)
                    if not info_dict:
                        # If not JSON and doesn't look like a file path, raise error
                        raise ValueError(
                            f"Input is neither a valid file path nor JSON: {file_info}"
                        )
            else:
                info_dict = file_info

            # Extract paper path from dictionary
            paper_path = info_dict.get("paper_path")
            if not paper_path:
                raise ValueError("No paper_path found in input dictionary")

            # Get the directory path instead of the file path
            paper_dir = os.path.dirname(paper_path)

            # Convert to absolute path if relative
            if not os.path.isabs(paper_dir):
                paper_dir = os.path.abspath(paper_dir)

            return paper_dir

        except (AttributeError, TypeError) as e:
            raise ValueError(f"Invalid input format: {str(e)}")

    @staticmethod
    def find_markdown_file(directory: str) -> Optional[str]:
        """
        Find the first markdown file in the given directory.

        Args:
            directory: Directory path to search

        Returns:
            Optional[str]: Path to the markdown file or None if not found
        """
        if not os.path.isdir(directory):
            return None

        for file in os.listdir(directory):
            if file.endswith(".md"):
                return os.path.join(directory, file)
        return None

    @staticmethod
    def parse_markdown_sections(content: str) -> List[Dict[str, Union[str, int, List]]]:
        """
        Parse markdown content and organize it by sections based on headers.

        Args:
            content: The markdown content to parse

        Returns:
            List[Dict]: A list of sections, each containing:
                - level: The header level (1-6)
                - title: The section title
                - content: The section content
                - subsections: List of subsections
        """
        # Split content into lines
        lines = content.split("\n")
        sections = []
        current_section = None
        current_content = []

        for line in lines:
            # Check if line is a header
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)

            if header_match:
                # If we were building a section, save its content
                if current_section is not None:
                    current_section["content"] = "\n".join(current_content).strip()
                    sections.append(current_section)

                # Start a new section
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = {
                    "level": level,
                    "title": title,
                    "content": "",
                    "subsections": [],
                }
                current_content = []
            elif current_section is not None:
                current_content.append(line)

        # Don't forget to save the last section
        if current_section is not None:
            current_section["content"] = "\n".join(current_content).strip()
            sections.append(current_section)

        return FileProcessor._organize_sections(sections)

    @staticmethod
    def _organize_sections(sections: List[Dict]) -> List[Dict]:
        """
        Organize sections into a hierarchical structure based on their levels.

        Args:
            sections: List of sections with their levels

        Returns:
            List[Dict]: Organized hierarchical structure of sections
        """
        result = []
        section_stack = []

        for section in sections:
            while section_stack and section_stack[-1]["level"] >= section["level"]:
                section_stack.pop()

            if section_stack:
                section_stack[-1]["subsections"].append(section)
            else:
                result.append(section)

            section_stack.append(section)

        return result

    @staticmethod
    async def read_file_content(file_path: str) -> str:
        """
        Read the content of a file asynchronously with automatic encoding detection.

        Args:
            file_path: Path to the file to read

        Returns:
            str: The content of the file

        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
        """
        try:
            # Ensure the file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Check if the file is actually a PDF (regardless of extension)
            with open(file_path, "rb") as f:
                header = f.read(10)
                if header.startswith(b'%PDF'):
                    print(f"🔍 Detected PDF file disguised as {os.path.splitext(file_path)[1]}: {file_path}")
                    # Return a helpful markdown content explaining the situation
                    file_size = os.path.getsize(file_path)
                    return f"""# PDF Document Detected

**File**: {os.path.basename(file_path)}
**Size**: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)
**Type**: PDF Document

## Issue
This file is a PDF document that was incorrectly saved with a .md extension.

## Solutions
1. **Rename the file**: Change the extension from .md to .pdf
2. **Use a PDF reader**: Open the file with a PDF viewer
3. **Convert to text**: Use a PDF-to-text converter

## For DeepCode Processing
To process this PDF with DeepCode:
1. Rename the file to have a .pdf extension
2. Upload it again - DeepCode will automatically extract and convert the content

---
*Auto-detected by DeepCode Encoding System*
*Respecting your local development privacy preferences*
"""

            # Try to detect encoding first
            detected_encoding = None
            try:
                import chardet
                with open(file_path, "rb") as f:
                    raw_data = f.read(10000)  # Read first 10KB for detection
                    result = chardet.detect(raw_data)
                    detected_encoding = result.get('encoding')
                    confidence = result.get('confidence', 0)
                    
                    # Only use detected encoding if confidence is high enough
                    if confidence < 0.7:
                        detected_encoding = None
            except ImportError:
                # chardet not available, will use fallback method
                pass
            except Exception:
                # Detection failed, will use fallback method
                detected_encoding = None

            # List of encodings to try in order
            encodings_to_try = []
            if detected_encoding:
                encodings_to_try.append(detected_encoding)
            
            # Add common encodings as fallbacks
            encodings_to_try.extend([
                'utf-8',
                'utf-8-sig',  # UTF-8 with BOM
                'latin1',     # ISO-8859-1
                'cp1252',     # Windows-1252
                'ascii',
                'utf-16',
                'utf-32'
            ])
            
            # Remove duplicates while preserving order
            seen = set()
            unique_encodings = []
            for enc in encodings_to_try:
                if enc and enc.lower() not in seen:
                    unique_encodings.append(enc)
                    seen.add(enc.lower())

            # Try each encoding until one works
            last_error = None
            for encoding in unique_encodings:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        content = f.read()
                    
                    # Successful read
                    if detected_encoding and encoding != detected_encoding:
                        print(f"Note: File {file_path} read with {encoding} encoding (detected: {detected_encoding})")
                    
                    return content
                    
                except UnicodeDecodeError as e:
                    last_error = e
                    continue
                except Exception as e:
                    last_error = e
                    continue
            
            # If all encodings failed, try reading as binary and handling errors
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                print(f"Warning: File {file_path} contains invalid UTF-8 characters, some may be replaced with �")
                return content
            except Exception as e:
                raise IOError(f"Error reading file {file_path}: Could not decode with any encoding. Last error: {str(last_error)}")

        except Exception as e:
            if isinstance(e, (FileNotFoundError, IOError)):
                raise
            raise IOError(f"Error reading file {file_path}: {str(e)}")

    @staticmethod
    def format_section_content(section: Dict) -> str:
        """
        Format a section's content with standardized spacing and structure.

        Args:
            section: Dictionary containing section information

        Returns:
            str: Formatted section content
        """
        # Start with section title
        formatted = f"\n{'#' * section['level']} {section['title']}\n"

        # Add section content if it exists
        if section["content"]:
            formatted += f"\n{section['content'].strip()}\n"

        # Process subsections
        if section["subsections"]:
            # Add a separator before subsections if there's content
            if section["content"]:
                formatted += "\n---\n"

            # Process each subsection
            for subsection in section["subsections"]:
                formatted += FileProcessor.format_section_content(subsection)

        # Add section separator
        formatted += "\n" + "=" * 80 + "\n"

        return formatted

    @staticmethod
    def standardize_output(sections: List[Dict]) -> str:
        """
        Convert structured sections into a standardized string format.

        Args:
            sections: List of section dictionaries

        Returns:
            str: Standardized string output
        """
        output = []

        # Process each top-level section
        for section in sections:
            output.append(FileProcessor.format_section_content(section))

        # Join all sections with clear separation
        return "\n".join(output)

    @classmethod
    async def process_file_input(
        cls, file_input: Union[str, Dict], base_dir: str = None
    ) -> Dict:
        """
        Process file input information and return the structured content.

        Args:
            file_input: File input information (JSON string, dict, or direct file path)
            base_dir: Optional base directory to use for creating paper directories (for sync support)

        Returns:
            Dict: The structured content with sections and standardized text
        """
        try:
            # First try to extract markdown file path from string
            if isinstance(file_input, str):
                import re

                file_path_match = re.search(r"`([^`]+\.md)`", file_input)
                if file_path_match:
                    paper_path = file_path_match.group(1)
                    file_input = {"paper_path": paper_path}

            # Extract paper directory path
            paper_dir = cls.extract_file_path(file_input)

            # If base_dir is provided, adjust paper_dir to be relative to base_dir
            if base_dir and paper_dir:
                # If paper_dir is using default location, move it to base_dir
                if paper_dir.endswith(("deepcode_lab", "agent_folders")):
                    paper_dir = base_dir
                else:
                    # Extract the relative part and combine with base_dir
                    paper_name = os.path.basename(paper_dir)
                    # Keep original directory name unchanged, no replacements
                    paper_dir = os.path.join(base_dir, "papers", paper_name)

                # Ensure the directory exists
                os.makedirs(paper_dir, exist_ok=True)

            if not paper_dir:
                raise ValueError("Could not determine paper directory path")

            # Get the actual file path
            file_path = None
            if isinstance(file_input, str):
                # Try to parse as JSON (handle download results)
                try:
                    parsed_json = json.loads(file_input)
                    if isinstance(parsed_json, dict) and "paper_path" in parsed_json:
                        file_path = parsed_json.get("paper_path")
                        # If file doesn't exist, try to find markdown file
                        if file_path and not os.path.exists(file_path):
                            paper_dir = os.path.dirname(file_path)
                            if os.path.isdir(paper_dir):
                                file_path = cls.find_markdown_file(paper_dir)
                                if not file_path:
                                    raise ValueError(
                                        f"No markdown file found in directory: {paper_dir}"
                                    )
                    else:
                        raise ValueError("Invalid JSON format: missing paper_path")
                except json.JSONDecodeError:
                    # Try to extract JSON from text (handle download results with extra text)
                    extracted_json = cls.extract_json_from_text(file_input)
                    if extracted_json and "paper_path" in extracted_json:
                        file_path = extracted_json.get("paper_path")
                        # If file doesn't exist, try to find markdown file
                        if file_path and not os.path.exists(file_path):
                            paper_dir = os.path.dirname(file_path)
                            if os.path.isdir(paper_dir):
                                file_path = cls.find_markdown_file(paper_dir)
                                if not file_path:
                                    raise ValueError(
                                        f"No markdown file found in directory: {paper_dir}"
                                    )
                    else:
                        # Not JSON, handle as file path
                        # Check if it's a file path (existing or not)
                        if file_input.endswith(
                            (".md", ".pdf", ".txt", ".docx", ".doc", ".html", ".htm")
                        ):
                            if os.path.exists(file_input):
                                file_path = file_input
                            else:
                                # File doesn't exist, try to find markdown in the directory
                                file_path = cls.find_markdown_file(paper_dir)
                                if not file_path:
                                    raise ValueError(
                                        f"No markdown file found in directory: {paper_dir}"
                                    )
                        elif os.path.exists(file_input):
                            if os.path.isfile(file_input):
                                file_path = file_input
                            elif os.path.isdir(file_input):
                                # If it's a directory, find the markdown file
                                file_path = cls.find_markdown_file(file_input)
                                if not file_path:
                                    raise ValueError(
                                        f"No markdown file found in directory: {file_input}"
                                    )
                        else:
                            raise ValueError(f"Invalid input: {file_input}")
            else:
                # Dictionary input
                file_path = file_input.get("paper_path")
                # If the file doesn't exist, try to find markdown in the directory
                if file_path and not os.path.exists(file_path):
                    paper_dir = os.path.dirname(file_path)
                    if os.path.isdir(paper_dir):
                        file_path = cls.find_markdown_file(paper_dir)
                        if not file_path:
                            raise ValueError(
                                f"No markdown file found in directory: {paper_dir}"
                            )

            if not file_path:
                raise ValueError("No valid file path found")

            # Read file content
            content = await cls.read_file_content(file_path)

            # Parse and structure the content
            structured_content = cls.parse_markdown_sections(content)

            # Generate standardized text output
            standardized_text = cls.standardize_output(structured_content)

            return {
                "paper_dir": paper_dir,
                "file_path": file_path,
                "sections": structured_content,
                "standardized_text": standardized_text,
            }

        except Exception as e:
            raise ValueError(f"Error processing file input: {str(e)}")

    @staticmethod
    def extract_json_from_text(text: str) -> Optional[Dict]:
        """
        Extract JSON from text that may contain markdown code blocks or other content.

        Args:
            text: Text that may contain JSON

        Returns:
            Optional[Dict]: Extracted JSON as dictionary or None if not found
        """
        import re

        # Try to find JSON in markdown code blocks
        json_pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find standalone JSON
        json_pattern = r"(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})"
        matches = re.findall(json_pattern, text, re.DOTALL)
        for match in matches:
            try:
                parsed = json.loads(match)
                if isinstance(parsed, dict) and "paper_path" in parsed:
                    return parsed
            except json.JSONDecodeError:
                continue

        return None
