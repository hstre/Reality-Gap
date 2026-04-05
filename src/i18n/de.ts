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

  research: {
    label: 'Explorative Forschung',
    heading: 'Historische Forschung',
    subheading: 'Retrospektive, querschnittliche und sektorale Beobachtungen aus dem aktuellen RG-Datensatz. Vorläufig und approximiert.',
    disclaimer: {
      heading: 'Forschungsvorbehalt',
      body: 'Diese Seite präsentiert explorative Beobachtungen auf Basis eines approximierten, begrenzten Datensatzes. Alle Ergebnisse sind vorläufig. Es werden keine prädiktiven oder kausalen Aussagen getroffen. RG ist ein deskriptiver heuristischer Indikator — kein Prognosemodell und keine Anlageberatung. Stichprobengrößen sind klein, die Datenabdeckung ist partiell, und alle Werte sind Näherungen aus öffentlichen Quellen (yfinance). Bitte keine starken Schlussfolgerungen aus dieser Analyse ziehen.',
    },

    takeaways: {
      heading: 'Was die aktuellen Daten vorläufig nahelegen',
      windowNote: (n: number) => `n = ${n} Unternehmen · historischer Ankerpunkt: 2023 · aktuelle Kurse ca. Anfang 2026 · explorativ`,
      items: [
        { kind: 'suggests', text: 'Niedrig-RG-Unternehmen (untere Hälfte nach RG10) erzielten im Schnitt +83 % vs. +36 % für die obere Hälfte — eine sichtbare Lücke in dieser 71-Unternehmen-Stichprobe über das Fenster 2023→aktuell.' },
        { kind: 'suggests', text: 'P/G (einfacheres Gewinnmultiple) liefert eine nahezu identische Aufteilung (+82 % vs. +34 %). RG10 und P/G haben eine Rangkorrelation von 0,87 — sie messen derzeit eng verwandte Größen.' },
        { kind: 'suggests', text: 'Market-to-Book (M/TE) zeigt ein monotones Quartilsmuster (+93 %, +65 %, +59 %, +37 %) — ein etwas klareres Muster als RG, mit jedoch kleinerem Spread.' },
        { kind: 'limits', text: 'Ausnahmen sind real und häufig. Broadcom (RG10 4,6; +250 %), Alphabet (RG10 0,7; +342 %) und Tesla (RG10 3,0; +93 %) brechen das einfache Muster. Jeder Durchschnitt verbirgt eine breite individuelle Streuung.' },
        { kind: 'open', text: 'Ob RG gegenüber P/G in dieser Stichprobe Zusatzinformation liefert, ist unklar. Dies erfordert den GFC-Zyklus (2007–2009), wo die TE-Variation strukturell anders ist als heute.' },
      ],
      kindLabels: { suggests: 'vorläufig', limits: 'Ausnahme', open: 'offene Frage' },
    },

    metricComparison: {
      heading: '6. RG vs. einfachere Metriken: Retrospektiver Gruppenvergleich',
      subheading: 'Vier Bewertungsmetriken, gemessen am historischen Ankerpunkt 2023 für 71 Unternehmen. Renditen approximieren die Kursentwicklung von diesem Datum bis aktuell (ca. Anfang 2026). Niedrige Gruppe = untere Hälfte nach Metrikwert; Hohe Gruppe = obere Hälfte.',
      sampleNote: 'Rendite = (aktuelle Marktkapitalisierung − Marktkapitalisierung 2023) / Marktkapitalisierung 2023. Marktkapitalisierung als historischer Schlusskurs × aktuelle Aktienanzahl approximiert.',
      comparisonTableHeading: 'Niedrig- vs. Hoch-Gruppe: Ø Approximierte Rendite',
      colMetric: 'Metrik',
      colN: 'n',
      colLowAvg: 'Ø Niedrig-Gruppe',
      colHighAvg: 'Ø Hoch-Gruppe',
      colSpread: 'Spread',
      colRho: 'ρ (Rendite)',
      quartileHeading: 'Quartilsaufschlüsselung',
      colQuartile: 'Quartil',
      colAvgRet: 'Ø Rendite',
      colRange: 'Metrikbereich',
      colN2: 'n',
      metricDescriptions: {
        rg10: 'RG10 — Reality Gap (geglättete Gewinne + EK-Basis)',
        pg:   'P/G — Marktkap. / (G × 10), einfaches Gewinnmultiple',
        mte:  'M/TE — Marktkap. / tangibles Eigenkapital (TE > 0)',
        ey:   'EY — Gewinnrendite: G / Marktkap. × 100 (invertiert)',
      },
      eyNote: 'EY ist invertiert: hohe EY = günstig. Das Gruppierungsmuster ist das Spiegelbild der anderen Metriken.',
      verdictHeading: 'Einschätzung',
      verdictBody: 'RG10 und P/G liefern auf dieser Stichprobe nahezu identische Niedrig-/Hoch-Splits (Spread ~47–49 %). Ihre Rangkorrelation beträgt 0,87 — sie messen eng verwandte Größen. M/TE zeigt einen klareren monotonen Gradienten. EY verhält sich erwartungsgemäß. Ob RG gegenüber P/G Zusatzinformation liefert, lässt sich aus diesem Beobachtungsfenster nicht ableiten.',
      casesHeading: 'Illustrative Einzelfälle',
      casesNote: 'Ausgewählte Beobachtungen aus der retrospektiven Analyse. Nicht repräsentativ — zur Verankerung der Aggregatergebnisse in konkreten Beispielen.',
      colCompany: 'Unternehmen',
      colRG10: 'RG10',
      colPG: 'P/G',
      colMTE: 'M/TE',
      colReturn: '≈ Rendite',
      colCase: 'Falltyp',
      caseTypes: {
        consistent: 'Konsistent mit Muster',
        exception: 'Ausnahme',
        ambiguous: 'Mehrdeutig',
      },
    },

    indexSection: {
      heading: '1. Indexvergleich (Momentaufnahme)',
      note: 'Median-RG10 und Interquartilsabstand je Index für die aktuellste Quartalsbeobachtung pro Unternehmen. Nur Unternehmen mit gültigem, nicht grenzwertigem RG10 einbezogen.',
      colIndex:  'Index',
      colN:      'n',
      colP25:    'P25',
      colMedian: 'Median RG10',
      colP75:    'P75',
      footnote:  'Ein höherer RG10 deutet darauf hin, dass der Markt ein größeres Vielfaches der Fundamentalbasis bewertet. Ob dies Überbewerung, erwartetes Gewinnwachstum oder strukturelle Unterschiede zwischen den Märkten widerspiegelt, lässt sich allein aus RG nicht bestimmen.',
    },
    distribution: {
      heading: '2. Aktuelle RG10-Verteilung',
      note: 'Verteilung des aktuellsten RG10 über {n} von {total} erfassten Unternehmen. {notCovered} als „fundamental nicht abgedeckt" klassifiziert (FB ≤ 0 für alle N). {nearBoundary} als grenzwertig markiert und von der Verteilung ausgeschlossen.',
      medianLabel: 'Median',
      footnote:    'RG10 = Marktkapitalisierung / Fundamentale Basis (N=10). Geglätteter Gewinn G aus den letzten 8 Quartalen approximiert. US-Unternehmen inflationsbereinigt (CPI-real). Alle Werte approximiert.',
    },
    sectors: {
      heading: '3. Sektorvergleich',
      note: 'Median-RG10 je Sektor. Balkenlänge entspricht dem Median; n = Anzahl Unternehmen. Sektoren mit weniger als 3 Unternehmen sollten mit besonderer Vorsicht interpretiert werden.',
      footnote: 'Sektorunterschiede können strukturelle Merkmale widerspiegeln (Kapitalintensität, immaterielle Werte, Verschuldung) und nicht notwendigerweise relative Bewertungsstreckung. Sektoren gemäß Datensatz-Klassifizierung.',
    },
    timeSeries: {
      heading: '4. Querschnittliche Zeitreihe',
      note: 'Median-RG10 und Interquartilsabstand über alle qualifizierenden Quartalsbeobachtungen je Periode. Nur Perioden mit ≥ 15 qualifizierenden Unternehmen werden angezeigt. Dies ist kein Paneldatensatz — die Unternehmenszusammensetzung variiert je Periode.',
      colPeriod:  'Periode',
      colN:       'n',
      colP25:     'P25',
      colMedian:  'Median RG10',
      colP75:     'P75',
      noData:     'Unzureichende Daten für Zeitreihe (weniger als 15 qualifizierende Unternehmen pro Periode).',
      footnote:   'Der Datensatz umfasst nur 4 aktuelle Quartale an Quartalsdaten sowie eine begrenzte Anzahl historischer Jahresbeobachtungen. Keine belastbaren Trendschlüsse aus dieser Stichprobe möglich.',
    },
    fragility: {
      heading: '5. Bewertungsfragilität und Divergenz',
      subheading: 'Trennt sich das obere RG-Segment im Zeitverlauf vom konservativen Kern? Eine wachsende Divergenz kann auf zunehmende Bewertungsfragilität hinweisen — strukturelle Anfälligkeit für abrupte Neubewertungen.',
      panelNote: (n: number, periods: number, method: string) =>
        `Balanciertes Panel von ${n} Unternehmen mit gültigem RG10 in allen ${periods} Zielperioden. Gruppierung: ${method}.`,
      methodQuartile: 'unteres Quartil = Conservative RG Group; oberes Quartil = High-RG Group',
      methodThird: 'unteres Drittel = Conservative RG Group; oberes Drittel = High-RG Group',
      dataTypeNote: 'GJ 2023 und GJ 2024 verwenden historische Schlusskurse (Jahresbeobachtungen). Q1–Q4 2025 verwenden die aktuelle Marktkapitalisierung (Stand Datenabruf, ca. Anfang 2026) — Variation innerhalb 2025 spiegelt Änderungen im geglätteten Gewinn G wider, keine Quartalspreisentwicklung.',
      signalHeading: 'Fragilitäts-Momentaufnahme',
      peakSpreadLabel: 'Spitze RG Fragility Spread',
      currentSpreadLabel: 'Aktueller RG Fragility Spread',
      peakRatioLabel: 'Spitze RG Fragility Ratio',
      currentRatioLabel: 'Aktuelle RG Fragility Ratio',
      divergenceChartHeading: 'Conservative vs. High-RG Median im Zeitverlauf',
      divergenceLegendCons: 'RG Conservative Median',
      divergenceLegendHigh: 'RG High Median',
      spreadChartHeading: 'RG Fragility Spread im Zeitverlauf',
      ratioChartHeading: 'RG Fragility Ratio im Zeitverlauf',
      tableHeading: 'Vollständige Fragilitätskennzahlen je Periode',
      colPeriod: 'Periode',
      colType: 'Daten',
      colConsMedian: 'Cons. Median',
      colHighMedian: 'High Median',
      colSpread: 'Spread',
      colRatio: 'Ratio',
      colSpreadChange: 'Spread Δ',
      colRatioChange: 'Ratio Δ',
      colUpperTail: '>3,0 Anteil',
      peakAnnotation: 'Spitze',
      annualLabel: 'jährlich',
      quarterlyLabel: 'quartalsweise',
      interpretation: {
        heading: 'Wie die RG-Divergenz zu lesen ist',
        items: [
          {
            title: 'Steigender Spread oder Ratio',
            body: 'Eine wachsende Lücke zwischen dem High-RG- und dem Conservative-RG-Median deutet darauf hin, dass die fundamentalsfernsten Bewertungen sich vom verankerten Kern entfernen. Im vorliegenden Datensatz erreichte der Fragility Spread in GJ 2024 seinen Höchststand — ca. 45 % über dem GJ-2023-Niveau.',
          },
          {
            title: 'Schnelles Divergenzwachstum',
            body: 'Beschleunigtes Spread-Wachstum — wie von GJ 2023 auf GJ 2024 beobachtet — kann auf zunehmende spekulative Konzentration im High-RG-Segment hinweisen. Dies beweist keinen Absturz oder eine Korrektur, erhöht aber die strukturelle Anfälligkeit, wenn die Divergenz nicht durch Gewinnwachstum gedeckt werden kann.',
          },
          {
            title: 'Nachfolgende Kontraktion',
            body: 'Der Fragility Spread ist von seinem GJ-2024-Höchststand deutlich auf das aktuelle Niveau zurückgegangen. Der konservative Kern stieg leicht an, das High-RG-Segment fiel signifikant. Dies ist konsistent mit einer Neubewertung der am stärksten überbewerteten Namen, wobei die kausale Interpretation unklar bleibt.',
          },
          {
            title: 'Was dies nicht beweist',
            body: 'Diese Analyse belegt nicht, dass RG-Fragilität ein Marktereignis vorhergesagt hat. Der Datensatz ist klein (31 Panel-Unternehmen), umfasst nur drei aussagekräftige historische Punkte und verwendet approximierte Marktkapitalisierungsdaten. Es werden keine kausalen, prädiktiven oder anlagerelevanten Aussagen gemacht.',
          },
        ],
      },
      limitationNote: 'Panel-Einschränkung: Nur 31 von 77 erfassten Unternehmen erscheinen in allen 6 Zielperioden. Das balancierte Panel überrepräsentiert Unternehmen mit konsistenter Geschäftsjahresausrichtung. Jahres- (GJ 2023, GJ 2024) und Quartalsperioden (2025) verwenden strukturell unterschiedliche Marktkapitalisierungsquellen — dies ist ein methodischer Bruch in der Zeitreihe, kein kontinuierliches Panel.',
    },

    useCases: {
      heading: '7. Mögliche Anwendungsfelder historischer RG-Analysen',
      items: [
        {
          title: 'Marktweite Bewertungsstreckung',
          body: 'Ein dauerhaft steigender Median-RG über mehrere Jahre könnte darauf hindeuten, dass sich Marktpreise zunehmend von Fundamentalbasen entfernen — ein Muster ähnlich dem Shiller-CAPE. Mit dem aktuellen 4-Quartals-Datensatz lässt sich dies nicht beurteilen.',
        },
        {
          title: 'Sektorrotationssignale',
          body: 'Unterschiede im Median-RG zwischen Sektoren können unterschiedliche Markterwartungen hinsichtlich Gewinnwachstum, Kapitalintensität oder Risiko widerspiegeln. Anhaltend hohe RG-Sektoren könnten in einer längeren historischen Studie näher untersucht werden.',
        },
        {
          title: 'Retrospektive Sortierungsanalyse',
          body: 'Bei ausreichend langer Zeitreihe ließe sich prüfen, ob Unternehmen mit historisch hohem RG-Quartil eine andere Kursentwicklung zeigten. Dies entspricht dem Ansatz akademischer Faktorforschung. Der aktuelle Datensatz ist für eine solche Analyse zu klein und zu kurzfristig.',
        },
        {
          title: 'Dispersion als Blasenindikator',
          body: 'Eine wachsende Streuung zwischen hohem und niedrigem RG — oder eine rasche Ausweitung des oberen Quartils — könnte als explorativer Hinweis auf konzentrierte Bewertungsstreckung dienen. Dies erfordert mehrjährige historische Daten, die in diesem Datensatz noch nicht verfügbar sind.',
        },
      ],
    },
    coverage: {
      heading: '8. Stand der historischen Datenbasis',
      subheading: 'Der aktuelle RG-Datensatz deckt nur einen kurzen modernen Ausschnitt der Marktgeschichte ab. Die beiden wichtigsten historischen Stresstests — der Dot-com-Zyklus und die globale Finanzkrise — liegen außerhalb des aktuellen Beobachtungsfensters. Dieser Abschnitt dokumentiert die Datenlücke, welche Teilbestände bereits vorhanden sind und was jede Erweiterungsphase erfordert.',
      currentSliceNote: 'Aktuelles Beobachtungsfenster: nur 2023–2026. Alle Fragilitäts- und Retrospektivanalysen auf dieser Seite basieren auf diesem engen modernen Zeitraum. Keine Schlussfolgerungen über langfristiges RG-Verhalten oder historische Krisendynamiken können aus diesem Fenster abgeleitet werden.',
      timelineHeading: 'Datenbasis-Zeitstrahl (1995–2026)',
      timelineLegend: {
        missing: 'Keine Daten — Forschungsziel',
        partial: 'Nur Erträge/Eigenkapital (keine Marktkapitalisierung)',
        full: 'Vollständige Abdeckung (aktuell)',
      },
      phasesHeading: 'Erforderliche Erweiterungsphasen',
      phases: [
        {
          id: 'dotcom',
          label: 'Phase 1: Dot-com-Zyklus',
          period: '1995–2003',
          subPeriods: [
            { label: 'Vorbereitende Blasenbildung', years: '1995–1999' },
            { label: 'Spitze', years: '1999–2000' },
            { label: 'Kollaps', years: '2000–2002' },
            { label: 'Nachgang', years: '2002–2003' },
          ],
          status: 'missing',
          statusLabel: 'Keine Daten — Datenakquisition erforderlich',
          dataAvailable: 'Keine Daten in der aktuellen Datenbank. Die SEC-XBRL-Pflicht begann erst 2007–2009. Ertrags- und Eigenkapitaldaten vor 2007 sind über die SEC-API nicht verfügbar.',
          dataNeeded: 'Quartalsweise Nettoergebnisse, Eigenkapital, Goodwill und immaterielle Werte für die 30 US-Unternehmen (S&P-500-Teilmenge) von 1995–2003. Historische Schlusskurse für die Marktkapitalisierungsberechnung. Für nicht-US-Unternehmen wären separate Datenquellen erforderlich.',
          acquisitionPath: 'Alternative Quellen erforderlich: Compustat/WRDS (akademische Lizenz), Calcbench oder manuelle Erhebung aus archivierten 10-K/10-Q-Berichten via SEC EDGAR. Diese Phase erfordert erhebliche neue Dateninfrastruktur.',
        },
        {
          id: 'gfc',
          label: 'Phase 2: Globale Finanzkrise',
          period: '2004–2011',
          subPeriods: [
            { label: 'Aufbau vor der Krise', years: '2004–2007' },
            { label: 'Maximale Fragilität', years: '2007' },
            { label: 'Kollaps', years: '2007–2009' },
            { label: 'Nachgang', years: '2009–2011' },
          ],
          status: 'partial',
          statusLabel: 'Ertrags-/Eigenkapitaldaten vorhanden — historische Kurse fehlen',
          dataAvailable: 'Die SEC-XBRL-Fundamentaldatenbank (fundamentals.db) enthält quartalsmäßige Nettoergebnisse, Eigenkapital, Goodwill und immaterielle Werte für 30 US-S&P-500-Unternehmen ab 2007. Die Abdeckung wächst von ~20 Titeln im Jahr 2007 auf 26–30 Titel bis 2009.',
          dataNeeded: 'Historische Schlusskurse und ausstehende Aktien zum jeweiligen Geschäftsperiodenenddatum für alle 30 US-Titel von 2004–2011. Dies ist das einzige fehlende Element für US-Unternehmen. Für Nikkei-225- und DAX-40-Unternehmen gibt es für diesen Zeitraum keine historische Datenquelle.',
          acquisitionPath: 'Historische Kurse sind über yfinance abrufbar (bereits in fetch_data.py integriert). Nächster Schritt: historischen Abruf auf 2004–2011-Periodenenden ausweiten, Kurse in fundamentals.db speichern, dann G und RG aus fundamentals.db berechnen. Geschätzter Umfang: moderate Ingenieurarbeit, keine neuen Datenlizenzen für US-Unternehmen erforderlich.',
        },
        {
          id: 'modern',
          label: 'Phase 3: Erweiterte moderne Geschichte',
          period: '2012–2022',
          subPeriods: [],
          status: 'partial',
          statusLabel: 'Ertrags-/Eigenkapitaldaten vorhanden — historische Kurse fehlen',
          dataAvailable: 'fundamentals.db hat nahezu vollständige Abdeckung für alle 30 US-Titel über diesen Zeitraum. Jahresdaten für Nikkei-225- und DAX-40-Unternehmen sind über yfinance teilweise verfügbar, wurden aber noch nicht systematisch erfasst.',
          dataNeeded: 'Historische Schlusskurse für US-Titel (2012–2022) und erweiterte Abdeckung nicht-US-amerikanischer Unternehmen. Historische EK-Daten anstelle der aktuellen EK-Snapshots, die in der vorliegenden Näherung verwendet werden.',
          acquisitionPath: 'Identisch mit Phase 2. Primär eine Abruf-und-Berechnungsaufgabe.',
        },
      ],
      fundamentalsDbNote: 'Eine SEC-XBRL-Fundamentaldatenbank (fundamentals.db) ist bereits vorhanden und deckt 30 US-Unternehmen von 2007 bis heute mit ~3.025 Zeilen ab. Dies ist die Grundlage für die Erweiterungsphasen 2 und 3. Das fehlende Element für alle historischen RG-Berechnungen sind historische Marktkapitalisierungsdaten, die historische Schlusskurse zu jedem Geschäftsperiodenende erfordern.',
      whatWeWouldSee: 'Was die historischen Stresstests zeigen würden',
      whatWeWouldSeeItems: [
        {
          title: 'Dot-com-Spitze (1999–2000)',
          body: 'RG-Fragility-Spread und -Ratio dürften extreme Werte erreicht haben — insbesondere in Technologie und Telekommunikation. Die Gewinne waren bei vielen Highflyern gering bis negativ; die Marktkapitalisierungen enorm. RG-Werte für Namen wie Cisco, Sun Microsystems oder WorldCom wären wahrscheinlich unmessbar oder zeigen sehr hohe Quotienten.',
        },
        {
          title: 'Vor-GFC-Spitze (2006–2007)',
          body: 'Finanzwerte und Immobilienunternehmen zeigten wahrscheinlich hohe RG-Werte aufgrund von Verschuldung und Vermögensinflation. Konservative Industrie- und Konsumgüterunternehmen zeigten wahrscheinlich niedrige RG-Werte. Der Fragility Spread in diesem Zeitraum ist die zentrale Forschungshypothese: Erreichte die RG-Divergenz kurz vor der Krise ihren Höchststand?',
        },
        {
          title: 'Nachkrisen-Normalisierung (2009–2012)',
          body: 'Nach dem Einbruch 2008–2009 sanken die Gewinne stark und die Marktkapitalisierungen fielen. Ob der RG-Spread komprimierte — wie im aktuellen Datensatz nach dem 2024er-Höchststand — oder trotz niedrigerer Kurse erhöht blieb, ist eine der offenen Forschungsfragen.',
        },
      ],
      disclaimer: 'Keines der obigen Muster ist ein bewiesenes Muster. Es handelt sich um Forschungshypothesen, die tatsächliche historische Daten zur Überprüfung erfordern. Die Dot-com- und GFC-Perioden stellen die wichtigsten Validierungsziele für das RG-Fragilitäts-Framework dar.',
    },

    limitations: {
      heading: '9. Datenbeschränkungen',
      items: [
        'Abdeckung: 77 Unternehmen aus drei Indizes (S&P 500 Top 30, Nikkei 225 Top 19, DAX 40 Top 28). Dies ist keine vollständige Indexabdeckung. Ergebnisse lassen keine indexweiten Schlüsse zu.',
        'Gewinnglättung: G wird als Mittelwert der letzten 8 verfügbaren Quartals-Nettoergebnisse annualisiert approximiert. Dies ist eine operative Vereinfachung; das Paper definiert G strenger.',
        'Tangibles Eigenkapital: EK kann auf Buchwert zurückgreifen, wenn Goodwill und immaterielle Werte aus der Datenquelle (yfinance) nicht separat verfügbar sind. Betroffene Beobachtungen sind mit teIsApprox = true markiert.',
        'CPI-Bereinigung für US-Unternehmen: Inflationsbereinigung verwendet FRED CPIAUCSL. Nicht-US-Unternehmen verwenden nominale Gewinne, was die Indexvergleichbarkeit einschränkt.',
        'Historische Marktkapitalisierung: Jahreshistorische Beobachtungen verwenden historischen Schlusskurs × aktuelle Aktienanzahl. Änderungen der Aktienanzahl werden nicht berücksichtigt.',
        'Historisches tangibles Eigenkapital: Jahreshistorische Beobachtungen verwenden den aktuellen EK-Snapshot (nicht historisch). Dies führt zu einer Approximation in allen historischen jährlichen RG-Werten.',
        'Keine geprüften Daten: Alle Werte sind aus yfinance / Yahoo Finance öffentlichen Daten abgeleitet. Abweichungen von geprüften Jahresabschlüssen sind möglich.',
        'Keine prädiktive Validierung: RG wurde nicht als prädiktiver Indikator validiert. Der Zusammenhang zwischen RG-Werten und künftigen Renditen ist unbekannt.',
      ],
    },
  },
} as const;

export type DeTranslations = typeof de;
