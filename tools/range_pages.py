"""Build one SEO landing page per product range.

Usage: python3 tools/range_pages.py
Writes <slug>/index.html for every entry in RANGES, using sunscreen-manufacturer/index.html
as the shared layout (header, footer, schema, styles), and adds the URLs to sitemap.xml.
Brand rules: name only Numour and Just Herbs as clients; no competitor names; no claims
beyond what the site and test reports support.
"""
import json, re, html, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = open(os.path.join(ROOT, "sunscreen-manufacturer/index.html"), encoding="utf-8").read()
BASE = "https://www.ecosmetix.in"
TODAY = datetime.date.today().isoformat()

def esc(s):
    return html.escape(s, quote=True)

RANGES = [
 dict(slug="baby-care-products-manufacturer", name="Baby care manufacturing", hero="baby.webp", pack="baby-care",
  title="Baby Care Products Manufacturer India | Ecosmetix",
  desc="Third-party baby care products manufacturer in India: mild baby wash, shampoo, lotion, cream, oil and diaper rash cream. Private label and custom R&D.",
  h1="Baby care products manufacturer for brands in India",
  lead="Mild, carefully chosen formulas for delicate baby skin, developed by our R&D team and manufactured under one roof in Ambala.",
  intro="Parents read every label, so a baby care launch has to get the base right: gentle cleansing systems, short ingredient lists and a soft sensorial feel. Ecosmetix develops and manufactures baby care for D2C and established brands, either from our ready private label formulas or built around your own brief. We help you choose fragrance-free or mild-fragrance options, the right packs and the claims your test reports can support.",
  make=["Baby wash and 2-in-1 shampoo and wash","Baby shampoo","Baby lotion and baby cream","Baby massage oil and baby oil","Diaper rash cream","Baby powder-free soothing balm"],
  actives=["Mild amino-acid and glucoside surfactants","Natural butters","Ceramides","Panthenol","Calendula","Plant oils"],
  faqs=[("Do you make fragrance-free baby products?","Yes. Every baby formula can be made fragrance-free or with a mild, baby-appropriate fragrance."),
        ("Can baby products carry 'dermatologically tested'?","Only when a test report for your final formula is on file. We help arrange safety and tolerance testing so the claim on your pack is supported."),
        ("Can I launch a full baby range at once?","Yes. Wash, shampoo, lotion, cream, oil and diaper cream can be developed as one matched range with shared packaging."),
        ("What is the MOQ for baby care?","MOQ depends on product and pack size. Share your SKU sizes and launch volume in the brief and we confirm MOQ and costing.")],
  related=["kids-care-products-manufacturer","pregnancy-care-products-manufacturer","body-lotion-manufacturer"]),

 dict(slug="kids-care-products-manufacturer", name="Kids care manufacturing", hero="baby.webp", pack="kids-care",
  title="Kids Care Products Manufacturer India | Ecosmetix",
  desc="Kids care products manufacturer in India: mild kids shampoo, body wash, lotion, face cream, sunscreen and lip balm. Private label and custom formulation.",
  h1="Kids care products manufacturer: mild, fun and brand-ready",
  lead="Shampoos, washes, lotions and sun care for children aged 3 to 12, with playful fragrances and packs that parents trust.",
  intro="Kids care sits between baby and adult ranges: children need mild formulas, while the products themselves can be colourful and fun. We develop kids shampoo, conditioner, body wash, lotion, face cream, sunscreen and lip balm with gentle cleansing systems and soft textures. Brands can start from our private label formulas or brief a custom range, and we support packaging, artwork and claim checks before launch.",
  make=["Kids shampoo and conditioner","Kids body wash and bubble bath","Kids body lotion and face cream","Kids sunscreen","Kids lip balm","Detangling sprays and leave-in conditioners"],
  actives=["Mild surfactant blends","Glycerin and hyaluronic acid","Shea butter","Panthenol","Aloe vera","Zinc oxide (sun care)"],
  faqs=[("How is kids care different from baby care?","Kids formulas stay mild but can use more playful fragrances, colours and textures, and cover needs such as detangling and outdoor sun care."),
        ("Can you make a kids sunscreen?","Yes. We build kids sun care on our mineral zinc oxide base. SPF and PA on the pack must match the test certificate for your batch."),
        ("Can the packs carry cartoon characters?","Yes, using your own original artwork. We check artwork and label compliance before production."),
        ("Do you offer private label kids products?","Yes. Ready formulas shorten launch time; you can still customise fragrance, colour and pack.")],
  related=["baby-care-products-manufacturer","teen-skin-care-manufacturer","shampoo-manufacturer"]),

 dict(slug="teen-skin-care-manufacturer", name="Teen skin care manufacturing", hero="model_blue.webp", pack="teen-care",
  title="Teen Skin Care Manufacturer India | Ecosmetix",
  desc="Teen skin care manufacturer in India: gentle face wash, oil-control moisturiser, anti-acne serum, pimple patches and light sunscreen. Graded ranges.",
  h1="Teen skin care manufacturer for first-routine brands",
  lead="Simple, gentle routines for young and oily skin: cleanse, treat, moisturise and protect.",
  intro="Teen skin care is about building a first routine that works without irritating young skin. Ecosmetix develops gentle face washes, oil-control moisturisers, clarifying serums, pimple patches and lightweight sunscreens for teen-focused brands. Our graded system lets you pick milder Grade 1 and 2 formulas for daily care, with encapsulated actives such as salicylic acid for lower irritation.",
  make=["Gentle gel and foam face wash","Oil-control gel moisturiser","Clarifying serum","Hydrocolloid pimple patches","Lightweight sunscreen","Lip care"],
  actives=["Encapsulated salicylic acid","Niacinamide","Zinc PCA","Azelaic Z-Pods","Centella","Hyaluronic acid"],
  faqs=[("Which grades suit teen skin?","Grade 1 and Grade 2 formulas are usually the starting point: gentle actives for daily use, with Grade 3 options for persistent concerns."),
        ("Can you build a complete teen routine?","Yes: cleanser, serum, moisturiser, sunscreen and pimple patches developed as one matched line."),
        ("Do you use encapsulated actives?","Yes. Encapsulated and controlled-release actives help keep formulas gentler on young skin."),
        ("How fast can I launch?","A lab sample is typically ready within 14 days of an approved brief; private label formulas can be faster.")],
  related=["anti-acne-products-manufacturer","pimple-patch-manufacturer","face-wash-manufacturer"]),

 dict(slug="pregnancy-care-products-manufacturer", name="Pregnancy care manufacturing", hero="pregnancy.webp", pack="pregnancy-care",
  title="Pregnancy Care Products Manufacturer India | Ecosmetix",
  desc="Pregnancy and mother care products manufacturer in India: belly butter, stretch mark cream and oil, body lotion and nipple butter. Private label and R&D.",
  h1="Pregnancy and mother care products manufacturer",
  lead="Nourishing butters, creams and oils for changing skin during and after pregnancy.",
  intro="Mother care brands need formulas that feel indulgent and are chosen with care. Ecosmetix develops belly butters, stretch mark creams and oils, body lotions and nipple butters, using rich butters and our HyaSphere Revive technology. We offer fragrance-free options, support safety testing for your final formula, and keep every claim tied to evidence on file.",
  make=["Belly butter","Stretch mark cream","Stretch mark oil","Body lotion for mothers","Nipple butter","Gentle body wash"],
  actives=["HyaSphere Revive","Murumuru butter","Cocoa butter","Shea butter","Centella","Plant oils"],
  faqs=[("Are pregnancy products fragrance-free?","They can be. Most mother care brands choose fragrance-free or very mild fragrance, and we develop either."),
        ("Can I claim 'reduces stretch marks'?","Only with supporting study data. We help you word claims on appearance, such as 'helps improve the look of skin', unless you have test results."),
        ("Which technologies do you use?","Our pregnancy range uses HyaSphere Revive with murumuru and cocoa butters for rich nourishment."),
        ("Can you pair this with a baby range?","Yes. Many brands launch mother and baby care together; see our baby care page.")],
  related=["baby-care-products-manufacturer","body-lotion-manufacturer","private-label-cosmetics-manufacturer"]),

 dict(slug="face-serum-manufacturer", name="Face serum manufacturing", hero="serum_teal.webp", pack="face-serum",
  title="Face Serum Manufacturer India | Liposomal Serums | Ecosmetix",
  desc="Face serum manufacturer in India: niacinamide, vitamin C, retinol, peptide and hydrating serums on liposomal and encapsulated delivery. Private label and R&D.",
  h1="Face serum manufacturer with advanced delivery systems",
  lead="Serums built delivery-system first: liposomal, microsponge and encapsulated actives for stability and gentler release.",
  intro="A serum is only as good as how its actives reach the skin and how stable they stay in the bottle. Our R&D team chooses the delivery system before the formula, then builds water serums, gel serums, oil serums and emulsions around your actives and target cost. Serums are available across our graded anti-acne, anti-pigmentation and anti-ageing ranges.",
  make=["Niacinamide serums","Vitamin C serums","Retinol and bakuchiol serums","Peptide and PDRN serums","Hydrating hyaluronic serums","Bi-phasic and oil serums"],
  actives=["Liposomal delivery","Microsponge retinol and bakuchiol","Encapsulated vitamin C","Peptides","PDRN","Azelaic Z-Pods"],
  faqs=[("Which serum formats can you make?","Water serums, gel serums, oil serums, emulsions and bi-phasic serums: around 15 to 20 texture types across our ranges."),
        ("How do you keep vitamin C or retinol stable?","We use stabilised and encapsulated forms and run stability tests during development."),
        ("Can I launch good, better and best serums?","Yes. Our Grade 1 to 4 system lets you build tiered serums from one range."),
        ("Is there a detailed guide?","Yes, read our guide to face serum manufacturing in India on the blog.")],
  related=["anti-pigmentation-serum-manufacturer","anti-ageing-cream-manufacturer","hair-serum-manufacturer"], blog="face-serum-manufacturer-india"),

 dict(slug="face-wash-manufacturer", name="Face wash manufacturing", hero="body_foam.webp", pack="face-wash",
  title="Face Wash Manufacturer India | Gel, Foam, Cream | Ecosmetix",
  desc="Face wash manufacturer in India: gel, foaming, cream and exfoliating cleansers for oily, dry, sensitive and acne-prone skin. Private label and custom R&D.",
  h1="Face wash and cleanser manufacturer for skin care brands",
  lead="Mild, non-stripping cleansers with stable foam, in every format your range needs.",
  intro="The face wash is often the first product a brand launches and the one customers reorder most. Ecosmetix develops gel, foaming, cream and exfoliating cleansers on mild surfactant systems, with concern-led actives for oily, acne-prone, dull or dry skin. Choose a ready formula or brief us on your actives, foam, fragrance and target cost.",
  make=["Gel face wash","Foaming face wash and foaming pump cleansers","Cream and milk cleansers","AHA/BHA exfoliating cleansers","Face scrubs","Clay cleansers"],
  actives=["Salicylic acid","Glycolic and lactic acid","Niacinamide","Ceramides","Vitamin C","Red and green clay"],
  faqs=[("Can you make sulphate-free face washes?","Yes. We work with mild amino-acid and glucoside surfactant systems."),
        ("Which formats are available?","Gel, foam, foaming pump, cream, scrub and clay cleansers."),
        ("Can a face wash be part of an anti-acne line?","Yes. Our graded anti-acne range includes gel and foam cleansers matched to the treatment products."),
        ("What packs do you fill?","Tubes, pump bottles and foaming pumps; we help you choose packs during development.")],
  related=["anti-acne-products-manufacturer","face-cream-moisturiser-manufacturer","teen-skin-care-manufacturer"]),

 dict(slug="face-cream-moisturiser-manufacturer", name="Face cream and moisturiser manufacturing", hero="model_cream.webp", pack="face-cream",
  title="Face Cream & Moisturiser Manufacturer India | Ecosmetix",
  desc="Face cream and moisturiser manufacturer in India: day and night creams, gel creams, barrier repair and oil-free moisturisers. Private label and custom R&D.",
  h1="Face cream and moisturiser manufacturer",
  lead="From light gel creams to rich night creams, in textures your customers enjoy using every day.",
  intro="Moisturisers live or die on texture. Our R&D team works across 15 to 20 texture types, from water gels to rich creams, and pairs them with actives for hydration, barrier repair, oil control or brightening. We manufacture day creams, night creams, gel creams and oil-free moisturisers for brands across India.",
  make=["Day cream and night cream","Gel cream and water gel","Barrier repair moisturiser","Oil-free and sebum-control moisturiser","Brightening cream","Anti-acne moisturiser"],
  actives=["Ceramides","Niacinamide","Hyaluronic acid","Peptides","Squalane","Panthenol"],
  faqs=[("Which textures can you make?","Around 15 to 20 texture types, including water gels, gel creams, lotions and rich creams."),
        ("Can I have the same cream in two textures?","Yes. Many brands launch a gel version for oily skin and a cream version for dry skin."),
        ("Do you make SPF moisturisers?","Yes, built on our sunscreen bases; SPF on pack must match the test certificate."),
        ("Can I add my own hero ingredient?","Yes. Custom formulation is built around your actives, claims, texture and target cost.")],
  related=["anti-ageing-cream-manufacturer","face-wash-manufacturer","skin-care-manufacturer"]),

 dict(slug="anti-acne-products-manufacturer", name="Anti-acne range manufacturing", hero="skin_profile.webp", pack="anti-acne-cream",
  title="Anti-Acne Products Manufacturer India | Graded Range | Ecosmetix",
  desc="Anti-acne products manufacturer in India: graded moisturisers, gels, cleansers, serums and pimple patches with salicylic acid, niacinamide and azelaic Z-Pods.",
  h1="Anti-acne products manufacturer with a graded range",
  lead="Grade 1 to Grade 4 formulas, from gentle daily care to advanced correction, in one matched range.",
  intro="Acne care needs both efficacy and gentleness. Our anti-acne range runs from Grade 1 (mild concern, gentlest actives) to Grade 4 (advanced, next-generation delivery), so your brand can offer good, better and best options from one range. Formats include moisturisers, repair creams, gel and foam cleansers, bi-phasic serums and pimple patches.",
  make=["Anti-acne moisturiser and gel cream","Repair cream","Gel and foam cleansers","Bi-phasic and clarifying serums","Spot gels","Hydrocolloid pimple patches"],
  actives=["Salicylic acid","Niacinamide","Azelaic Z-Pods","Aquaxyl&trade;","Zinc PCA","Tea tree"],
  faqs=[("What does Grade 1 to 4 mean?","Grade 1 is for mild concern and daily care; Grade 2 uses upgraded or encapsulated actives; Grade 3 targets persistent concern; Grade 4 is advanced, next-generation delivery."),
        ("Can I claim 'treats acne'?","Cosmetic products should use appearance claims, such as 'helps reduce the look of blemishes'. We help you word claims your evidence supports."),
        ("Do you make pimple patches?","Yes, day and night hydrocolloid patches. See our pimple patch page."),
        ("Is there a guide to grading?","Yes, read our blog post on the acne skincare grading system for brands.")],
  related=["pimple-patch-manufacturer","teen-skin-care-manufacturer","face-wash-manufacturer"], blog="acne-skincare-grading-system-brands"),

 dict(slug="anti-pigmentation-serum-manufacturer", name="Anti-pigmentation manufacturing", hero="model_face.webp", pack="anti-pigmentation-serum",
  title="Anti-Pigmentation Serum Manufacturer India | Ecosmetix",
  desc="Anti-pigmentation serum and cream manufacturer in India: vitamin C, niacinamide, tranexamic acid, arbutin and kojic formulas in a graded range.",
  h1="Anti-pigmentation serum and cream manufacturer",
  lead="Serums, creams and spot correctors that help reduce the look of dark spots and uneven tone.",
  intro="Pigmentation is one of the most searched skin concerns in India, and buyers compare actives closely. Our graded anti-pigmentation range covers serums and creams for oily and dry skin, built on stabilised and encapsulated actives for better stability and lower irritation. Brands can launch gentle brightening products at Grade 1 and advanced correctors at Grade 4.",
  make=["Brightening serums","Anti-pigmentation creams for oily and dry skin","Spot correctors","Vitamin C serums","Under-arm and body brightening lotions","Lip brightening care"],
  actives=["Tranexamic acid","Niacinamide","Alpha arbutin","Kojic dipalmitate","Stabilised vitamin C","Azelaic Z-Pods"],
  faqs=[("Which actives do you use for pigmentation?","Tranexamic acid, niacinamide, alpha arbutin, kojic dipalmitate, stabilised vitamin C and azelaic acid, chosen by grade and skin type."),
        ("Can you make it for oily and dry skin?","Yes. The range has separate serum and cream formats for oily and dry skin."),
        ("How do you avoid irritation?","We use encapsulated and controlled-release actives and set concentrations by grade."),
        ("What claims can I use?","Appearance claims such as 'helps reduce the look of dark spots', supported by your evidence on file.")],
  related=["face-serum-manufacturer","anti-ageing-cream-manufacturer","body-lotion-manufacturer"]),

 dict(slug="anti-ageing-cream-manufacturer", name="Anti-ageing manufacturing", hero="model_glow.webp", pack="anti-ageing-cream",
  title="Anti-Ageing Cream Manufacturer India | Retinol, Peptides | Ecosmetix",
  desc="Anti-ageing cream and serum manufacturer in India: encapsulated retinol, bakuchiol, peptides, PDRN and exosomes in a graded range. Private label and R&D.",
  h1="Anti-ageing cream and serum manufacturer",
  lead="Night creams, serums and eye care built on encapsulated retinol, peptides and next-generation actives.",
  intro="Anti-ageing buyers expect named, proven actives and elegant textures. Ecosmetix develops anti-ageing creams and serums using microsponge retinol and bakuchiol for gradual release, peptides such as Matrixyl&reg; 3000, PDRN and exosomes. The graded range lets your brand offer an entry retinol cream alongside a premium Grade 4 serum.",
  make=["Retinol and bakuchiol night creams","Peptide serums","Firming and lifting creams","PDRN and exosome serums","Anti-ageing eye creams","Day creams with SPF"],
  actives=["Microsponge retinol","Bakuchiol","Matrixyl&reg; 3000","PDRN","Exosomes","Hyaluronic acid"],
  faqs=[("Why encapsulated retinol?","Encapsulation and microsponge delivery release retinol gradually, which helps reduce irritation."),
        ("Can I use 'botox-like' claims?","We advise against absolute or medical-sounding claims. We help you word claims your test data supports."),
        ("Which formats are available?","Creams, gel creams, serums and eye creams."),
        ("Can I combine anti-ageing and brightening?","Yes. Custom formulas can combine actives within one product, subject to stability testing.")],
  related=["under-eye-cream-manufacturer","face-serum-manufacturer","face-cream-moisturiser-manufacturer"]),

 dict(slug="body-lotion-manufacturer", name="Body care manufacturing", hero="body.webp", pack="body-lotion",
  title="Body Lotion Manufacturer India | Body Care | Ecosmetix",
  desc="Body lotion and body care manufacturer in India: lotions, butters, body washes and serums for hydration, brightening and bumpy skin. Private label and R&D.",
  h1="Body lotion and body care manufacturer",
  lead="Concern-led body care: hydration, smoothing, brightening and acne-prone body skin.",
  intro="Body care has moved beyond basic moisture. Our range includes body washes and lotions for body acne, pigmentation and rough, bumpy skin, alongside rich butters and body serums. Ecosmetix develops fast-absorbing, non-sticky textures and manufactures them at scale, from light lotions in pump bottles to rich butters in jars.",
  make=["Body lotions","Body butters","Body washes","Body serums","Smoothing lotions for bumpy skin","Hand and foot creams"],
  actives=["10% lactic acid","10% niacinamide","2% kojic acid","Urea","Shea butter","Ceramides"],
  faqs=[("Do you make lotions for bumpy skin?","Yes, including smoothing lotions with lactic acid and urea."),
        ("Which packs do you fill?","Pump bottles, tubes and jars across common sizes."),
        ("Can I launch a matched wash and lotion?","Yes. Many brands launch a body wash and lotion pair for one concern."),
        ("What is the MOQ?","MOQ depends on product and pack size; share your SKU sizes and launch volume and we confirm.")],
  related=["pregnancy-care-products-manufacturer","anti-pigmentation-serum-manufacturer","baby-care-products-manufacturer"]),

 dict(slug="lip-balm-manufacturer", name="Lip care manufacturing", hero="product_lineup.webp", pack="lip-balm",
  title="Lip Balm Manufacturer India | Lip Care | Ecosmetix",
  desc="Lip balm and lip care manufacturer in India: lip balms, tinted balms, lip masks, scrubs and serums in stick, tube and pot formats. Private label and R&D.",
  h1="Lip balm and lip care manufacturer",
  lead="Nourishing balms, tints, masks and scrubs in stick, tube and pot formats.",
  intro="Lip care is an easy add-on for any skin care brand and a strong impulse buy. Ecosmetix develops lip balms, tinted balms, overnight lip masks, lip scrubs and lip serums on nourishing butter and oil bases, with flavoured, tinted and SPF options. We also offer lip brightening care within our anti-pigmentation range.",
  make=["Lip balm sticks","Tinted lip balms","Overnight lip masks","Lip scrubs","Lip serums and oils","Lip brightening care"],
  actives=["Shea and cocoa butter","Plant oils","Vitamin E","Hyaluronic acid","Peptides","Natural flavours"],
  faqs=[("Which formats are available?","Stick, tube, pot and roll-on."),
        ("Can lip balms have SPF?","Yes; the SPF on pack must match the test certificate for your batch."),
        ("Do you make tinted balms?","Yes, in several shades."),
        ("Can I add lip care to an existing range?","Yes, and we can match fragrance and packaging to your current products.")],
  related=["anti-pigmentation-serum-manufacturer","kids-care-products-manufacturer","private-label-cosmetics-manufacturer"]),

 dict(slug="under-eye-cream-manufacturer", name="Under-eye care manufacturing", hero="model_eye.webp", pack="under-eye-cream",
  title="Under-Eye Cream Manufacturer India | Ecosmetix",
  desc="Under-eye cream manufacturer in India: creams, gels and serums with caffeine, peptides, microsponge retinol and exosomes. User-trial results. Private label.",
  h1="Under-eye cream manufacturer",
  lead="Creams, gels and serums for the delicate under-eye area, with results shown from a 12-day user trial.",
  intro="The under-eye area needs light textures and gentle actives. Our under-eye range includes plant-based and advanced creams such as Reti-K, Exo-K and K-Biopep, plus an instant fine-line smoother. The site's results page shows an under-eye cream user trial over 12 days, with consent; individual results vary.",
  make=["Under-eye creams","Under-eye gels","Eye serums and roll-ons","Instant fine-line smoothers","Plant-based eye creams","Retinol and exosome eye care"],
  actives=["Microsponge retinol","Milk exosomes","Peptides","Caffeine","Niacinamide","Hyaluronic acid"],
  faqs=[("What results are shown?","Our results page shows an under-eye cream user trial over 12 days, shared with consent. Individual results vary."),
        ("Which formats are available?","Creams, gels, serums and roll-ons with metal applicators."),
        ("Is retinol safe for the eye area?","We use microsponge retinol for gradual, gentler release and set concentrations for the eye area."),
        ("Can I launch a plant-based eye cream?","Yes, our range includes a plant-based under-eye cream.")],
  related=["anti-ageing-cream-manufacturer","face-serum-manufacturer","face-cream-moisturiser-manufacturer"]),

 dict(slug="pimple-patch-manufacturer", name="Pimple patch manufacturing", hero="skin_profile.webp", pack="pimple-patch",
  title="Pimple Patch Manufacturer India | Hydrocolloid | Ecosmetix",
  desc="Pimple patch manufacturer in India: hydrocolloid day and night patches, invisible patches and active-infused patches. 21-day user trial. Private label.",
  h1="Pimple patch manufacturer: hydrocolloid day and night patches",
  lead="Invisible day patches, thicker night patches and active-infused options, with custom sheets and packaging.",
  intro="Pimple patches are one of the fastest-moving acne products online. Ecosmetix supplies hydrocolloid patches for day and night use, ultra-thin invisible patches and active-infused patches, in your choice of sizes, sheet layouts, pouches and boxes. Our results page shows a pimple patch user trial over 21 days, shared with consent; individual results vary.",
  make=["Invisible day patches","Night patches","Active-infused patches","Mixed-size sheets","Pouch and box packs","Patch plus spot-gel kits"],
  actives=["Hydrocolloid","Salicylic acid","Tea tree","Niacinamide","Centella","Hyaluronic acid"],
  faqs=[("What results are shown?","Our results page shows a pimple patch user trial over 21 days, shared with consent. Individual results vary."),
        ("Can I choose patch sizes?","Yes. We offer single and mixed-size sheets."),
        ("Do you make active-infused patches?","Yes, with actives such as salicylic acid and tea tree."),
        ("Can patches be part of an acne range?","Yes; they pair with our graded anti-acne range.")],
  related=["anti-acne-products-manufacturer","teen-skin-care-manufacturer","face-wash-manufacturer"]),

 dict(slug="shampoo-manufacturer", name="Shampoo manufacturing", hero="hair.webp", pack="hair-shampoo",
  title="Shampoo Manufacturer India | Third Party | Ecosmetix",
  desc="Third-party shampoo manufacturer in India: anti-dandruff, anti-hair fall, sulphate-free, quaternium-free and liposomal shampoos. Private label and R&D.",
  h1="Shampoo manufacturer for hair care brands",
  lead="Concern-led shampoos on mild cleansing systems, including our Liposomal Shampoo.",
  intro="Shampoo is the anchor of most hair care launches. Ecosmetix develops anti-dandruff, anti-hair fall, sulphate-free, quaternium-free, colour-protect and curl shampoos, plus our Liposomal Shampoo that carries actives to scalp and hair. Every formula is built for stable foam and a clean rinse, and can be matched with conditioners, masks and serums.",
  make=["Anti-dandruff shampoo","Anti-hair fall shampoo","Sulphate-free shampoo","Quaternium-free shampoo","Colour-protect and curl shampoo","Liposomal Shampoo"],
  actives=["Piroctone olamine","Redensyl&reg;","Baicapil&trade;","Keratin","Coconut-derived surfactants","Liposomal delivery"],
  faqs=[("Do you make sulphate-free shampoos?","Yes, on mild amino-acid and glucoside surfactant systems."),
        ("What is a liposomal shampoo?","A shampoo that uses lipid vesicles to carry actives to the scalp and hair. See our liposomal shampoo page."),
        ("Can I launch a matched hair range?","Yes: shampoo, conditioner, mask and serum developed together."),
        ("Is there a detailed guide?","Yes, read our guide to third-party shampoo manufacturing in India.")],
  related=["liposomal-shampoo-manufacturer","conditioner-hair-mask-manufacturer","hair-serum-manufacturer"], blog="third-party-shampoo-manufacturer-india"),

 dict(slug="hair-serum-manufacturer", name="Hair serum manufacturing", hero="hair_waves.webp", pack="hair-serum",
  title="Hair Serum Manufacturer India | Hair Growth Serum | Ecosmetix",
  desc="Hair serum manufacturer in India: hair growth, anti-hair fall, scalp and frizz-control serums with HyaSphere, peptides and liposomal delivery.",
  h1="Hair serum manufacturer: growth, scalp and frizz care",
  lead="Lightweight serums for scalp and lengths, including a hair growth serum with HyaSphere shown in a 45-day user trial.",
  intro="Hair serums are a fast-growing, high-value category. Ecosmetix develops hair growth serums, anti-hair fall and scalp serums, frizz-control and leave-in serums, using HyaSphere and liposomal delivery to carry actives into the scalp. Our results page shows a hair growth serum with HyaSphere over a 45-day user trial, shared with consent; individual results vary.",
  make=["Hair growth serum","Anti-hair fall serum","Scalp serum","Frizz-control serum","Leave-in hair serum","Hair oils and tonics"],
  actives=["HyaSphere","Redensyl&reg;","Baicapil&trade;","Peptides","Rosemary","Caffeine"],
  faqs=[("What results are shown?","Our results page shows a hair growth serum with HyaSphere over a 45-day user trial, with consent. Individual results vary."),
        ("Which formats do you make?","Dropper serums, sprays, roll-ons and leave-in creams."),
        ("Is there a guide to hair growth actives?","Yes, read our blog on hair growth serum actives and formulation."),
        ("Can serums match my shampoo?","Yes; we develop matched hair systems.")],
  related=["shampoo-manufacturer","liposomal-shampoo-manufacturer","hair-care-manufacturer"], blog="hair-growth-serum-actives-formulation"),

 dict(slug="liposomal-shampoo-manufacturer", name="Liposomal shampoo manufacturing", hero="hair.webp", pack="liposomal-shampoo",
  title="Liposomal Shampoo Manufacturer India | Ecosmetix",
  desc="Liposomal shampoo manufacturer in India: lipid-vesicle delivery for anti-hair fall, anti-dandruff and repair shampoos, with matching conditioners and serums.",
  h1="Liposomal shampoo manufacturer",
  lead="Liposomal technology, built in-house, to carry actives to the scalp and hair in a rinse-off format.",
  intro="Most shampoos rinse their actives away in seconds. Our Liposomal Shampoo uses lipid vesicles to carry actives to the scalp and hair, giving brands a science-led point of difference on shelf. We build it for hair fall, dandruff, repair and scalp balance, in sulphate-free and quaternium-free versions, with matching liposomal conditioners, masks and serums.",
  make=["Liposomal anti-hair fall shampoo","Liposomal anti-dandruff shampoo","Liposomal repair shampoo","Liposomal scalp-balance shampoo","Liposomal conditioner","Liposomal hair mask"],
  actives=["Liposomal delivery","Peptides","Keratin","Biotin","Rosemary","Piroctone olamine"],
  faqs=[("What does liposomal mean?","Liposomes are lipid vesicles that carry actives into skin and scalp. Read our explainer on liposomal and encapsulation delivery systems."),
        ("Can it be sulphate-free?","Yes, on mild surfactant systems."),
        ("Can I add a matching serum?","Yes; liposomal shampoo pairs with our HyaSphere hair serums."),
        ("Is this a private label or custom product?","Both. Start from our liposomal base or brief a custom version.")],
  related=["shampoo-manufacturer","hair-serum-manufacturer","conditioner-hair-mask-manufacturer"], blog="liposomal-encapsulation-delivery-systems-explained"),

 dict(slug="conditioner-hair-mask-manufacturer", name="Conditioner and hair mask manufacturing", hero="hair_waves.webp", pack="conditioner-hair-mask",
  title="Conditioner & Hair Mask Manufacturer India | Ecosmetix",
  desc="Hair conditioner and hair mask manufacturer in India: rinse-off and leave-in conditioners, deep-repair masks, bond repair and keratin care. Private label.",
  h1="Conditioner and hair mask manufacturer",
  lead="Rinse-off and leave-in conditioners, deep-repair masks, bond repair and keratin systems.",
  intro="Conditioners and masks turn a shampoo into a system and raise basket value. Ecosmetix develops rinse-off and leave-in conditioners, deep-repair masks and overnight treatments for damage, frizz, dryness, colour care and hair fall, including quaternium-free and silicone-free options. Our hair care range also covers bond repair, keratin and curl systems.",
  make=["Rinse-off conditioner","Leave-in conditioner","Deep-repair hair mask","Bond repair treatment","Keratin conditioner and mask","Curl cream"],
  actives=["Keratin","Bond-repair actives","Argan oil","Shea butter","Panthenol","Coconut-derived conditioners"],
  faqs=[("Do you make quaternium-free conditioners?","Yes, along with silicone-free options."),
        ("Can I launch a bond repair range?","Yes, as part of our hair care range."),
        ("Which packs do you fill?","Tubes, bottles and jars."),
        ("Can it match my shampoo?","Yes; we develop matched shampoo, conditioner and mask systems.")],
  related=["shampoo-manufacturer","liposomal-shampoo-manufacturer","hair-care-manufacturer"]),
]

