
from app.schemas.diagnostic import (
    DiagnosticRequest,
    DiagnosticResponse,
)


def analyze_error(
    request: DiagnosticRequest,
) -> DiagnosticResponse:
    error_log = request.error_log.lower()

    if "connection refused" in error_log:
        cause = (
            "Service tujuan mungkin tidak aktif, "
            "atau koneksi ke port tujuan ditolak."
        )
        steps = [
            "Periksa status service tujuan.",
            "Periksa host dan port pada konfigurasi aplikasi.",
            "Periksa konektivitas jaringan dan firewall.",
        ]

    elif "timeout" in error_log:
        cause = (
            "Permintaan mungkin melebihi batas waktu "
            "akibat service lambat atau gangguan jaringan."
        )
        steps = [
            "Periksa durasi respons service tujuan.",
            "Periksa konektivitas jaringan.",
            "Periksa konfigurasi timeout aplikasi.",
        ]

    else:
        cause = (
            "Penyebab belum dapat ditentukan dari "
            "aturan analisis sederhana."
        )
        steps = [
            "Periksa log sebelum dan sesudah error.",
            "Identifikasi komponen yang mengalami gangguan.",
            "Bandingkan dengan dokumentasi troubleshooting.",
        ]

    return DiagnosticResponse(
        application=request.application,
        error_summary="Log error diterima untuk dianalisis.",
        possible_cause=cause,
        recommended_steps=steps,
        analysis_type="mock",
    )
