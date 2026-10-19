from io import BytesIO, StringIO
import re
import pandas as pd

# Extract common machine error-code formats from the free-text Kendala/Update fields.
_ERROR_PATTERNS = [
    re.compile(r"\bE\.?[A-Z]?\s*\d{2,5}\b", re.IGNORECASE),
    re.compile(r"\b0x[0-9A-F]{3,8}\b", re.IGNORECASE),
    re.compile(r"\b(?:error|err)\s*(?:code)?\s*[:#-]?\s*\d{1,5}(?:\s*[+/-]\s*[A-F0-9]{1,5})?\b", re.IGNORECASE),
    re.compile(r"\b[A-F]\d{2,4}\b", re.IGNORECASE),
]


def load_failure_data(file_content: bytes, filename: str) -> pd.DataFrame:
    """Load Excel/CSV and normalize common header formatting issues."""
    filename = (filename or "").lower().strip()
    if not file_content:
        raise ValueError("File yang diunggah kosong.")

    try:
        if filename.endswith(".csv"):
            # sep=None uses the Python engine to infer comma, semicolon, or tab.
            try:
                df = pd.read_csv(
                    BytesIO(file_content),
                    sep=None,
                    engine="python",
                    encoding="utf-8-sig",
                )
            except UnicodeDecodeError:
                df = pd.read_csv(
                    BytesIO(file_content),
                    sep=None,
                    engine="python",
                    encoding="latin-1",
                )
        elif filename.endswith(".xlsx"):
            # First sheet is the default; for the known RBG recap, try Sheet7 if present.
            workbook = pd.ExcelFile(BytesIO(file_content), engine="openpyxl")
            sheet = "Sheet7" if "Sheet7" in workbook.sheet_names else workbook.sheet_names[0]
            df = pd.read_excel(workbook, sheet_name=sheet)
        elif filename.endswith(".xls"):
            df = pd.read_excel(BytesIO(file_content))
        else:
            raise ValueError("Format file harus CSV, XLSX, atau XLS.")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Gagal membaca file: {exc}") from exc

    if df.empty:
        raise ValueError("File tidak memiliki data.")

    # Strip BOM, spaces and wrapping quotes from headers.
    cleaned = []
    for col in df.columns:
        name = str(col).replace("\ufeff", "").strip().strip('"').strip("'").strip()
        cleaned.append(name)
    df.columns = cleaned

    # If CSV was imported as one column, retry common delimiters.
    if len(df.columns) == 1 and filename.endswith(".csv"):
        raw = file_content.decode("utf-8-sig", errors="replace")
        for delimiter in (";", "\t", "|"):
            if delimiter in raw.splitlines()[0]:
                candidate = pd.read_csv(
                    StringIO(raw),
                    sep=delimiter,
                    engine="python",
                )
                if len(candidate.columns) > 1:
                    candidate.columns = [
                        str(c).replace("\ufeff", "").strip().strip('"').strip("'").strip()
                        for c in candidate.columns
                    ]
                    df = candidate
                    break

    if len(set(df.columns)) != len(df.columns):
        raise ValueError("Nama kolom duplikat setelah spasi dibersihkan.")
    return df


def _parse_source_dates(series: pd.Series) -> pd.Series:
    # Supports source strings like '02-01-2026 / 10:52' and Excel datetime cells.
    try:
        return pd.to_datetime(series, errors="coerce", dayfirst=True, format="mixed")
    except TypeError:  # Compatibility with older pandas versions.
        return pd.to_datetime(series, errors="coerce", dayfirst=True)


def _normalize_code(value: str) -> str:
    value = re.sub(r"\s+", "", value.upper())
    value = value.replace("E.", "E")
    return value


