from backend.services.scoring_service import detect_contract_type, evaluate_missing_protections

def test_detect_rental_type():
    rental_text = "This lease agreement is made between Landlord and Tenant for monthly rent of Flat 402 with security deposit."
    contract_type = detect_contract_type(rental_text, "lease.pdf")
    assert contract_type == "rental"

def test_detect_employment_type():
    emp_text = "The Company offers employment as Software Engineer with CTC salary, probation period, and leave policy."
    contract_type = detect_contract_type(emp_text, "offer_letter.docx")
    assert contract_type == "employment"

def test_missing_protections_rental():
    # Text that mentions rent and deposit but omits inspection notice and maintenance breakdown
    partial_text = "Tenant will pay rent of INR 25000 and deposit of INR 50000. Landlord can terminate."
    missing = evaluate_missing_protections("rental", partial_text)
    assert len(missing) > 0
    names = [m.name for m in missing]
    assert any("Inspection" in n or "Maintenance" in n for n in names)
