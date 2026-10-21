# Content migration audit

Source: public WordPress pages and posts at dundasvets.com, captured October 21, 2026.

16 published pages and 8 complete articles retained. Seven service detail pages, four doctors and their original photographs, hospital history, both locations, original opening-hour rows, all eight homepage review excerpts and all eight articles are present.

| Source slug | Original URL | Demo path | Result |
|---|---|---|---|
| home | https://dundasvets.com/ | /dundas-east-animal-hospital/ | Migrated; filler sentences omitted, original snapshot retained |
| surgical-services | https://dundasvets.com/surgical-services/ | /dundas-east-animal-hospital/surgical-services/ | Migrated |
| dentistry-services | https://dundasvets.com/dentistry-services/ | /dundas-east-animal-hospital/dentistry-services/ | Migrated |
| reference-laboratory-testing | https://dundasvets.com/reference-laboratory-testing/ | /dundas-east-animal-hospital/reference-laboratory-testing/ | Migrated |
| in-house-medical-imaging | https://dundasvets.com/in-house-medical-imaging/ | /dundas-east-animal-hospital/in-house-medical-imaging/ | Migrated |
| in-house-laboratory-diagnostics | https://dundasvets.com/in-house-laboratory-diagnostics/ | /dundas-east-animal-hospital/in-house-laboratory-diagnostics/ | Migrated |
| laser-surgery | https://dundasvets.com/laser-surgery/ | /dundas-east-animal-hospital/laser-surgery/ | Migrated |
| wellness-and-preventive-care | https://dundasvets.com/wellness-and-preventive-care/ | /dundas-east-animal-hospital/wellness-and-preventive-care/ | Migrated |
| team | https://dundasvets.com/team/ | /dundas-east-animal-hospital/team/ | Migrated |
| contact-us | https://dundasvets.com/contact-us/ | /dundas-east-animal-hospital/contact-us/ | Migrated |
| blog | https://dundasvets.com/blog/ | /dundas-east-animal-hospital/blog/ | Migrated |
| 404-2 | https://dundasvets.com/404-2/ | /dundas-east-animal-hospital/404-2/ | Retained for review: unfinished template |
| faq | https://dundasvets.com/faq/ | /dundas-east-animal-hospital/faq/ | Retained for review: unfinished template |
| service-detail | https://dundasvets.com/service-detail/ | /dundas-east-animal-hospital/service-detail/ | Retained for review: unfinished template |
| services | https://dundasvets.com/services/ | /dundas-east-animal-hospital/services/ | Retained for review: unfinished template |
| about-us | https://dundasvets.com/about-us/ | /dundas-east-animal-hospital/about-us/ | Migrated |
| how-weather-changes-affect-your-pets-health | https://dundasvets.com/how-weather-changes-affect-your-pets-health/ | /dundas-east-animal-hospital/how-weather-changes-affect-your-pets-health/ | Migrated |
| pet-allergies-symptoms-causes-and-treatments | https://dundasvets.com/pet-allergies-symptoms-causes-and-treatments/ | /dundas-east-animal-hospital/pet-allergies-symptoms-causes-and-treatments/ | Migrated |
| understanding-common-skin-conditions-in-pets | https://dundasvets.com/understanding-common-skin-conditions-in-pets/ | /dundas-east-animal-hospital/understanding-common-skin-conditions-in-pets/ | Migrated |
| spay-or-neuter-what-every-pet-owner-should-consider | https://dundasvets.com/spay-or-neuter-what-every-pet-owner-should-consider/ | /dundas-east-animal-hospital/spay-or-neuter-what-every-pet-owner-should-consider/ | Migrated |
| the-ultimate-guide-to-puppy-and-kitten-care | https://dundasvets.com/the-ultimate-guide-to-puppy-and-kitten-care/ | /dundas-east-animal-hospital/the-ultimate-guide-to-puppy-and-kitten-care/ | Migrated |
| why-annual-vet-checkups-can-save-youre-your-pets-life | https://dundasvets.com/why-annual-vet-checkups-can-save-youre-your-pets-life/ | /dundas-east-animal-hospital/why-annual-vet-checkups-can-save-youre-your-pets-life/ | Migrated |
| vaccinations-for-pets-what-every-pet-parent-must-know | https://dundasvets.com/vaccinations-for-pets-what-every-pet-parent-must-know/ | /dundas-east-animal-hospital/vaccinations-for-pets-what-every-pet-parent-must-know/ | Migrated |
| 10-signs-your-pet-needs-to-see-a-vet-dont-ignore-them | https://dundasvets.com/10-signs-your-pet-needs-to-see-a-vet-dont-ignore-them/ | /dundas-east-animal-hospital/10-signs-your-pet-needs-to-see-a-vet-dont-ignore-them/ | Migrated |

## Explicit treatment of source issues

- `content/original-content.json` preserves every page/post’s complete visible text and safe semantic HTML, including placeholders. Original scripts, styling, tracking and executable forms are intentionally not imported.
- The original `faq`, `services`, `service-detail` and `404-2` routes contain unfinished template text. Every word remains accessible in a labelled original-content disclosure; the services route additionally provides the real service directory. Template phone numbers, $25 prices, free medicine and 24/7 claims are not presented as verified clinic facts.
- The homepage no-content message and lorem ipsum sentence are omitted from its presentation, retained in the source snapshot.
- About-page template headings (including pet shelter facility) remain in the original page content; their accompanying lorem ipsum is visibly labelled by the source-review notice added during QA.
- Dundas weekday and separate Wednesday hours conflict. Both source rows are visible; no opening-hours schema is emitted pending clinic confirmation. No Sunday hours are invented.
- Google reviews and their count are an original-site snapshot, clearly labelled; no aggregate-rating schema is emitted.
- Original social icons point to #, so labels remain in the contact source disclosure without invented profiles.
- All original service/article slugs are preserved. /home/ canonicalizes to /. The existing category and author archive URLs have local routes listing the same eight posts. The public sitemap was cross-checked: all 24 page/post URLs and both archive URLs are covered.
- The static demo does not send appointment forms or process payments; phone/email contacts remain functional.
