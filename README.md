# Reasoning and Agents Notebooks

This repository contains notebooks and teaching materials for the EBU6505 Reasoning and Agents module.

## Getting Started

### Prerequisites

- Python 3.11
- Terminal/Command Prompt
- VS Code (recommended)

### Setting up the Virtual Environment with `uv`

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver that we'll use to create our virtual environment.

1. **Install `uv`** (if not already installed):
    ```bash
    # On macOS and Linux.
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

    ```bash
    # On Windows.
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

2. **Create a virtual environment (under the project directory)**:
    ```bash
    uv venv
    ```

3. **Activate the virtual environment**:
    - On Windows:
      ```bash
      .venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source .venv/bin/activate
      ```

4. **Install required packages**:
    ```bash
    uv sync
    ```

## Using the Notebooks

### Running Jupyter Notebooks

1. Activate your virtual environment (see above)
2. Use VS Code to open the project folder and open the notebooks. (Recommended)
3. Or, Navigate to the project folder, Launch Jupyter in the project folder:
    ```bash
    jupyter notebook
    ```
4. Select the notebook you want to open

### Running Slides

The presentation slides can be viewed in two ways:

1. **Double-click Method**: (Recommended)
    - Simply double-click on any slide file (`.slides.html`) in your file explorer
    - Your default browser will open the slides in presentation mode

2. **From Jupyter**:
    - Open the corresponding notebook in Jupyter
    - Select "File" > "Export Notebook As" > "Reveal.js Slides"
    - Open the generated HTML file

## Troubleshooting

If you encounter issues:

- Ensure your virtual environment is activated
- Use student forum or contact the lecturer.

## License

This material is provided for educational purposes as part of the EBU6505 module.