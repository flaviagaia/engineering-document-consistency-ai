from __future__ import annotations

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .config import CONTRACTS_DIR


DOCUMENTS = {
    "baseline_scope_contract.pdf": [
        "1.1 - The contractor shall deliver the 3D model revision within 10 calendar days after kickoff.",
        "1.2 - Quality verification shall be performed by the contractor before submission.",
        "1.3 - Measurement shall be based on approved isometric sheets.",
        "2.1 - Valve tagging shall follow the project coding standard ENG-VAL-01.",
        "2.2 - Technical clarification requests shall be answered within 5 business days.",
    ],
    "technical_memorial_rev_a.pdf": [
        "1.1 - The contractor shall deliver the 3D model revision within 15 calendar days after kickoff.",
        "1.2 - Quality verification shall be performed by the contractor before submission.",
        "1.3 - Measurement shall be based on approved isometric sheets.",
        "2.1 - Valve tagging shall follow the project coding standard ENG-VAL-01.",
        "2.2 - Technical clarification requests shall be answered within 5 business days.",
    ],
    "inspection_plan_rev_b.pdf": [
        "1.1 - The contractor shall deliver the 3D model revision within 10 calendar days after kickoff.",
        "1.2 - Quality verification shall be performed by the client before submission.",
        "1.3 - Measurement shall be based on approved isometric sheets.",
        "2.1 - Valve tagging shall follow the project coding standard ENG-VAL-02.",
        "2.2 - Technical clarification requests shall be answered within 3 business days.",
    ],
    "commercial_appendix.pdf": [
        "1.1 - The contractor shall deliver the 3D model revision within 10 calendar days after kickoff.",
        "1.2 - Quality verification shall be performed by the contractor before submission.",
        "1.3 - Measurement shall be based on approved bill of quantities.",
        "2.1 - Valve tagging shall follow the project coding standard ENG-VAL-01.",
        "2.2 - Technical clarification requests shall be answered within 5 business days.",
    ],
    "execution_guideline.pdf": [
        "1.1 - The contractor shall deliver the 3D model revision within 10 calendar days after kickoff.",
        "1.2 - Quality verification shall be performed by the contractor before submission.",
        "1.3 - Measurement shall be based on approved isometric sheets.",
        "2.1 - Valve tagging shall follow the project coding standard ENG-VAL-01.",
        "2.2 - Technical clarification requests shall be answered within 5 business days.",
        "3.1 - The client shall review all submissions within 7 business days.",
    ],
}


def build_sample_contract_pdfs() -> list[str]:
    CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)
    generated_files = []
    for filename, clauses in DOCUMENTS.items():
        path = CONTRACTS_DIR / filename
        pdf = canvas.Canvas(str(path), pagesize=A4)
        width, height = A4
        y = height - 60
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, "Engineering Contract Package")
        y -= 30
        pdf.setFont("Helvetica", 10)
        for clause in clauses:
            if y < 80:
                pdf.showPage()
                y = height - 60
                pdf.setFont("Helvetica", 10)
            pdf.drawString(50, y, clause)
            y -= 20
        pdf.save()
        generated_files.append(filename)
    return generated_files