def _classify_text(text: str) -> str:
    t = text.casefold()
    rules = [
        ("Jammed / uang tersangkut", ("jammed", "ngejam", "tersangkut", "uang tidak berjalan", "uang nyangkut")),
        ("Kaset / cassette / hopper / stacker", ("kaset", "cassette", "hopper", "stacker", "bin")),
        ("Sensor / mekanik / cleaning", ("sensor", "cleaning", "clean", "mekanik", "transport", "roller")),
        ("Koneksi / LAN / komunikasi", ("koneksi", "communication", "komunikasi", "lan", "jaringan", "tidak konek")),
        ("Pintu / cover / kunci", ("pintu", "cover", "kunci", "door")),
        ("Tablet / PC / AIO", ("tablet", "pc aio", "aio", "pc tidak", "komputer")),
        ("Power / listrik", ("power", "listrik", "mati total", "tidak bisa dinyalakan")),
    ]
    for label, keywords in rules:
        if any(keyword in t for keyword in keywords):
            return label
    return "Kendala lain / belum terklasifikasi"


def _extract_error_labels(row: pd.Series, error_col: str, update_col: str) -> list[str]:
    chunks = []
    for col in (error_col, update_col):
        if col in row.index and pd.notna(row[col]):
            chunks.append(str(row[col]))
    text = "\n".join(chunks)
    found = []
    for pattern in _ERROR_PATTERNS:
        for match in pattern.findall(text):
            code = _normalize_code(match)
            # Drop generic fragments accidentally caught inside hexadecimal-like values.
            if len(code) >= 3 and code not in found:
                found.append(code)
    return found or [_classify_text(text)]


