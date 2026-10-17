"""Unit tests for source HTML/JSON/JS parsers without network calls."""

from scraper.sources import crunchdao, devpost, ens, quantcontests


def test_crunchdao_parse_items_filters_bio():
    sample_items = [
        {
            "id": 27,
            "name": "structural-break-real-time",
            "displayName": "ADIA Lab Structural Break",
            "fullName": "ADIA Lab Structural Break Challenge: Real-Time Edition",
            "shortDescription": "Detect structural breaks in time series.",
            "status": "OPEN",
            "start": "2026-09-14T15:00:00Z",
            "end": "2026-11-30T15:00:00Z",
            "continuous": False,
            "hostedByName": "ADIA Lab",
            "prizePoolText": "100,000 $USDC",
            "prizePoolUsd": 100000.0,
            "url": "https://hub.crunchdao.com/competitions/structural-break-real-time",
            "statistics": {"participants": 812, "teams": 812, "submissions": 5211},
        },
        {
            "id": 25,
            "name": "broad-obesity-3",
            "displayName": "Broad Obesity #3",
            "fullName": "Autoimmune Disease Machine Learning Challenge #3",
            "shortDescription": "Single-cell Perturb-seq adipocyte differentiation.",
            "status": "OPEN",
            "hostedByName": "Broad Institute",
            "prizePoolText": "50,000 $USDC",
            "prizePoolUsd": 50000.0,
        },
    ]
    records = crunchdao._parse_items(sample_items)
    assert len(records) == 1
    assert records[0].title == "ADIA Lab Structural Break Challenge: Real-Time Edition"
    assert records[0].prize_usd == 100000.0


def test_ens_parse_html_and_records():
    html = """
    <html><body>
      <div class="search_result_container">
        <a href="/challenges/167">
          <h4>Asset Allocation Performance forecasting <em>by QRT (2026)</em></h4>
          <div title="Economic sciences">Economic sciences</div>
          <div title="Finance">Finance</div>
          <p>Forecast asset allocation portfolio performance from financial time series.</p>
        </a>
      </div>
      <div class="search_result_container">
        <a href="/challenges/160">
          <h4>Radiology CT Scan Segmentation <em>by Hospital (2026)</em></h4>
          <div title="Medicine">Medicine</div>
          <p>Segment tumor lesions in medical CT scans.</p>
        </a>
      </div>
    </body></html>
    """
    items = ens._parse_html(html)
    assert len(items) == 2
    records = ens._items_to_records(items)
    assert len(records) == 1
    assert "Asset Allocation Performance forecasting" in records[0].title
    assert records[0].organizer == "QRT"


def test_quantcontests_parse_js():
    sample_js = """
    const platforms = {
      worldquant: { name: 'WorldQuant BRAIN' }
    };
    const competitions = [
      {
        id: 'wq-1',
        title: 'WorldQuant BRAIN Alpha Research',
        platform: 'worldquant',
        description: 'Build predictive mathematical alpha models.',
        prize: '$100,000+',
        startDate: 'Ongoing',
        deadline: 'Ongoing',
        link: 'https://platform.worldquantbrain.com/',
        difficulty: 'Intermediate',
        tags: ['Ongoing', 'Alpha Research']
      }
    ];
    """
    parsed = quantcontests._parse_quant_contests_js(sample_js)
    assert len(parsed) == 1
    assert parsed[0]["title"] == "WorldQuant BRAIN Alpha Research"
    assert parsed[0]["platform"] == "worldquant"


def test_devpost_parse_date_range():
    start, end = devpost._parse_date_range("Oct 01 - Nov 15, 2026")
    assert start == "Oct 01, 2026"
    assert end == "Nov 15, 2026"

