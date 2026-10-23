"""Reproducible, explicitly fictional text-based invoice fixtures."""
import json
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parent.parent

def generate(destination: Path = ROOT / "data/samples") -> None:
    destination.mkdir(parents=True, exist_ok=True)
    fixtures = []
    for index, vendor in enumerate(["Imaginary Orbit Supplies", "Fictional Fern Studio", "Example Moon Workshop"], 1):
        record = {"file": f"invoice_{index}.pdf", "invoice_number": f"SYN-2026-{index:03}",
                  "vendor": vendor, "customer": "Fictional Demo Customer",
                  "date": "2026-10-20", "currency": "USD", "subtotal": "100.00", "tax": "20.00", "total": "120.00"}
        fields = [("Invoice", record["invoice_number"]), ("Vendor", vendor), ("Bill to", record["customer"]),
                  ("Date", record["date"]), ("Subtotal", "USD 100.00"), ("Tax", "USD 20.00"), ("Total", "USD 120.00")]
        if index == 2:
            fields = fields[1:4] + fields[:1] + fields[4:]
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_text((40, 40), "SYNTHETIC FIXTURE - NOT A REAL INVOICE", fontsize=12)
            for row, (label, value) in enumerate(fields):
                if index == 3:
                    page.insert_text((40, 90 + row*45), label, fontsize=11)
                    page.insert_text((260, 90 + row*45), value, fontsize=11)
                else:
                    page.insert_text((40, 100 + row*35), f"{label}: {value}", fontsize=11)
            document.save(destination / record["file"], no_new_id=True)
        fixtures.append(record)
    (destination / "ground_truth.json").write_text(json.dumps(fixtures, indent=2)+"\n", encoding="utf-8")
    (destination / "invoice.txt").write_text("SYNTHETIC INVOICE\nVendor: Fictional Paper Co\nInvoice: TXT-001\nTotal: USD 42.00\n", encoding="utf-8")

if __name__ == "__main__":
    generate()