LABELS = {r["slug"]: r["name"] for r in RANGES}
LABELS.update({"hair-care-manufacturer":"Hair care manufacturing","skin-care-manufacturer":"Skin care manufacturing",
               "private-label-cosmetics-manufacturer":"Private label cosmetics","sunscreen-manufacturer":"Sunscreen manufacturing"})

def build(r):
    url = f"{BASE}/{r['slug']}/"
    t = TEMPLATE
    head_end = t.index("</head>")
    head = t[:head_end]
    # meta
    old_title = re.search(r"<title>(.*?)</title>", head).group(1)
    old_desc = re.search(r"<meta name='description' content='(.*?)'>", head).group(1)
    head = head.replace(old_title, esc(r["title"])).replace(old_desc, esc(r["desc"]))
    head = head.replace(f"{BASE}/sunscreen-manufacturer/", url)
    # replace page-specific JSON-LD (Service, FAQ, Breadcrumb) – keep the first (org) block
    blocks = re.findall(r"<script type='application/ld\+json'>.*?</script>", head, flags=re.S)
    for b in blocks[1:]:
        head = head.replace(b, "")
    service = {"@context":"https://schema.org","@type":"Service","name":r["name"],"serviceType":r["name"],
               "provider":{"@id":f"{BASE}/#org"},"areaServed":{"@type":"Country","name":"India"},"url":url,"description":r["desc"]}
    faq = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":html.unescape(re.sub('<[^>]+>','',a))}} for q,a in r["faqs"]]}
    crumbs = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":f"{BASE}/"},
        {"@type":"ListItem","position":2,"name":"Product ranges","item":f"{BASE}/product-ranges/"},
        {"@type":"ListItem","position":3,"name":r["name"],"item":url}]}
    for obj in (service, faq, crumbs):
        head += "<script type='application/ld+json'>" + json.dumps(obj, ensure_ascii=False) + "</script>"
    body_start = t.index("<main id='main'>")
    body_end = t.index("</main>") + len("</main>")
    pre = t[head_end:body_start]
    post = t[body_end:]

    ticks = "".join(f"<li>{m}</li>" for m in r["make"])
    tags = "".join(f"<span>{a}</span>" for a in r["actives"])
    faqs = "".join(f"<details><summary>{esc(q)}</summary><p>{a}</p></details>" for q,a in r["faqs"])
    blog = ""
    if r.get("blog"):
        blog = f"<li><a href='/blog/{r['blog']}/'>Read the guide on our blog</a></li>"
    rel = "".join(f"<li><a href='/{s}/'>{LABELS.get(s,s)}</a></li>" for s in r["related"])
    stats = re.search(r"<section class='section-ice'.*?</section>", t, flags=re.S).group(0)
    steps = re.search(r"<section><div class='wrap'><div class='center'><span class='eyebrow'>Process</span>.*?</section>", t, flags=re.S).group(0)
    cta = re.search(r"<section><div class='wrap'><div class='cta hexbg'>.*?</section>", t, flags=re.S).group(0)

    main = (f"<main id='main'><section class='page-hero hexbg'><div class='bg' style=\"background-image:url('/assets/img/{r['hero']}');opacity:.35\"></div>"
        f"<div class='wrap' style='position:relative'><nav class='crumbs' aria-label='Breadcrumb'><a href='/'>Home</a> / <a href='/product-ranges/'>Product ranges</a> / {esc(r['name'])}</nav>"
        f"<span class='eyebrow'>{esc(r['name'])}</span><h1>{esc(r['h1'])}</h1><div class='rule'></div><p class='lead'>{esc(r['lead'])}</p></div></section>"
        f"<section><div class='wrap'><div class='split'><div><h2>{esc(r['name'].capitalize())} for your brand</h2><div class='rule'></div><p>{r['intro']}</p>"
        f"<ul class='ticks' style='margin-top:18px'>{ticks}</ul><div class='btns'><a class='btn btn-primary' href='/product-brief/'>Share your brief</a><a class='btn btn-ghost' href='/brochure/'>Download brochure</a></div></div>"
        f"<div class='photo'><img src='/assets/img/ranges/{r['pack']}.webp' alt='{esc(r['name'])} by Ecosmetix, Ambala' loading='lazy' width='800' height='800'></div></div></div></section>"
        f"{stats}"
        f"<section><div class='wrap'><div class='split' style='align-items:start'><div><span class='eyebrow'>Ingredients and technologies</span><h2>What we formulate with</h2><div class='rule'></div>"
        f"<p>Every formula is chosen with the delivery system first, then the actives, texture and target cost. Typical ingredients in this range include:</p><div class='tags' style='margin-top:16px'>{tags}</div></div>"
        f"<div><span class='eyebrow'>Service options</span><h2>Three ways to work with us</h2><div class='rule'></div><ul class='ticks'>"
        f"<li><b>Private label:</b> launch faster from our 100+ proven, graded formulas.</li>"
        f"<li><b>Custom formulation (R&amp;D):</b> built around your actives, claims, texture and target cost.</li>"
        f"<li><b>Third-party manufacturing:</b> we manufacture, fill and pack your formula or ours.</li></ul></div></div></div></section>"
        f"{steps}"
        f"<section class='section-cloud'><div class='wrap'><div class='split' style='align-items:start'><div><span class='eyebrow'>FAQ</span><h2>{esc(r['name'].capitalize())}: questions</h2><div class='rule'></div>"
        f"<p style='margin-top:16px'>Related ranges and guides:</p><ul class='ticks' style='margin-top:8px'>{rel}{blog}<li><a href='/product-ranges/'>All product ranges</a></li></ul></div><div>{faqs}</div></div></div></section>"
        f"{cta}</main>")
    out = t[:0] + head + pre + main + post
    os.makedirs(os.path.join(ROOT, r["slug"]), exist_ok=True)
    open(os.path.join(ROOT, r["slug"], "index.html"), "w", encoding="utf-8").write(out)

def sitemap():
    p = os.path.join(ROOT, "sitemap.xml")
    s = open(p, encoding="utf-8").read()
    add = ""
    for r in RANGES:
        loc = f"{BASE}/{r['slug']}/"
        if loc not in s:
            add += f"<url><loc>{loc}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.9</priority></url>\n"
    s = s.replace("<url><loc>https://www.ecosmetix.in/about/</loc>", add + "<url><loc>https://www.ecosmetix.in/about/</loc>", 1)
    s = re.sub(r"(<loc>https://www.ecosmetix.in/product-ranges/</loc><lastmod>)[^<]+", r"\g<1>" + TODAY, s)
    open(p, "w", encoding="utf-8").write(s)

if __name__ == "__main__":
    for r in RANGES:
        build(r)
    sitemap()
    print(len(RANGES), "range pages built")
