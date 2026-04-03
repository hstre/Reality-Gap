export const de = {
  lang: 'de',
  langLabel: 'DE',
  altLang: 'EN',
  altLangLabel: 'EN',

  nav: {
    home: 'Startseite',
    methodology: 'Methodik',
    paper: 'Paper',
    companies: 'Unternehmen',
    rankings: 'Rankings',
    about: 'Über',
  },

  footer: {
    tagline: 'Ein forschungsbasierter heuristischer Indikator für fundamentale Abdeckung.',
    disclaimer: 'Alle dargestellten Daten sind illustrativ und dienen ausschließlich Forschungszwecken. Keine Anlageberatung.',
    copyright: (year: number) => `© ${year} Hanns-Steffen Rentschler`,
  },

  home: {
    meta: {
      title: 'Reality Gap — Indikator für fundamentale Abdeckung',
      description:
        'Reality Gap (RG) ist ein forschungsbasierter heuristischer Indikator, der misst, ob die Marktbewertung eines Unternehmens durch seine fundamentale Basis ungefähr abgedeckt ist.',
    },
    hero: {
      title: 'Reality Gap',
      subtitle: 'Ein forschungsbasierter Indikator für fundamentale Abdeckung',
      description:
        'Reality Gap (RG) misst das Verhältnis zwischen der Marktkapitalisierung eines Unternehmens und seiner geschätzten fundamentalen Basis — abgeleitet aus geglätteten Gewinnen und materiellem Eigenkapital. Es handelt sich um einen heuristischen Abdeckungsindikator, kein Modell für innere Werte.',
      note: 'Alle dargestellten Daten sind illustrativ. Siehe Methodik für Details.',
    },
    cards: {
      methodology: {
        title: 'Methodik',
        description: 'Wie RG8, RG10 und RG12 konstruiert werden und was sie messen.',
      },
      paper: {
        title: 'Working Paper',
        description: 'Die vollständige methodische Grundlage und der theoretische Kontext.',
      },
      rankings: {
        title: 'Rankings',
        description: 'Eine vergleichende Übersicht der Unternehmen, sortiert nach ihrem RG10-Wert.',
      },
      companies: {
        title: 'Unternehmen',
        description: 'Individuelle RG-Profile für jedes Unternehmen im Datensatz.',
      },
    },
    cta: 'Erkunden',
  },

  methodology: {
    meta: {
      title: 'Methodik — Reality Gap',
      description:
        'Eine Erläuterung, wie der Reality-Gap-Indikator konstruiert wird, was RG8, RG10 und RG12 messen und wie Trendcodes zu interpretieren sind.',
    },
    title: 'Methodik',
    intro:
      'Diese Seite erläutert, wie der Reality-Gap-Indikator (RG) konstruiert wird und was er misst. Für die vollständige formale Herleitung wird auf das Working Paper verwiesen.',
    sections: {
      whatIsRG: {
        heading: 'Was misst RG?',
        body: [
          'Der Reality-Gap-Indikator misst, ob die aktuelle Marktkapitalisierung eines Unternehmens durch eine geschätzte fundamentale Basis ungefähr abgedeckt ist. Die fundamentale Basis ergibt sich aus einer Kombination aus geglätteten Gewinnen und materiellem Eigenkapital.',
          'Ein höherer RG-Wert zeigt eine größere Lücke zwischen Marktbewertung und geschätzter fundamentaler Basis an — das heißt, der Markt bewertet das Unternehmen mit einem erheblichen Vielfachen dessen, was die Fundamentaldaten allein stützen würden.',
          'Ein niedrigerer RG-Wert deutet darauf hin, dass der Marktpreis näher an der fundamentalen Basis liegt.',
        ],
      },
      whatRGIsNot: {
        heading: 'Was RG nicht misst',
        body: [
          'RG ist kein Modell für innere Werte. Es beansprucht nicht, den „wahren" oder „fairen" Wert eines Unternehmens zu bestimmen.',
          'RG ist kein Kursziel. Es impliziert nicht, dass eine Aktie in einem handlungsrelevanten Sinne über- oder unterbewertet ist.',
          'RG ist keine Anlageempfehlung. Es ist ein beschreibender, heuristischer Indikator für analytische und Forschungszwecke.',
          'Der Indikator sollte mit Vorsicht interpretiert werden, insbesondere bei Unternehmen mit begrenzter Betriebsgeschichte, ungewöhnlichen Kapitalstrukturen oder nicht standardmäßigen Ertragsmustern.',
        ],
      },
      variants: {
        heading: 'RG-Varianten: RG8, RG10, RG12',
        body: 'Der RG-Indikator wird mit drei verschiedenen Glättungsfenstern für Gewinne berechnet:',
        items: [
          {
            label: 'RG8',
            description:
              'Verwendet eine geglättete Gewinnbasis über 8 Quartale (2 Jahre). Reagiert stärker auf aktuelle Gewinnveränderungen.',
          },
          {
            label: 'RG10',
            description:
              'Verwendet eine geglättete Gewinnbasis über 10 Quartale (2,5 Jahre). Die primäre Referenzvariante.',
          },
          {
            label: 'RG12',
            description:
              'Verwendet eine geglättete Gewinnbasis über 12 Quartale (3 Jahre). Stabiler, aber weniger sensibel gegenüber jüngsten Veränderungen.',
          },
        ],
        note: 'RG10 wird als primäre Kennzahl für das Ranking verwendet. Der Vergleich von RG8, RG10 und RG12 liefert zusätzlichen Kontext über die Stabilität der Gewinne.',
      },
      trendCodes: {
        heading: 'Trendcodes',
        body: 'Jede Beobachtung trägt einen Trendcode, der die jüngste Richtungsänderung des RG-Werts anzeigt:',
        items: [
          { code: '++', label: 'Stark steigend', description: 'RG ist in den letzten Quartalen deutlich gestiegen.' },
          { code: '+', label: 'Steigend', description: 'RG ist in den letzten Quartalen moderat gestiegen.' },
          { code: '=', label: 'Annähernd stabil', description: 'RG ist weitgehend unverändert geblieben.' },
          { code: '-', label: 'Sinkend', description: 'RG ist in den letzten Quartalen moderat gesunken.' },
          { code: '--', label: 'Stark sinkend', description: 'RG ist in den letzten Quartalen deutlich gesunken.' },
        ],
        note: 'Trendcodes werden pro Beobachtung berechnet und spiegeln die Richtung der Veränderung wider, nicht das absolute Niveau.',
      },
      keyConcepts: {
        heading: 'Schlüsselkonzepte',
        items: [
          {
            label: 'Materielles Eigenkapital',
            description:
              'Buchwert des Eigenkapitals bereinigt um Goodwill und andere immaterielle Vermögenswerte. Wird als Untergrenzkomponente in der Berechnung der fundamentalen Basis verwendet.',
          },
          {
            label: 'Geglättete Gewinne',
            description:
              'Ein Durchschnitt des Nettoeinkommens über das Beobachtungsfenster (8, 10 oder 12 Quartale). Die Glättung reduziert den Einfluss von Einmaleffekten und zyklischen Verzerrungen.',
          },
          {
            label: 'Fundamentale Basis',
            description:
              'Ein annäherndes kombiniertes Maß für Ertragskraft und materielles Eigenkapital. Wird als Nenner im RG-Verhältnis verwendet.',
          },
          {
            label: 'Heuristischer Indikator',
            description:
              'RG ist ausdrücklich eine Heuristik — ein praktisches Näherungsinstrument. Er ist darauf ausgelegt, informativ und konsistent zu sein, nicht ein präzises oder definitives Bewertungsmodell zu sein.',
          },
        ],
      },
      paper: {
        heading: 'Vollständige Methodik',
        body: 'Für die vollständige formale Herleitung, Annahmen, Einschränkungen und ausgearbeitete Beispiele wird auf das Working Paper verwiesen.',
        link: 'Working Paper lesen',
      },
    },
  },

  paper: {
    meta: {
      title: 'Working Paper — Reality Gap',
      description:
        'Das Working Paper mit der vollständigen theoretischen und methodischen Grundlage des Reality-Gap-Indikators.',
    },
    title: 'Working Paper',
    label: 'Working Paper',
    paperTitle: 'Reality Gap: Ein heuristischer Indikator für fundamentale Abdeckung',
    author: 'Hanns-Steffen Rentschler',
    abstract: {
      heading: 'Abstract',
      body: 'Dieses Paper stellt den Reality-Gap-Indikator (RG) vor, ein heuristisches Maß für das Verhältnis zwischen der Marktkapitalisierung eines Unternehmens und seiner geschätzten fundamentalen Basis. Die fundamentale Basis wird aus einer Kombination geglätteter Gewinne — gemittelt über 8, 10 oder 12 Quartalszeiträume — und materiellem Buchwert des Eigenkapitals konstruiert. Das resultierende Verhältnis bietet einen beschreibenden, periodenspezifischen Blick darauf, wie weit Marktbewertungen über das hinausgehen, was die zugrunde liegenden Fundamentaldaten direkt stützen. Das Paper präsentiert die formale Konstruktion des Indikators, erörtert seine Annahmen und Einschränkungen und veranschaulicht seine Anwendung an einer Stichprobe börsennotierter Unternehmen. RG ist ausdrücklich kein Bewertungsmodell und generiert keine Kursziele oder Anlageempfehlungen.',
    },
    download: {
      heading: 'Download',
      description: 'Das Working Paper ist als PDF-Dokument verfügbar.',
      button: 'Working Paper herunterladen (PDF)',
      ssrn: 'Auf SSRN ansehen',
      placeholder: 'Das PDF wird hier verfügbar sein, sobald das Paper veröffentlicht ist.',
    },
    citation: {
      heading: 'Zitierhinweis',
      note: 'Bitte zitieren als:',
    },
  },

  companies: {
    meta: {
      title: 'Unternehmen — Reality Gap',
      description: 'Übersicht der Unternehmen im Reality-Gap-Datensatz mit ihren aktuellen RG-Werten.',
    },
    title: 'Unternehmen',
    intro: 'Die folgenden Unternehmen sind im ersten Reality-Gap-Datensatz enthalten. Alle Werte sind illustrative Näherungswerte.',
    rg10Label: 'RG10',
    trendLabel: 'Trend',
    periodLabel: 'Periode',
    viewDetails: 'Details anzeigen',
    dataNote: 'Illustrative Daten — keine Anlageberatung.',
  },

  companyDetail: {
    backToCompanies: '← Zurück zu Unternehmen',
    latestObservation: 'Aktuelle Beobachtung',
    period: 'Periode',
    ticker: 'Ticker',
    sector: 'Sektor',
    currency: 'Währung',
    metrics: {
      heading: 'RG-Kennzahlen',
      notComputable: 'RG nicht berechenbar',
      notComputableNote: 'Die fundamentale Basis ist null oder negativ: Das materielle Eigenkapital ist negativ und der geglättete Gewinn ist über alle Glättungsfenster (RG8, RG10, RG12) hinweg negativ. Nach der RG-Methodik bedeutet eine nicht-positive fundamentale Basis, dass die Gewinnhistorie keine fundamentale Abdeckung bei der aktuellen Marktkapitalisierung bietet. RG ist undefiniert.',
    },
    supportingData: {
      heading: 'Zusatzdaten',
      marketCap: 'Marktkapitalisierung (ca.)',
      bookEquity: 'Buchwert Eigenkapital (ca.)',
      netIncome: 'Nettoeinkommen (ca.)',
      fundamentalBase: 'Fundamentale Basis (ca.)',
      billions: 'in Milliarden',
    },
    trend: 'Trend',
    dataNote: 'Datenhinweis',
    historicalChart: {
      heading: 'Historische RG-Werte',
      noData: 'Historischer RG-Verlauf für dieses Unternehmen noch nicht verfügbar.',
      shorterHistory: 'Historische Reihe kürzer als 10 Jahre aufgrund aktueller Datenverfügbarkeit.',
    },
    disclaimer: 'Alle Werte sind illustrative Näherungswerte und werden ausschließlich zu Forschungszwecken bereitgestellt. Keine Anlageberatung.',
  },

  rankings: {
    meta: {
      title: 'Rankings — Reality Gap',
      description: 'Vergleichendes Ranking der Unternehmen nach ihrem Reality-Gap-Wert (RG10).',
    },
    title: 'Rankings',
    intro: 'Unternehmen gerankt nach ihrem aktuellen RG10-Wert. Alle Daten sind illustrativ.',
    filterLabel: 'Sektor:',
    allSectors: 'Alle Sektoren',
    indexFilterLabel: 'Index:',
    allIndices: 'Alle Indizes',
    searchLabel: 'Suche:',
    searchPlaceholder: 'Unternehmen oder Ticker…',
    sortBy: 'Sortieren nach',
    noResults: 'Keine Unternehmen entsprechen Ihrem Filter.',
    columns: {
      company: 'Unternehmen',
      ticker: 'Ticker',
      sector: 'Sektor',
      period: 'Periode',
      rg8: 'RG8',
      rg10: 'RG10',
      rg12: 'RG12',
      trend: 'Trend',
    },
    dataNote: 'Illustrative Daten — keine Anlageberatung.',
  },

  about: {
    meta: {
      title: 'Über — Reality Gap',
      description: 'Über das Reality-Gap-Projekt, seinen Zweck und Kontaktmöglichkeiten.',
    },
    title: 'Über',
    sections: {
      project: {
        heading: 'Das Projekt',
        body: [
          'Reality Gap (RG) ist ein unabhängiges Forschungsprojekt, das einen heuristischen Indikator für fundamentale Abdeckung entwickelt. Das Projekt ist mit keiner Finanzinstitution, keinem Investmentfonds und keinem kommerziellen Datenanbieter verbunden.',
          'Der Indikator ist als analytisches Werkzeug für Forscher und Investoren konzipiert, die Marktbewertungen in den Kontext von Fundamentaldaten stellen möchten. Er ist nicht als Grundlage für Anlageentscheidungen gedacht.',
          'Alle auf dieser Website in der ersten Version veröffentlichten Daten sind illustrativ und näherungsweise. Sie werden bereitgestellt, um die Struktur und Eigenschaften des Indikators zu demonstrieren, nicht als verlässliche Finanzdaten.',
        ],
      },
      author: {
        heading: 'Autor',
        body: 'Der Reality-Gap-Indikator wurde von Hanns-Steffen Rentschler entwickelt. Das begleitende Working Paper präsentiert den vollständigen methodischen Rahmen.',
      },
      contact: {
        heading: 'Kontakt',
        body: 'Für Fragen, Feedback oder Forschungsanfragen können Sie per E-Mail Kontakt aufnehmen.',
        email: 'rentschler@lbsmail.de',
        githubLabel: 'Projekt auf GitHub',
      },
      dataSources: {
        heading: 'Datenquellen',
        body: [
          'Alle auf dieser Website angezeigten Finanzdaten — einschließlich Marktkapitalisierung, Nettogewinn und Buchwert — werden über yfinance abgerufen, eine Open-Source-Python-Bibliothek, die öffentlich verfügbare Daten von Yahoo Finance bezieht.',
          'Yahoo Finance aggregiert Finanzdaten von Börsen und Unternehmensberichten. Die Daten können Fehler, Verzögerungen oder Lücken enthalten. Es wird keine unabhängige Überprüfung vorgenommen.',
          'Historische Marktkapitalisierungswerte sind Näherungswerte: Schlusskurse am Geschäftsjahresende multipliziert mit der aktuellen Aktienanzahl. Veränderungen der Aktienanzahl im Zeitverlauf sind nicht berücksichtigt.',
          'Die dargestellten RG-Werte sind berechnete Näherungen, keine geprüften Finanzkennzahlen. Sie dienen ausschließlich Forschungs- und Illustrationszwecken.',
        ],
      },
      disclaimer: {
        heading: 'Haftungsausschluss',
        body: 'Nichts auf dieser Website stellt eine Anlageberatung, eine Empfehlung zum Kauf oder Verkauf von Wertpapieren oder eine Aufforderung zu einer Anlageentscheidung dar. Der Reality-Gap-Indikator ist ein beschreibendes Forschungsinstrument. Alle Daten sind illustrativ.',
      },
    },
  },

  trend: {
    '++': 'Stark steigend',
    '+': 'Steigend',
    '=': 'Stabil',
    '-': 'Sinkend',
    '--': 'Stark sinkend',
  },
} as const;

export type DeTranslations = typeof de;
