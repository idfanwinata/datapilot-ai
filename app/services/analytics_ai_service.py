import json
import os
from google import genai


def analyze_analytics_with_ai(analysis: dict) -> dict:
    """Interpret computed analytics with Gemini; does not invent measurements."""
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY belum dikonfigurasi.")

    payload = {
        "total_cases": analysis.get("total_cases"),
        "top_error_code": analysis.get("top_error_code"),
        "top_error_frequency": analysis.get("top_error_frequency"),
        "error_summary": analysis.get("error_summary", [])[:10],
        "machine_summary": analysis.get("machine_summary", []),
        "monthly_summary": analysis.get("monthly_summary", []),
        "done_tickets": analysis.get("done_tickets"),
        "open_tickets": analysis.get("open_tickets"),
        "cancelled_tickets": analysis.get("cancelled_tickets"),
        "median_resolution_hours": analysis.get("median_resolution_hours"),
        "mean_resolution_hours": analysis.get("mean_resolution_hours"),
        "valid_resolution_rows": analysis.get("valid_resolution_rows"),
        "duration_summary": analysis.get("duration_summary", []),
        "data_quality": analysis.get("data_quality", {}),
    }

    prompt = f"""
Anda adalah data analyst untuk data tiket perawatan mesin cash processing,
termasuk Glory RBG-100. Analisis statistik berikut dan jawab dalam Bahasa Indonesia.

DATA STATISTIK:
{json.dumps(payload, ensure_ascii=False, indent=2, default=str)}

Kembalikan JSON valid dengan struktur:
{{
  "summary": "Ringkasan eksekutif 2-4 kalimat",
  "key_findings": ["Temuan berbasis angka"],
  "priority_actions": [
    {{
      "priority": "P1/P2/P3",
      "issue": "Kategori kendala",
      "evidence": "Frekuensi/persentase yang mendukung",
      "recommended_action": "Tindakan yang dapat dilakukan",
      "verification": "Data/pemeriksaan untuk memvalidasi"
    }}
  ],
  "trend_interpretation": "Interpretasi tren bulanan; sebutkan jika data belum cukup",
  "duration_interpretation": "Interpretasi median/rata-rata durasi; sebutkan jumlah sampel valid",
  "data_limitations": ["Keterbatasan data"]
}}

Aturan:
- Jangan mengarang angka, kode error, atau tren.
- Jangan menyatakan komponen pasti rusak; sebut kemungkinan penyebab sebagai hipotesis.
- Kendala berbasis kalimat bukan kode error resmi.
- Utamakan temuan dengan frekuensi terbesar dan Pareto.
- Rekomendasi harus dapat ditindaklanjuti dan perlu diverifikasi teknisi.
- Jika statistik tidak cukup untuk suatu kesimpulan, katakan belum cukup data.
"""
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        )
        if not response.text:
            raise RuntimeError("Gemini tidak mengembalikan hasil analisis.")
        result = json.loads(response.text)
        if not isinstance(result, dict):
            raise RuntimeError("Format respons AI bukan JSON object.")
        return result
    except Exception as exc:
        raise RuntimeError(f"Analisis Gemini gagal: {exc}") from exc
