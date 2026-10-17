from scraper.research import detect_conference, enrich_research_fields, extract_paper_url


def test_detect_conference_and_quant_sponsors():
    conf, yr = detect_conference(
        "ADIA Lab Structural Break Challenge 2026",
        "Real-time structural break detection on CrunchDAO",
        ["time-series"],
    )
    assert conf == "ADIA Lab"
    assert yr == 2026

    conf2, yr2 = detect_conference(
        "Asset Allocation Performance forecasting",
        "Hosted by QRT on ENS Challenge Data",
        ["finance"],
        organizer="QRT (2026)",
    )
    assert conf2 == "QRT Research"

    conf3, yr3 = detect_conference(
        "ICAIF 2026 FinLLM Financial Reasoning Challenge",
        "ACM International Conference on AI in Finance",
        ["icaif"],
    )
    assert conf3 == "ICAIF"
    assert yr3 == 2026


def test_extract_paper_url_arxiv_and_ssrn():
    url1 = extract_paper_url("See benchmark paper at https://arxiv.org/abs/2502.12345v2 for LOB details.")
    assert url1 == "https://arxiv.org/abs/2502.12345v2"

    url2 = extract_paper_url("Working paper available at https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4129381")
    assert url2 == "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4129381"


def test_enrich_research_fields_combined():
    conf, yr, paper = enrich_research_fields(
        "G-Research Quantitative Forecasting 2026",
        "Details in arXiv:2505.99881",
        ["quant"],
    )
    assert conf == "G-Research"
    assert yr == 2026
    assert paper == "https://arxiv.org/abs/2505.99881"

