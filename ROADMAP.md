# Roadmap & Future Enhancements

Plán vývoje projektu StoreChecker.

## 🚀 Version 1.0 - MVP (Aktuální)

- [x] Scrapery pro 5 řetězců (Tesco, Penny, Billa, Albert, Kaufland)
- [x] SQLite databáze pro ukládání a sledování historií
- [x] Email notifikace s HTML a textovými formáty
- [x] APScheduler pro plánované běhy
- [x] CLI interface (--once, --schedule)
- [x] Podrobná dokumentace
- [x] Change tracking (nové, zavřené, opět otevřené sklady)

## 📋 Version 1.1 - Stability & Polish

Plánované:
- [ ] Unit testy pro scrapery a databázi
- [ ] Integrační testy
- [ ] Retry mechanika pro flaky síť
- [ ] Lepší error handling
- [ ] Configuration validation
- [ ] Logging improvements
- [ ] Performance optimizations

Timeline: 2-4 týdny

## 🎨 Version 1.2 - Web Dashboard

Plánované:
- [ ] Flask/FastAPI backend
- [ ] HTML dashboard pro prohlížení skladu
- [ ] Filtrování po městě, řetězci, statusu
- [ ] Statistiky a grafy
- [ ] Search across all stores
- [ ] Store details page
- [ ] Change history timeline

Timeline: 4-6 týdnů

## 📱 Version 1.3 - Multi-Channel Notifications

Plánované:
- [ ] Telegram notifikace
- [ ] Slack integration
- [ ] SMS notifikace (Twilio)
- [ ] Push notifications (Web Push API)
- [ ] Discord webhook
- [ ] Notification templates/preferences
- [ ] Quiet hours (nevzbudzet v noci)

Timeline: 3-4 týdny

## 🌐 Version 2.0 - Advanced Features

Plánované:
- [ ] Geografické filtrování (najít sklady poblíž)
- [ ] Store comparison (mezi řetězci)
- [ ] Analytics & insights
- [ ] Machine learning pro predikci uzavření
- [ ] Backup notifications (pokud primární selže)
- [ ] API pro integraci
- [ ] Mobile aplikace

Timeline: 6+ měsíců

## 🔧 Technical Debt & Improvements

Pro všechna vydání:
- [ ] Aktualizovat CSS selektory v scrapery (URGENT!)
- [ ] Přidat Selenium fallback pro JS-heavy sites
- [ ] Refactor database schema pro horší scalability
- [ ] Add caching layer (Redis?)
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Automated testing on schedule
- [ ] Performance benchmarking

## 🐛 Known Issues & Limitations

Aktuální známé problémy:

1. **CSS selektory jsou placeholdery**
   - Musí se aktualizovat pro skutečné fungování
   - Priorita: CRITICAL ⚠️

2. **Scrapery nemběží asynchronně**
   - Lineární spouštění trvá déle
   - Plán: Async scraping v 1.1

3. **Bez unit testů**
   - Riziková refaktorování
   - Plán: 1.1

4. **Limitované error handling**
   - Síťové chyby nejsou resilientní
   - Plán: 1.1

5. **Bez rate limitingu**
   - Může být zablokován webem
   - Plán: 1.1

6. **Databáze není optimalizovaná**
   - Pomalé pro 1000s záznamů
   - Plán: 2.0

## 🎯 High Priority Items

Ihned potřebnější:

1. **Vytvořit funkční scrapery** ⭐⭐⭐
   - CSS selektory z aktuálních webů
   - Selenium pro JS-heavy sites
   - Testování na 100+ skladům

2. **E2E testy** ⭐⭐⭐
   - Testovací běh pro všechny řetězce
   - Ověření emailu

3. **Dokumentace pro aktualizaci selektorů** ⭐⭐
   - SCRAPER_GUIDE.md je dobrý start
   - Potřebuji video tutoriál?

4. **Error handling** ⭐⭐
   - Network timeouts
   - Bad HTML parsing
   - SMTP failures

## 💡 Community Suggestions

Překvapivé nápady:

- Kombinovat s Google Maps API pro polohu
- Srovnávat ceny (pokud dostupné)
- Integrace s calendarovými notifikacemi
- Browser extension
- Slack bot pro dotazy
- Analytics pro studium vzorů zavírání

## 📊 Success Metrics

Chci dosáhnout:

- [ ] 5+ akyních řetězců
- [ ] 500+ sledovaných skladů
- [ ] <5min čas na běh weekly checku
- [ ] 99% email delivery rate
- [ ] <1MB database na rok
- [ ] <100 LOC per scraper
- [ ] 50+ GitHub stars

## 🤝 Contributing to Roadmap

Máte nápad? Chcete pomoci?

1. Otevřete GitHub Issue
2. Diskutujte design
3. Implementujte
4. Odešlete PR

Viz [CONTRIBUTING.md](CONTRIBUTING.md).

## 📞 Contact & Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: [your-email]@example.com
- **Documentation**: Viz [README.md](README.md)

---

**Poslední aktualizace**: Březen 2024

Děkujeme za zájem o StoreChecker! 🚀
