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
    copyright: (year: number) => `© ${year} Reality Gap Project`,
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
        body: 'The RG indicator is calculated using three different smoothing windows for earnings:',
        items: [
          {
            label: 'RG8',
            description:
              'Uses an 8-quarter (2-year) smoothed earnings base. More responsive to recent earnings changes.',
          },
          {
            label: 'RG10',
            description:
              'Uses a 10-quarter (2.5-year) smoothed earnings base. The primary reference variant.',
          },
          {
            label: 'RG12',
            description:
              'Uses a 12-quarter (3-year) smoothed earnings base. More stable but less sensitive to recent shifts.',
          },
        ],
        note: 'RG10 is used as the primary ranking metric. Comparing RG8, RG10, and RG12 together provides additional context about earnings stability.',
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
    author: 'H. Stre',
    abstract: {
      heading: 'Abstract',
      body: 'This paper introduces the Reality Gap (RG) indicator, a heuristic measure of the relationship between a company\'s market capitalisation and its estimated fundamental base. The fundamental base is constructed from a combination of smoothed earnings — averaged over 8, 10, or 12 quarterly periods — and tangible book equity. The resulting ratio provides a descriptive, period-specific view of how far market valuations extend beyond what the underlying fundamentals directly support. The paper presents the formal construction of the indicator, discusses its assumptions and limitations, and illustrates its application across a sample of publicly traded companies. RG is explicitly not a valuation model and does not generate price targets or investment recommendations.',
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
    },
    supportingData: {
      heading: 'Supporting Data',
      marketCap: 'Market Cap (approx.)',
      bookEquity: 'Book Equity (approx.)',
      netIncome: 'Net Income (approx.)',
      fundamentalBase: 'Fundamental Base (approx.)',
      billions: 'in billions',
    },
    trend: 'Trend',
    dataNote: 'Data Note',
    historicalPlaceholder: {
      heading: 'Historical RG Values',
      body: 'Chart shows available observations. Historical market cap approximated from closing price × current shares outstanding.',
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
        body: 'The Reality Gap indicator was developed by H. Stre. The accompanying working paper presents the full methodological framework.',
      },
      contact: {
        heading: 'Contact',
        body: 'For questions, feedback, or research inquiries, please get in touch via email.',
        email: 'contact@reality-gap.com',
        githubLabel: 'Project on GitHub',
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
} as const;

export type Translations = typeof en;
