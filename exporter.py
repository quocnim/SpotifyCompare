from pathlib import Path
from comparator import results_to_dataframes

def export_excel(results, path):
    dataframes = results_to_dataframes(results)

    with __import__("pandas").ExcelWriter(path, engine="openpyxl") as writer:
        for sheet, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet[:31], index=False)

def export_csv_bundle(results, folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)

    for sheet, df in results_to_dataframes(results).items():
        filename = (
            sheet.lower()
            .replace(" ", "_")
            .replace("/", "_")
        )
        df.to_csv(folder / f"{filename}.csv", index=False)
