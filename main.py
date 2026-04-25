from pathlib import Path
from ContainerChecker.cc_workflow import run_comparison


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent

    result = run_comparison(
        file_a=script_dir / "REEFERS EGPSD 27.03.2026.pdf",
        parser_a="MAX3",
        file_b=script_dir / "MSK_ReeferManifest_FinalChangesToLoadListDeadline_IB7612E612EEGPSDTM.pdf",
        parser_b="MSK",
        base_dir=script_dir,
    )

    summary = result["summary"]

    print("\nsummary:")
    print(f"Container in file A: {summary['count_a']}")
    print(f"Container in file B: {summary['count_b']}")
    print(f"Container in both files: {summary['count_both']}")
    print(f"only in A: {summary['only_a']}")
    print(f"only in B: {summary['only_b']}")
    print(f"differences: {summary['differences']}")
    print(f"result saved in: {summary['output_dir']}")