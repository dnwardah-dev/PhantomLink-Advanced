from datetime import datetime, timezone


def build_investigation_report(url: str, analysis: dict) -> dict:
    score = analysis.get("risk_score")
    level = analysis.get("risk_level", "UNASSESSED")

    explanations = {
        "HIGH": "URL memiliki beberapa indikator mencurigakan. Hindari memasukkan informasi pribadi sebelum melakukan verifikasi.",
        "MEDIUM": "URL memiliki sejumlah indikator risiko yang perlu diperiksa lebih lanjut.",
        "LOW": "Tidak banyak indikator mencurigakan ditemukan melalui analisis awal. Ini bukan jaminan bahwa website aman.",
        "UNASSESSED": "URL tidak dapat dinilai karena tidak lolos validasi awal."
    }

    recommendations = {
        "HIGH": "Jangan memasukkan password, OTP, atau informasi rekening.",
        "MEDIUM": "Verifikasi alamat website melalui sumber resmi.",
        "LOW": "Tetap periksa identitas website sebelum membagikan informasi.",
        "UNASSESSED": "Periksa kembali URL yang dimasukkan."
    }

    return {
        "investigation": {
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_type": "offline_heuristic"
        },
        "risk_assessment": {
            "score": score,
            "level": level,
            "summary": explanations.get(level, explanations["UNASSESSED"])
        },
        "evidence": analysis.get("indicators", []),
        "recommendation": recommendations.get(
            level, recommendations["UNASSESSED"]
        ),
        "disclaimer": "Hasil ini merupakan analisis heuristik awal, bukan keputusan pasti bahwa website aman atau berbahaya."
    }
