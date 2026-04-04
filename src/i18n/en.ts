export const en = {
  lang: 'en',
  langLabel: 'EN',
  altLang: 'DE',
  altLangLabel: 'DE',

  nav: {
    home: 'Home',
    methodology: 'Methodology',
    paper: 'Paper',
    companies: 'Companies',
    rankings: 'Rankings',
    about: 'About',
  },

  footer: {
    tagline: 'A research-based heuristic indicator for fundamental coverage.',
    disclaimer: 'All data shown is illustrative and for research purposes only. Not investment advice.',
    copyright: (year: number) => `© ${year} Hanns-Steffen Rentschler`,
  },

  home: {
    meta: {
      title: 'Reality Gap — Fundamental Coverage Indicator',
      description:
        'Reality Gap (RG) is a research-based heuristic indicator measuring whether a company\'s market valuation is approximately covered by its fundamental base.',
    },
    hero: {
      title: 'Reality Gap',
      subtitle: 'A Research-Based Indicator for Fundamental Coverage',
      description:
        'Reality Gap (RG) measures the relationship between a company\'s market capitalisation and its estimated fundamental base — derived from smoothed earnings and tangible equity. It is a heuristic coverage indicator, not an intrinsic value model.',
      note: 'All data shown is illustrative. See the methodology for details.',
    },
    cards: {
      methodology: {
        title: 'Methodology',
        description: 'How RG8, RG10, and RG12 are constructed and what they measure.',
      },
      paper: {
        title: 'Working Paper',
        description: 'The full methodological foundation and theoretical context.',
      },
      rankings: {
        title: 'Rankings',
        description: 'A comparative view of companies sorted by their RG10 value.',
      },
      companies: {
        title: 'Companies',
        description: 'Individual RG profiles for each company in the dataset.',
      },
    },
    cta: 'Explore',
  },

  methodology: {
    meta: {
      title: 'Methodology — Reality Gap',
      description:
        'An explanation of how the Reality Gap indicator is constructed, what RG8, RG10, and RG12 measure, and how trend codes are interpreted.',
    },
    title: 'Methodology',
    intro:
      'This page explains how the Reality Gap (RG) indicator is constructed and what it measures. For the complete formal derivation, please refer to the working paper.',
    sections: {
      whatIsRG: {
        heading: 'What Does RG Measure?',
        body: [
          'The Reality Gap indicator measures whether a company\'s current market capitalisation is approximately covered by an estimated fundamental base. The fundamental base is derived from a combination of smoothed earnings and tangible equity.',
          'A higher RG value indicates a larger gap between market valuation and the estimated fundamental base — meaning the market is pricing the company at a significant multiple of what the fundamentals alone would support.',
          'A lower RG value suggests that the market price is closer to being covered by the fundamental base.',
        ],
      },
      whatRGIsNot: {
        heading: 'What RG Does Not Measure',
        body: [
          'RG is not an intrinsic value model. It does not claim to determine a company\'s "true" or "fair" value.',
          'RG is not a price target. It does not imply that a stock is overvalued or undervalued in any actionable sense.',
          'RG is not an investment recommendation. It is a descriptive, heuristic indicator intended for analytical and research purposes.',
          'The indicator should be interpreted with caution, particularly for companies with limited operating history, unusual capital structures, or non-standard earnings patterns.',
        ],
      },
      variants: {
        heading: 'RG Variants: RG8, RG10, RG12',
        body: 'The subscript N (8, 10, 12) is the capitalization factor — not a smoothing window. G is computed once using a single fixed rule and enters the formula with three different multiples:',
        items: [
          {
            label: 'RG8',
            description:
              'RG\u2088 = MC / (TE + 8\u00d7G). Uses a capitalization factor of 8. The most conservative assumption: only 8 years of smoothed earnings are assumed to justify the earnings component. With the same G and TE, RG8 \u2265 RG10 \u2265 RG12.',
          },
          {
            label: 'RG10',
            description:
              'RG\u2081\u2080 = MC / (TE + 10\u00d7G). Uses a capitalization factor of 10. The primary reference variant.',
          },
          {
            label: 'RG12',
            description:
              'RG\u2081\u2082 = MC / (TE + 12\u00d7G). Uses a capitalization factor of 12. The most generous assumption: 12 years of smoothed earnings justify the earnings component. Produces the lowest RG of the three.',
          },
        ],
        note: 'G is smoothed over the last 8 available quarters (annualized). N is the capitalization factor — not the averaging window. RG10 is the primary ranking metric.',
      },
      trendCodes: {
        heading: 'Trend Codes',
        body: 'Each observation carries a trend code indicating the recent directional change in the RG value:',
        items: [
          { code: '++', label: 'Strongly Increasing', description: 'RG has increased significantly in recent quarters.' },
          { code: '+', label: 'Increasing', description: 'RG has increased moderately in recent quarters.' },
          { code: '=', label: 'Approximately Stable', description: 'RG has remained broadly unchanged.' },
          { code: '-', label: 'Declining', description: 'RG has declined moderately in recent quarters.' },
          { code: '--', label: 'Strongly Declining', description: 'RG has declined significantly in recent quarters.' },
        ],
        note: 'Trend codes are computed per observation and reflect the direction of change, not the absolute level.',
      },
      keyConcepts: {
        heading: 'Key Concepts',
        items: [
          {
            label: 'Tangible Equity',
            description:
              'Book equity adjusted for goodwill and other intangible assets. Used as a floor component in the fundamental base calculation.',
          },
          {
            label: 'Smoothed Earnings',
            description:
              'An average of net income across the observation window (8, 10, or 12 quarters). Smoothing reduces the impact of one-time items and cyclical distortions.',
          },
          {
            label: 'Fundamental Base',
            description:
              'An approximate combined measure of earnings capacity and tangible equity. Used as the denominator in the RG ratio.',
          },
          {
            label: 'Heuristic Indicator',
            description:
              'RG is explicitly a heuristic — a practical approximation tool. It is designed to be informative and consistent, not to be a precise or definitive valuation model.',
          },
        ],
      },
      paper: {
        heading: 'Full Methodology',
        body: 'For the complete formal derivation, assumptions, limitations, and worked examples, please refer to the working paper.',
        link: 'Read the Working Paper',
      },
    },
  },

  paper: {
    meta: {
      title: 'Working Paper — Reality Gap',
      description:
        'The working paper presenting the full theoretical and methodological foundation of the Reality Gap indicator.',
    },
    title: 'Working Paper',
    label: 'Working Paper',
    paperTitle: 'Reality Gap: A Heuristic Indicator for Fundamental Coverage',
    author: 'Hanns-Steffen Rentschler',
    abstract: {
      heading: 'Abstract',
      body: 'This paper introduces the Reality Gap (RG) indicator, a heuristic measure of the relationship between a company\'s market capitalisation and its estimated fundamental base. The fundamental base is FB\u2099 = TE + E\u2099 where TE is tangible equity and E\u2099 = N\u00d7G is the capitalised sustainable earning power (G = smoothed long-run earnings, N \u2208 {8, 10, 12} the capitalization factor). The resulting ratio provides a descriptive, period-specific view of how far market valuations extend beyond what the underlying fundamentals directly support. The paper presents the formal construction of the indicator, discusses its assumptions and limitations, and illustrates its application across a sample of publicly traded companies. RG is explicitly not a valuation model and does not generate price targets or investment recommendations.',
    },
    download: {
      heading: 'Download',
      description: 'The working paper is available as a PDF document.',
      button: 'Download Working Paper (PDF)',
      ssrn: 'View on SSRN',
      placeholder: 'The PDF will be available here once the paper is published.',
    },
    citation: {
      heading: 'Citation',
      note: 'Please cite as:',
    },
  },

  companies: {
    meta: {
      title: 'Companies — Reality Gap',
      description: 'Overview of companies in the Reality Gap dataset with their latest RG values.',
    },
    title: 'Companies',
    intro: 'The companies below are included in the initial Reality Gap dataset. All values are illustrative approximations.',
    rg10Label: 'RG10',
    trendLabel: 'Trend',
    periodLabel: 'Period',
    viewDetails: 'View Details',
    dataNote: 'Illustrative data — not investment advice.',
  },

  companyDetail: {
    backToCompanies: '← Back to Companies',
    latestObservation: 'Latest Observation',
    period: 'Period',
    ticker: 'Ticker',
    sector: 'Sector',
    currency: 'Currency',
    metrics: {
      heading: 'RG Metrics',
      notComputable: 'Not Fundamentally Covered',
      notComputableNote: 'FB\u2099 = TE + E\u2099 \u2264 0 for all capitalization factors N \u2208 {8,10,12}. Tangible equity is negative and smoothed earnings G are not large enough to produce a positive fundamental base. Under the paper definition, RG is undefined for this company at this period.',
      nearBoundaryHeading: 'Near-Boundary Case',
      nearBoundaryNote: 'Tangible equity (TE) is deeply negative. The fundamental base FB\u2088 = TE + G\u00d78 is positive but very small — less than 10% of the earnings contribution G\u00d78. A small change in smoothed earnings G would push FB\u2088 negative (not fundamentally covered). RG\u2088 values above 50 are displayed as \u201e>50\u201c for readability. The underlying raw value is stored in full precision.',
    },
    supportingData: {
      heading: 'Supporting Data',
      marketCap: 'Market Cap (approx.)',
      tangibleEquity: 'Tangible Equity (TE)',
      smoothedEarnings: 'Smoothed Earnings G (ann.)',
      netIncome: 'Net Income (approx.)',
      fundamentalBase: 'Fundamental Base FB\u2081\u2080',
      teApprox: 'TE approximated as book equity (goodwill/intangibles not separately available from data source).',
      billions: 'in billions',
    },
    trend: 'Trend',
    dataNote: 'Data Note',
    historicalChart: {
      heading: 'Historical RG Values',
      noData: 'Historical RG chart not yet available for this company.',
      shorterHistory: 'Historical series shorter than 10 years due to current data availability.',
    },
    disclaimer: 'All values are illustrative approximations and are provided for research purposes only. Not investment advice.',
  },

  rankings: {
    meta: {
      title: 'Rankings — Reality Gap',
      description: 'Comparative ranking of companies by their Reality Gap (RG10) value.',
    },
    title: 'Rankings',
    intro: 'Companies ranked by their latest RG10 value. All data is illustrative.',
    downloadJson: 'Download JSON',
    downloadCsv: 'Download CSV',
    downloadNote: 'Full dataset. Research use only. Not investment advice.',
    filterLabel: 'Sector:',
    allSectors: 'All Sectors',
    indexFilterLabel: 'Index:',
    allIndices: 'All Indices',
    searchLabel: 'Search:',
    searchPlaceholder: 'Company or ticker…',
    sortBy: 'Sort by',
    noResults: 'No companies match your filter.',
    columns: {
      company: 'Company',
      ticker: 'Ticker',
      sector: 'Sector',
      period: 'Period',
      rg8: 'RG8',
      rg10: 'RG10',
      rg12: 'RG12',
      trend: 'Trend',
    },
    dataNote: 'Illustrative data — not investment advice.',
  },

  about: {
    meta: {
      title: 'About — Reality Gap',
      description: 'About the Reality Gap project, its purpose, and how to get in touch.',
    },
    title: 'About',
    sections: {
      project: {
        heading: 'The Project',
        body: [
          'Reality Gap (RG) is an independent research project developing a heuristic indicator for fundamental coverage. The project is not affiliated with any financial institution, investment fund, or commercial data provider.',
          'The indicator is designed as an analytical tool for researchers and investors who wish to place market valuations in the context of fundamental data. It is not intended as a basis for investment decisions.',
          'All data published on this website in the initial release is illustrative and approximate. It is provided to demonstrate the indicator\'s structure and properties, not as reliable financial data.',
        ],
      },
      author: {
        heading: 'Author',
        body: 'The Reality Gap indicator was developed by Hanns-Steffen Rentschler. The accompanying working paper presents the full methodological framework.',
      },
      contact: {
        heading: 'Contact',
        body: 'For questions, feedback, or research inquiries, please get in touch via email.',
        email: 'rentschler@lbsmail.de',
        githubLabel: 'Project on GitHub',
      },
      websiteApproximation: {
        heading: 'Website Approximation Note',
        body: [
          'The paper defines G as the smoothed long-run earnings measure. This website uses a fixed operational approximation: G_approx = mean of the last 8 available quarterly net income figures, annualised (×4). The same G_approx is used identically for RG8, RG10, and RG12 — only the capitalization factor N changes.',
          'This approximation is consistent with the paper\'s structural logic (single G, varying N) but differs from a full paper implementation in two respects: (1) the smoothing window is fixed at 8 quarters rather than potentially calibrated per company; (2) when fewer than 8 real quarterly observations are available, the series is extended with annual figures divided by 4 as a fallback.',
          'Wherever real quarterly data is insufficient, the observation is labeled with dataType = "annual" and excluded from the historical chart. The smoothedEarnings field and teIsApprox flag are stored explicitly in each observation so the approximation is always traceable.',
        ],
      },
      dataSources: {
        heading: 'Data Sources',
        body: [
          'All financial data displayed on this website — including market capitalisation, net income, and tangible equity — is retrieved via yfinance, an open-source Python library that accesses publicly available data from Yahoo Finance.',
          'Yahoo Finance aggregates financial data from stock exchanges and company filings. The data may contain errors, delays, or gaps. No independent verification is performed.',
          'Historical market capitalisation values are approximations: closing prices at fiscal year-end multiplied by current shares outstanding. Share count changes over time are not reflected.',
          'The RG values shown are computed approximations, not audited financial figures. They are provided for research and illustrative purposes only.',
        ],
      },
      disclaimer: {
        heading: 'Disclaimer',
        body: 'Nothing on this website constitutes investment advice, a recommendation to buy or sell any security, or a solicitation of any investment decision. The Reality Gap indicator is a descriptive research tool. All data is illustrative.',
      },
    },
  },

  trend: {
    '++': 'Strongly Increasing',
    '+': 'Increasing',
    '=': 'Stable',
    '-': 'Declining',
    '--': 'Strongly Declining',
  },

  research: {
    label: 'Exploratory Research',
    heading: 'Historical Research',
    subheading: 'Retrospective, cross-sectional, and sector-level observations from the current RG dataset. Preliminary and approximate.',
    disclaimer: {
      heading: 'Research Caveat',
      body: 'This page presents exploratory observations based on an approximate, limited dataset. All results are preliminary. No predictive or causal claims are made. RG is a descriptive heuristic indicator — not a forecasting model and not investment advice. Sample sizes are small, data coverage is partial, and all values are approximations derived from public sources via yfinance. Do not draw strong conclusions from this analysis.',
    },
    indexSection: {
      heading: '1. Cross-Index Snapshot',
      note: 'Median RG10 and interquartile range by index for the most recent quarterly observation per company. Only companies with a valid, non-near-boundary RG10 are included.',
      colIndex:  'Index',
      colN:      'n',
      colP25:    'P25',
      colMedian: 'Median RG10',
      colP75:    'P75',
      footnote:  'Higher RG10 suggests the market is assigning a larger multiple to the fundamental base. Whether this reflects overvaluation, expected future earnings growth, or structural differences between markets cannot be determined from RG alone.',
    },
    distribution: {
      heading: '2. Current RG10 Distribution',
      note: 'Distribution of the most recent RG10 across {n} of {total} covered companies. {notCovered} classified as "not fundamentally covered" (FB ≤ 0 for all N). {nearBoundary} flagged as near-boundary and excluded from distribution.',
      medianLabel: 'Median',
      footnote:    'RG10 = Market Cap / Fundamental Base (N=10). Smoothed earnings G approximated from last 8 quarters. US companies adjusted for inflation (CPI-real). All values approximate.',
    },
    sectors: {
      heading: '3. Sector Comparison',
      note: 'Median RG10 by sector. Bar length represents median; n = number of companies. Sectors with fewer than 3 companies should be interpreted with particular caution.',
      footnote: 'Sector differences may reflect structural characteristics (capital intensity, intangibles, leverage) rather than relative valuation stretch. Sectors are as classified in the dataset.',
    },
    timeSeries: {
      heading: '4. Cross-Sectional Snapshot Over Time',
      note: 'Median RG10 and interquartile range across all qualifying quarterly observations per period. Only periods with ≥ 15 qualifying companies are shown. This is not a panel dataset — the company composition varies across periods.',
      colPeriod:  'Period',
      colN:       'n',
      colP25:     'P25',
      colMedian:  'Median RG10',
      colP75:     'P75',
      noData:     'Insufficient data for time series (fewer than 15 qualifying companies per period).',
      footnote:   'The dataset covers only 4 recent quarters of quarterly data plus a limited number of annual historical observations. No robust trend conclusions can be drawn from this sample.',
    },
    useCases: {
      heading: '5. What Historical RG Analysis Might Reveal',
      items: [
        {
          title: 'Market-wide valuation stretch',
          body: 'If median RG rises consistently over multiple years, it could suggest that market prices are moving further from fundamental bases — a pattern reminiscent of valuation-stretch indicators like the Shiller CAPE. With the current 4-quarter dataset this cannot be assessed.',
        },
        {
          title: 'Sector rotation signals',
          body: 'Differences in median RG across sectors may reflect varying market expectations for earnings growth, capital intensity, or risk. Persistent high-RG sectors could be candidates for closer scrutiny in a longer historical study.',
        },
        {
          title: 'Retrospective sorting analysis',
          body: 'In a sufficiently long dataset, one could group companies by their RG quartile at a historical date and observe subsequent price performance. This is the approach used in academic factor research. The current dataset is too small and too short for such an analysis to be meaningful.',
        },
        {
          title: 'Dispersion as a bubble indicator',
          body: 'Widening dispersion between high-RG and low-RG companies — or rapid upper-tail expansion — could serve as an exploratory signal of concentrated valuation stretch. This requires multi-year historical data not yet available in this dataset.',
        },
      ],
    },
    limitations: {
      heading: '6. Data Limitations',
      items: [
        'Coverage: 77 companies across three indices (S&P 500 top 30, Nikkei 225 top 19, DAX 40 top 28). This is not a complete index. Results do not generalise to index-level conclusions.',
        'Earnings smoothing: G is approximated as the mean of the last 8 available quarterly net income figures, annualised. This is an operational simplification; the paper defines G more rigorously.',
        'Tangible equity: TE may fall back to book equity when goodwill and intangibles are not separately available from the data source (yfinance). Affected observations are flagged teIsApprox = true.',
        'CPI adjustment for US companies: Inflation adjustment uses FRED CPIAUCSL. Non-US companies use nominal earnings, which affects cross-index comparability.',
        'Historical market cap: Annual historical observations use historical closing price × current shares outstanding. Share count changes are not reflected.',
        'Historical tangible equity: Annual historical observations use the current TE snapshot (not historical TE). This introduces an approximation into all historical annual RG values.',
        'No audited data: All values are derived from yfinance / Yahoo Finance public data. Figures may differ from audited financial statements.',
        'No predictive validation: RG has not been validated as a predictive indicator. The relationship between RG values and future returns is unknown.',
      ],
    },
  },
} as const;

export type Translations = typeof en;
