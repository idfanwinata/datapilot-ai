
import logging

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from app.services.analytics_service import (
    load_failure_data,
    analyze_failures,
)

from app.services.analytics_ai_service import (
    analyze_analytics_with_ai,
)

from app.rag.rag_service import (
    index_knowledge_base,
    analyze_with_rag,
)

from app.services.llm_service import analyze_with_llm
from app.services.diagnostic_service import analyze_error

from app.services.history_service import (
    save_diagnosis,
    list_diagnoses,
    get_diagnosis,
)

from app.schemas.diagnostic import (
    DiagnosticRequest,
    DiagnosticResponse,
)


logger = logging.getLogger(__name__)

router = APIRouter()


# =========================================================
# HEALTH CHECK
# =========================================================

@router.get("/health")
def health_check():
    return {"status": "healthy"}


# =========================================================
# DIAGNOSIS STANDAR
# =========================================================

@router.post(
    "/diagnostics/analyze",
    response_model=DiagnosticResponse,
)
def analyze_diagnostic(request: DiagnosticRequest):
    return analyze_error(request)


# =========================================================
# DIAGNOSIS MENGGUNAKAN GEMINI AI
# =========================================================

@router.post(
    "/diagnostics/analyze-ai",
    response_model=DiagnosticResponse,
)
def analyze_diagnostic_with_ai(request: DiagnosticRequest):
    try:
        return analyze_with_llm(request)

    except RuntimeError as exc:
        logger.exception("Runtime error saat analisis Gemini")
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Error saat analisis Gemini")
        raise HTTPException(
            status_code=502,
            detail=(
                "Gagal mendapatkan analisis dari layanan AI. "
                "Periksa terminal Uvicorn."
            ),
        ) from exc


# =========================================================
# INDEX KNOWLEDGE BASE
# =========================================================

@router.post("/knowledge/index")
def index_documents():
    try:
        return index_knowledge_base()

    except RuntimeError as exc:
        logger.exception(
            "Runtime error saat indexing knowledge base"
        )
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected error saat indexing knowledge base"
        )
        raise HTTPException(
            status_code=500,
            detail=(
                "Gagal melakukan indexing knowledge base. "
                "Periksa terminal Uvicorn."
            ),
        ) from exc


# =========================================================
# DIAGNOSIS MENGGUNAKAN RAG + SIMPAN RIWAYAT
# =========================================================

@router.post("/diagnostics/analyze-rag")
def analyze_diagnostic_with_rag(request: DiagnosticRequest):
    logger.info("RAG STEP 1: Memulai diagnosis")

    try:
        logger.info("RAG STEP 2: Memanggil analyze_with_rag")

        result = analyze_with_rag(request)

        logger.info("RAG STEP 3: Menyimpan riwayat diagnosis")

        save_diagnosis(
            application=request.application,
            error_log=request.error_log,
            result=result,
        )

        logger.info(
            "RAG STEP 4: Diagnosis dan penyimpanan berhasil"
        )

        return result

    except HTTPException:
        raise

    except RuntimeError as exc:
        logger.exception("Runtime error saat diagnosis RAG")

        status_code = (
            400 if "kosong" in str(exc).lower() else 503
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("RAG FAILED: Error saat diagnosis RAG")

        err_text = str(exc)
        err_upper = err_text.upper()

        if "429" in err_text or "RESOURCE_EXHAUSTED" in err_upper:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Batas kuota Gemini API tercapai. "
                    "Silakan coba lagi nanti atau periksa API key "
                    "dan model yang digunakan."
                ),
            ) from exc

        if "503" in err_text or "UNAVAILABLE" in err_upper:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Layanan AI sedang sibuk. "
                    "Silakan coba beberapa saat lagi."
                ),
            ) from exc

        raise HTTPException(
            status_code=500,
            detail=f"Diagnosis RAG gagal: {err_text}",
        ) from exc


# =========================================================
# RIWAYAT DIAGNOSIS
# =========================================================

@router.get("/diagnostics/history")
def diagnosis_history(limit: int = 20):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit harus antara 1 dan 100.",
        )

    history = list_diagnoses(limit)

    return {
        "total": len(history),
        "history": history,
    }


# =========================================================
# DETAIL SATU RIWAYAT DIAGNOSIS
# =========================================================

@router.get("/diagnostics/history/{diagnosis_id}")
def diagnosis_history_detail(diagnosis_id: int):
    if diagnosis_id < 1:
        raise HTTPException(
            status_code=400,
            detail="ID diagnosis harus lebih besar dari 0.",
        )

    diagnosis = get_diagnosis(diagnosis_id)

    if diagnosis is None:
        raise HTTPException(
            status_code=404,
            detail="Riwayat diagnosis tidak ditemukan.",
        )

    return diagnosis


# =========================================================
# ANALYTICS DATA KERUSAKAN MESIN + GEMINI AI
# =========================================================

@router.post("/analytics/analyze")
async def analyze_machine_data(
    file: UploadFile = File(...),
    error_col: str = Form("Kendala"),
    machine_col: str = Form("Tipe"),
    date_col: str = Form("Date Start"),
):
    try:
        filename = file.filename or "upload.xlsx"
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="File yang diunggah kosong.",
            )

        # STEP 1: Membaca Excel atau CSV
        df = load_failure_data(
            content,
            filename,
        )

        # STEP 2: Menghitung statistik dengan Python
        analysis = analyze_failures(
            df=df,
            error_col=error_col.strip(),
            machine_col=machine_col.strip(),
            date_col=date_col.strip() or None,
            update_col="Update",
            start_date_col="Date Start",
            end_date_col="Date End",
            status_col="Status",
        )

        # STEP 3: Membuat insight otomatis dengan Gemini
        try:
            logger.info(
                "ANALYTICS AI: Memulai analisis Gemini"
            )

            ai_insight = analyze_analytics_with_ai(analysis)

            ai_status = "success"
            ai_error = None

            logger.info(
                "ANALYTICS AI: Analisis berhasil"
            )

        except Exception as exc:
            logger.exception(
                "ANALYTICS AI: Gagal menghasilkan insight"
            )

            # Hasil statistik tetap dikembalikan.
            ai_insight = None
            ai_status = "failed"
            ai_error = str(exc)

        # STEP 4: Mengirim hasil ke dashboard
        return {
            "message": "Analisis data selesai.",
            "filename": filename,
            "columns": df.columns.tolist(),
            "analysis": analysis,
            "ai_status": ai_status,
            "ai_insight": ai_insight,
            "ai_error": ai_error,
        }

    except HTTPException:
        raise

    except ValueError as exc:
        logger.exception(
            "Format atau data analytics tidak valid"
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Gagal menganalisis data kerusakan mesin"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Analisis gagal. Periksa terminal Uvicorn "
                "untuk melihat detail error."
            ),
        ) from exc

    finally:
        await file.close()