def analyze_failures(
    df: pd.DataFrame,
    error_col: str = "Kendala",
    machine_col: str = "Tipe",
    date_col: str | None = "Date Start",
    status_col: str = "Status",
    start_date_col: str = "Date Start",
    end_date_col: str = "Date End",
    update_col: str = "Update",
) -> dict:
    required_columns = [error_col, machine_col]
    if date_col:
        required_columns.append(date_col)
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Kolom tidak ditemukan: {', '.join(missing)}")

    data = df.copy()
    data[error_col] = data[error_col].astype("string").str.strip()
    # Include rows where either the initial complaint or service update exists.
    valid_error = data[error_col].notna() & data[error_col].ne("")
    if update_col in data.columns:
        update_values = data[update_col].astype("string").str.strip()
        valid_update = update_values.notna() & update_values.ne("")
        valid_error = valid_error | valid_update
    data = data.loc[valid_error].copy()
    if data.empty:
        raise ValueError("Tidak ditemukan data pada kolom Kendala atau Update.")

    # Count each ticket once per distinct error/theme. Prefer explicit codes when present;
    # otherwise classify the complaint text. Update is only a fallback when complaint is blank,
    # avoiding inflated counts from repeated technician notes.
    labels_per_row = []
    for _, row in data.iterrows():
        complaint = str(row.get(error_col, "") or "")
        update_text = str(row.get(update_col, "") or "") if update_col in data.columns else ""
        complaint_labels = _extract_error_labels(
            pd.Series({error_col: complaint, update_col: ""}),
            error_col,
            update_col,
        )
        if not complaint.strip() or complaint.casefold() in ("nan", "<na>"):
            complaint_labels = _extract_error_labels(
                pd.Series({error_col: "", update_col: update_text}),
                error_col,
                update_col,
            )
        labels_per_row.append(list(dict.fromkeys(complaint_labels)))

    expanded = pd.DataFrame({
        "error_code": [label for labels in labels_per_row for label in labels]
    })
    error_summary = (
        expanded["error_code"].value_counts()
        .rename_axis("error_code")
        .reset_index(name="frequency")
    )
    total_label_mentions = int(error_summary["frequency"].sum())
    error_summary["percentage"] = (
        error_summary["frequency"] / total_label_mentions * 100
    ).round(2)
    error_summary["cumulative_percentage"] = (
        error_summary["frequency"].cumsum() / total_label_mentions * 100
    ).round(2)
    error_summary.insert(0, "rank", range(1, len(error_summary) + 1))

    machine_summary = (
        data[machine_col].fillna("Tidak diketahui").astype(str).str.strip()
        .replace("", "Tidak diketahui").value_counts()
        .rename_axis("machine_model").reset_index(name="frequency")
    )

    result = {
        "total_cases": int(len(data)),
        "unique_error_codes": int(error_summary["error_code"].nunique()),
        "unique_machine_models": int(data[machine_col].dropna().astype(str).nunique()),
        "top_error_code": str(error_summary.iloc[0]["error_code"]) if not error_summary.empty else "-",
        "top_error_frequency": int(error_summary.iloc[0]["frequency"]) if not error_summary.empty else 0,
        "error_summary": error_summary.to_dict(orient="records"),
        "machine_summary": machine_summary.to_dict(orient="records"),
        "error_count_basis": f"Kode error diekstrak dari kolom {error_col}" + (f" + {update_col}" if update_col in data.columns else "") + "; jika tidak ditemukan, baris dikelompokkan menurut tema kendala.",
    }

    if status_col in data.columns:
        status = data[status_col].fillna("").astype(str).str.strip()
        normalized = status.str.casefold()
        done_mask = normalized.eq("done")
        cancelled_mask = normalized.eq("cancelled")
        open_mask = normalized.isin(["pending progress", "on progress", "dispatched"])
        result["done_tickets"] = int(done_mask.sum())
        result["open_tickets"] = int(open_mask.sum())
        result["cancelled_tickets"] = int(cancelled_mask.sum())
    else:
        result["done_tickets"] = None
        result["open_tickets"] = None
        result["cancelled_tickets"] = None

    if start_date_col in data.columns and end_date_col in data.columns:
        starts = _parse_source_dates(data[start_date_col])
        ends = _parse_source_dates(data[end_date_col])
        hours = (ends - starts).dt.total_seconds() / 3600
        valid_hours = hours[(hours >= 0) & (hours <= 30 * 24)]
        result["median_resolution_hours"] = round(float(valid_hours.median()), 2) if not valid_hours.empty else None
        result["mean_resolution_hours"] = round(float(valid_hours.mean()), 2) if not valid_hours.empty else None
        result["valid_resolution_rows"] = int(valid_hours.count())
        result["duration_under_1_hour"] = int((valid_hours < 1).sum())
        result["duration_1_to_4_hours"] = int(((valid_hours >= 1) & (valid_hours < 4)).sum())
        result["duration_4_to_8_hours"] = int(((valid_hours >= 4) & (valid_hours < 8)).sum())
        result["duration_over_8_hours"] = int((valid_hours >= 8).sum())
    else:
        result["median_resolution_hours"] = None
        result["mean_resolution_hours"] = None
        result["valid_resolution_rows"] = 0

    if date_col and date_col in data.columns:
        parsed_dates = _parse_source_dates(data[date_col])
        dated = data.loc[parsed_dates.notna()].copy()
        dated["_date"] = parsed_dates.loc[parsed_dates.notna()]
        monthly = dated.assign(period=dated["_date"].dt.to_period("M").astype(str)).groupby("period").size().reset_index(name="frequency")
        result["monthly_summary"] = monthly.to_dict(orient="records")
        result["valid_date_rows"] = int(len(dated))
    else:
        result["monthly_summary"] = []
        result["valid_date_rows"] = 0

    duration_rows = [
        {"period": "< 1 jam", "frequency": result.get("duration_under_1_hour", 0)},
        {"period": "1–4 jam", "frequency": result.get("duration_1_to_4_hours", 0)},
        {"period": "4–8 jam", "frequency": result.get("duration_4_to_8_hours", 0)},
        {"period": ">= 8 jam", "frequency": result.get("duration_over_8_hours", 0)},
    ]
    result["duration_summary"] = duration_rows
    result["data_quality"] = {
        "source_rows": int(len(df)),
        "analyzed_rows": int(len(data)),
        "excluded_rows": int(len(df) - len(data)),
        "error_label_mentions": int(total_label_mentions),
        "valid_date_rows": int(result.get("valid_date_rows", 0)),
        "valid_resolution_rows": int(result.get("valid_resolution_rows", 0)),
    }
    result["analysis_notes"] = [
        "Frekuensi dihitung per tiket untuk kategori kendala yang teridentifikasi.",
        "Persentase menggunakan total label kendala yang dianalisis sebagai denominator.",
        "Tema kendala berbasis teks adalah klasifikasi awal, bukan kode error resmi.",
    ]
    return result
