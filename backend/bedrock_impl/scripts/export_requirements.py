from pathlib import Path
from subprocess import run

output_path = Path(__file__).parent.parent / "src" / "bedrock_impl" / "requirements.txt"

def main():
    print(f"Exporting requirements to {output_path}...")
    run([
        "poetry",
        "export",
        "-f", "requirements.txt",
        "--without-hashes",
        f"--output={output_path}"
    ], check=True)
    print("Success")