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
        body: 'N im Subscript bezeichnet den Kapitalisierungsfaktor — nicht das Glättungsfenster. G wird einheitlich über die letzten 8 Quartale geglättet.',
        items: [
          {
            label: 'RG8',
            description:
              'RG\u2088 = MC / (EK + 8\u00d7G). Konservative Annahme: nur 8 Jahresgewinne rechtfertigen die Gewinnkomponente. Ergibt den höchsten RG-Wert der drei Varianten.',
          },
          {
            label: 'RG10',
            description:
              'RG\u2081\u2080 = MC / (EK + 10\u00d7G). Primäre Referenzvariante.',
          },
          {
            label: 'RG12',
            description:
              'RG\u2081\u2082 = MC / (EK + 12\u00d7G). Großzügige Annahme: 12 Jahresgewinne rechtfertigen die Gewinnkomponente. Ergibt den niedrigsten RG-Wert der drei Varianten.',
          },
        ],
        note: 'Bei positivem G gilt stets: RG8 \u2265 RG10 \u2265 RG12. RG10 ist die primäre Kennzahl für das Ranking.',
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
              'Geglätteter Langfristgewinn G: Mittelwert der letzten 8 verfügbaren Quartale, annualisiert. Dasselbe G wird für RG8, RG10 und RG12 verwendet — nur der Kapitalisierungsfaktor N variiert.',
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
      body: 'Dieses Paper stellt den Reality-Gap-Indikator (RG) vor, ein heuristisches Maß für das Verhältnis zwischen der Marktkapitalisierung eines Unternehmens und seiner geschätzten fundamentalen Basis. Die fundamentale Basis ist FB\u2099 = EK + E\u2099, wobei EK das tangible Eigenkapital und E\u2099 = N\u00d7G die kapitalisierte nachhaltige Ertragskraft ist (G = geglätteter Langfristgewinn, N \u2208 {8, 10, 12} der Kapitalisierungsfaktor). Das resultierende Verhältnis bietet einen beschreibenden, periodenspezifischen Blick darauf, wie weit Marktbewertungen über das hinausgehen, was die zugrunde liegenden Fundamentaldaten direkt stützen. Das Paper präsentiert die formale Konstruktion des Indikators, erörtert seine Annahmen und Einschränkungen und veranschaulicht seine Anwendung an einer Stichprobe börsennotierter Unternehmen. RG ist ausdrücklich kein Bewertungsmodell und generiert keine Kursziele oder Anlageempfehlungen.',
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
      notComputable: 'Fundamental nicht abgedeckt',
      notComputableNote: 'FB\u2099 = EK + E\u2099 \u2264 0 für alle Kapitalisierungsfaktoren N \u2208 {8,10,12}. Das tangible Eigenkapital ist negativ und der geglättete Gewinn G reicht nicht aus, um eine positive fundamentale Basis zu erzeugen. Nach der Papierdefinition ist RG für dieses Unternehmen in diesem Zeitraum undefiniert.',
      nearBoundaryHeading: 'Grenzfall der Methodik',
      nearBoundaryNote: 'Das tangible Eigenkapital (EK) ist stark negativ. Die fundamentale Basis FB\u2088 = EK + G\u00d78 ist zwar positiv, aber sehr klein \u2014 unter 10\u00a0% des Gewinnbeitrags G\u00d78. Eine kleine \u00c4nderung im gegl\u00e4tteten Gewinn G w\u00fcrde FB\u2088 ins Negative kippen (nicht fundamental gedeckt). RG\u2088-Werte \u00fcber 50 werden aus Gr\u00fcnden der Lesbarkeit als \u201e>50\u201c dargestellt. Der zugrundeliegende Rohwert ist in voller Pr\u00e4zision gespeichert.',
    },
    supportingData: {
      heading: 'Zusatzdaten',
      marketCap: 'Marktkapitalisierung (ca.)',
      tangibleEquity: 'Tangibles Eigenkapital (EK)',
      smoothedEarnings: 'Geglätteter Gewinn G (ann.)',
      netIncome: 'Nettoeinkommen (ca.)',
      fundamentalBase: 'Fundamentale Basis FB\u2081\u2080',
      teApprox: 'EK als Buchwert angenähert (Goodwill/immaterielle Vermögenswerte nicht separat aus der Datenquelle verfügbar).',
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
    downloadJson: 'JSON herunterladen',
    downloadCsv: 'CSV herunterladen',
    downloadNote: 'Vollständiger Datensatz. Nur für Forschungszwecke. Keine Anlageberatung.',
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
      websiteApproximation: {
        heading: 'Operative Näherung auf dieser Website',
        body: [
          'Das Paper definiert G als geglättetes Langfrist-Ertragsmass. Diese Website verwendet eine feste operative Näherung: G_approx = Mittelwert der letzten 8 verfügbaren Quartale, annualisiert (×4). Dasselbe G_approx wird identisch für RG8, RG10 und RG12 verwendet — nur der Kapitalisierungsfaktor N variiert.',
          'Diese Näherung folgt der strukturellen Logik des Papers (ein einziges G, variierendes N), weicht jedoch in zwei Punkten von einer vollständigen Paper-Implementierung ab: (1) Das Glättungsfenster ist auf 8 Quartale fixiert, anstatt ggf. unternehmensspezifisch kalibriert zu sein; (2) wenn weniger als 8 echte Quartalsdaten vorliegen, wird die Reihe mit Jahresdaten geteilt durch 4 ergänzt.',
          'Beobachtungen mit unzureichenden Quartalsdaten werden mit dataType = \"annual\" gekennzeichnet und aus dem historischen Verlaufschart ausgeschlossen. Das Feld smoothedEarnings sowie das Flag teIsApprox werden in jeder Beobachtung explizit gespeichert, sodass die Näherung stets nachvollziehbar bleibt.',
        ],
      },
      dataSources: {
        heading: 'Datenquellen',
        body: [
          'Alle auf dieser Website angezeigten Finanzdaten — einschließlich Marktkapitalisierung, Nettogewinn und tangibles Eigenkapital — werden über yfinance abgerufen, eine Open-Source-Python-Bibliothek, die öffentlich verfügbare Daten von Yahoo Finance bezieht.',
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
