#!/usr/bin/env python3
"""Generate trilingual cybersecurity PowerPoint presentation."""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml
from lxml import etree
import copy

# ── Colour palette ──────────────────────────────────────────────────────────
DARK_BLUE   = RGBColor(0x0D, 0x47, 0x71)
MEDIUM_BLUE = RGBColor(0x15, 0x65, 0xC0)
LIGHT_BLUE  = RGBColor(0xE3, 0xF2, 0xFD)
ACCENT      = RGBColor(0xFF, 0x6F, 0x00)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
DARK_GRAY   = RGBColor(0x33, 0x33, 0x33)
GREEN       = RGBColor(0x2E, 0x7D, 0x32)
RED         = RGBColor(0xC6, 0x28, 0x28)

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)

SLIDE_W = prs.slide_width
SLIDE_H = prs.slide_height


# ── Helpers ─────────────────────────────────────────────────────────────────

def blank_slide():
    layout = prs.slide_layouts[6]  # blank
    return prs.slides.add_slide(layout)


def add_bg(slide, color=DARK_BLUE):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, color, alpha=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def set_text(shape, text, size=18, bold=False, color=DARK_GRAY, align=PP_ALIGN.LEFT,
             italic=False, wrap=True):
    tf = shape.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = "Calibri"
    return tf


def add_textbox(slide, left, top, width, height, text, size=18, bold=False,
                color=DARK_GRAY, align=PP_ALIGN.LEFT, italic=False):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    set_text(txBox, text, size, bold, color, align, italic)
    return txBox


def add_multiline(slide, left, top, width, height, lines, size=16, color=DARK_GRAY,
                  line_spacing=1.2):
    """lines = list of (text, bold, color_override)"""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(lines):
        if isinstance(item, tuple):
            text, bold, c = item[0], item[1] if len(item) > 1 else False, item[2] if len(item) > 2 else color
        else:
            text, bold, c = item, False, color
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(4)
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = c
        run.font.name = "Calibri"
    return txBox


def section_header(slide, fr, ar, en, subtitle_fr=""):
    add_bg(slide, DARK_BLUE)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(1.1), MEDIUM_BLUE)
    add_textbox(slide, Inches(0.5), Inches(0.15), Inches(12), Inches(0.8),
                fr, size=32, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(slide, Inches(0.5), Inches(1.3), Inches(12), Inches(0.7),
                ar, size=26, bold=True, color=LIGHT_BLUE, align=PP_ALIGN.CENTER)
    add_textbox(slide, Inches(0.5), Inches(2.0), Inches(12), Inches(0.6),
                en, size=22, bold=True, color=RGBColor(0xBB, 0xDE, 0xFB), align=PP_ALIGN.CENTER)
    if subtitle_fr:
        add_textbox(slide, Inches(0.5), Inches(2.8), Inches(12), Inches(0.5),
                    subtitle_fr, size=16, color=WHITE, align=PP_ALIGN.CENTER, italic=True)


def content_slide(title_fr, title_ar, title_en, bullets):
    """bullets = list of dicts with keys fr, ar, en"""
    slide = blank_slide()
    add_bg(slide, WHITE)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(1.05), DARK_BLUE)
    add_textbox(slide, Inches(0.4), Inches(0.08), Inches(12.5), Inches(0.45),
                title_fr, size=24, bold=True, color=WHITE)
    add_textbox(slide, Inches(0.4), Inches(0.52), Inches(12.5), Inches(0.45),
                f"{title_ar}  |  {title_en}", size=14, color=LIGHT_BLUE)

    y = Inches(1.2)
    for b in bullets:
        # icon bullet
        add_rect(slide, Inches(0.4), y + Inches(0.05), Inches(0.12), Inches(0.12), ACCENT)
        add_textbox(slide, Inches(0.65), y, Inches(12), Inches(0.55),
                    b["fr"], size=15, bold=True, color=DARK_BLUE)
        add_textbox(slide, Inches(0.65), y + Inches(0.45), Inches(12), Inches(0.45),
                    b["ar"], size=13, color=DARK_GRAY)
        add_textbox(slide, Inches(0.65), y + Inches(0.85), Inches(12), Inches(0.4),
                    b["en"], size=12, color=RGBColor(0x66, 0x66, 0x66), italic=True)
        y += Inches(1.35)
    return slide


def add_appear_animation(slide, shape, delay_ms=0):
    """Add appear-on-click animation to a shape via OOXML."""
    slide_part = slide.part
    slide_el = slide_part._element

    # Ensure timing tree exists
    timing = slide_el.find(qn("p:timing"))
    if timing is None:
        timing = parse_xml(
            '<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'
        )
        slide_el.append(timing)

    tn_lst = timing.find(qn("p:tnLst"))
    if tn_lst is None:
        tn_lst = parse_xml(
            '<p:tnLst xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
            '<p:childTnLst/></p:cTn></p:par></p:tnLst>'
        )
        timing.append(tn_lst)

    cTn_root = tn_lst.find(".//" + qn("p:cTn"))
    child_lst = cTn_root.find(qn("p:childTnLst"))

    spid = shape.shape_id
    anim_id = len(child_lst) + 2

    seq_xml = f"""
    <p:seq xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
           concurrent="1" nextAc="seek">
      <p:cBhvr>
        <p:cTn id="{anim_id}" dur="indefinite" nodeType="mainSeq"/>
        <p:tgtEl>
          <p:sldTgt/>
        </p:tgtEl>
      </p:cBhvr>
      <p:childTnLst>
        <p:par>
          <p:cTn id="{anim_id + 1}" fill="hold">
            <p:stCondLst>
              <p:cond delay="indefinite"/>
            </p:stCondLst>
            <p:childTnLst>
              <p:par>
                <p:cTn id="{anim_id + 2}" presetID="1" presetClass="entr" presetSubtype="0"
                       fill="hold" nodeType="clickEffect">
                  <p:stCondLst>
                    <p:cond delay="0"/>
                  </p:stCondLst>
                  <p:childTnLst>
                    <p:set>
                      <p:cBhvr>
                        <p:cTn id="{anim_id + 3}" dur="1" fill="hold">
                          <p:stCondLst>
                            <p:cond delay="0"/>
                          </p:stCondLst>
                        </p:cTn>
                        <p:tgtEl>
                          <p:spTgt spid="{spid}"/>
                        </p:tgtEl>
                        <p:attributeName>style.visibility</p:attributeName>
                      </p:cBhvr>
                      <p:to>
                        <p:strVal val="visible"/>
                      </p:to>
                    </p:set>
                  </p:childTnLst>
                </p:cTn>
              </p:par>
            </p:childTnLst>
          </p:cTn>
        </p:par>
      </p:childTnLst>
    </p:seq>
    """
    child_lst.append(parse_xml(seq_xml))


def quiz_slide(num, q_fr, q_ar, q_en, a_fr, a_ar, a_en):
    slide = blank_slide()
    add_bg(slide, WHITE)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(0.9), DARK_BLUE)
    add_textbox(slide, Inches(0.5), Inches(0.15), Inches(12), Inches(0.6),
                f"Quiz {num}  |  اختبار {num}  |  Quiz {num}",
                size=22, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    add_rect(slide, Inches(0.5), Inches(1.1), Inches(12.3), Inches(2.8), LIGHT_BLUE)
    add_textbox(slide, Inches(0.7), Inches(1.2), Inches(12), Inches(0.5),
                "❓ Question", size=14, bold=True, color=ACCENT)
    add_textbox(slide, Inches(0.7), Inches(1.65), Inches(12), Inches(0.55),
                q_fr, size=18, bold=True, color=DARK_BLUE)
    add_textbox(slide, Inches(0.7), Inches(2.2), Inches(12), Inches(0.5),
                q_ar, size=16, color=DARK_GRAY)
    add_textbox(slide, Inches(0.7), Inches(2.7), Inches(12), Inches(0.5),
                q_en, size=15, color=RGBColor(0x66, 0x66, 0x66), italic=True)

    add_textbox(slide, Inches(0.5), Inches(4.1), Inches(12), Inches(0.4),
                "👉 Cliquez pour révéler la réponse  |  انقر لإظهار الإجابة  |  Click to reveal answer",
                size=12, color=ACCENT, align=PP_ALIGN.CENTER, italic=True)

    ans_box = add_rect(slide, Inches(0.5), Inches(4.6), Inches(12.3), Inches(2.5), RGBColor(0xE8, 0xF5, 0xE9))
    ans_box.line.color.rgb = GREEN
    ans_tf_box = add_textbox(slide, Inches(0.7), Inches(4.7), Inches(12), Inches(0.4),
                             "✅ Réponse  |  الإجابة  |  Answer", size=14, bold=True, color=GREEN)
    add_textbox(slide, Inches(0.7), Inches(5.15), Inches(12), Inches(0.55),
                a_fr, size=17, bold=True, color=DARK_BLUE)
    add_textbox(slide, Inches(0.7), Inches(5.65), Inches(12), Inches(0.5),
                a_ar, size=15, color=DARK_GRAY)
    add_textbox(slide, Inches(0.7), Inches(6.1), Inches(12), Inches(0.45),
                a_en, size=14, color=RGBColor(0x66, 0x66, 0x66), italic=True)

    # Hide answer initially via animation
    try:
        add_appear_animation(slide, ans_box)
        add_appear_animation(slide, ans_tf_box)
    except Exception:
        pass  # animation is bonus; content still works

    return slide


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
add_bg(s, DARK_BLUE)
add_rect(s, Inches(0), Inches(2.5), SLIDE_W, Inches(0.08), ACCENT)
add_textbox(s, Inches(0.5), Inches(0.8), Inches(12.3), Inches(1.0),
            "CYBERSÉCURITÉ", size=48, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_textbox(s, Inches(0.5), Inches(1.7), Inches(12.3), Inches(0.7),
            "الأمن السيبراني", size=40, bold=True, color=LIGHT_BLUE, align=PP_ALIGN.CENTER)
add_textbox(s, Inches(0.5), Inches(2.7), Inches(12.3), Inches(0.6),
            "CYBERSECURITY", size=36, bold=True, color=RGBColor(0xBB, 0xDE, 0xFB), align=PP_ALIGN.CENTER)
add_textbox(s, Inches(0.5), Inches(3.5), Inches(12.3), Inches(0.5),
            "Histoire • Avancées • Risques humains • Conseils pratiques",
            size=18, color=WHITE, align=PP_ALIGN.CENTER)
add_textbox(s, Inches(0.5), Inches(4.0), Inches(12.3), Inches(0.5),
            "التاريخ • التطورات • المخاطر البشرية • نصائح عملية",
            size=16, color=LIGHT_BLUE, align=PP_ALIGN.CENTER)
add_textbox(s, Inches(0.5), Inches(4.5), Inches(12.3), Inches(0.5),
            "History • Advances • Human Risks • Practical Tips",
            size=16, color=RGBColor(0xBB, 0xDE, 0xFB), align=PP_ALIGN.CENTER, italic=True)
add_textbox(s, Inches(0.5), Inches(5.8), Inches(12.3), Inches(0.5),
            "Présentation accessible — profil non technique",
            size=14, color=WHITE, align=PP_ALIGN.CENTER, italic=True)
add_textbox(s, Inches(0.5), Inches(6.5), Inches(12.3), Inches(0.5),
            "Réalisé par : Yacoub HOURMATALLA  &  Ismail SIDIYA",
            size=16, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — WHAT IS CYBERSECURITY?
# ══════════════════════════════════════════════════════════════════════════════
content_slide(
    "Qu'est-ce que la cybersécurité ?",
    "ما هو الأمن السيبراني؟",
    "What is Cybersecurity?",
    [
        {
            "fr": "🛡️ Protéger nos informations numériques — comme un cadenas sur vos données",
            "ar": "🛡️ حماية معلوماتنا الرقمية — كقفل على بياناتكم",
            "en": "🛡️ Protecting our digital information — like a lock on your data",
        },
        {
            "fr": "🌐 Tout ce qui est connecté à Internet peut être attaqué : téléphones, ordinateurs, maisons intelligentes",
            "ar": "🌐 كل ما يتصل بالإنترنت قد يتعرض للهجوم: الهواتف، الحاسوب، المنازل الذكية",
            "en": "🌐 Anything connected to the Internet can be attacked: phones, computers, smart homes",
        },
        {
            "fr": "👤 95 % des failles viennent de l'erreur humaine — pas seulement des pirates informatiques",
            "ar": "👤 ٩٥٪ من الثغرات ناتجة عن خطأ بشري — وليس فقط المخترقين",
            "en": "👤 95% of breaches come from human error — not just hackers",
        },
    ],
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — SECTION: HISTORY
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
section_header(s,
    "📜 Histoire de la Cybersécurité",
    "📜 تاريخ الأمن السيبراني",
    "📜 History of Cybersecurity",
    "Des années 1970 à aujourd'hui — les grandes étapes")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — HISTORY TIMELINE 1
# ══════════════════════════════════════════════════════════════════════════════
content_slide(
    "Les grandes dates (1970–2000)",
    "التواريخ المهمة (١٩٧٠–٢٠٠٠)",
    "Key Dates (1970–2000)",
    [
        {
            "fr": "1971 — Creeper : premier « virus » expérimental (message : « Je suis Creeper, attrape-moi ! »)",
            "ar": "١٩٧١ — كريبر: أول «فيروس» تجريبي (رسالة: «أنا كريبر، أمسكني!»)",
            "en": "1971 — Creeper: first experimental 'virus' (message: 'I'm Creeper, catch me!')",
        },
        {
            "fr": "1988 — Morris Worm : 6 000 ordinateurs infectés → naissance des CERT (équipes d'alerte)",
            "ar": "١٩٨٨ — دودة موريس: ٦٠٠٠ حاسوب مصاب → ولادة فرق CERT للتنبيه",
            "en": "1988 — Morris Worm: 6,000 computers infected → birth of CERT alert teams",
        },
        {
            "fr": "1990s — Internet grand public : e-mails, mots de passe, premiers antivirus grand public",
            "ar": "٩٠٠ات — الإنترنت للجميع: البريد الإلكتروني، كلمات المرور، أول برامج مكافحة الفيروسات",
            "en": "1990s — Public Internet: email, passwords, first consumer antivirus software",
        },
    ],
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — HISTORY TIMELINE 2
# ══════════════════════════════════════════════════════════════════════════════
content_slide(
    "Les grandes dates (2000–2025)",
    "التواريخ المهمة (٢٠٠٠–٢٠٢٥)",
    "Key Dates (2000–2025)",
    [
        {
            "fr": "2000 — ILOVEYOU : 50 millions d'infections via un simple e-mail d'amour",
            "ar": "٢٠٠٠ — ILOVEYOU: ٥٠ مليون إصابة عبر بريد إلكتروني بسيط",
            "en": "2000 — ILOVEYOU: 50 million infections via a simple love email",
        },
        {
            "fr": "2010s — Ransomware (rançongiciel) : vos fichiers sont bloqués, on exige une rançon",
            "ar": "٢٠١٠ات — برامج الفدية: ملفاتكم محجوزة ويطلبون فدية",
            "en": "2010s — Ransomware: your files are locked, attackers demand payment",
        },
        {
            "fr": "2020s — IA, télétravail, objets connectés : de nouvelles surfaces d'attaque",
            "ar": "٢٠٢٠ات — الذكاء الاصطناعي، العمل عن بُعد، إنترنت الأشياء: أسطح هجوم جديدة",
            "en": "2020s — AI, remote work, IoT: new attack surfaces emerge",
        },
    ],
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — SECTION: ADVANCES
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
section_header(s,
    "🚀 Avancées Importantes",
    "🚀 التطورات المهمة",
    "🚀 Important Advances")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — ADVANCES
# ══════════════════════════════════════════════════════════════════════════════
content_slide(
    "Les avancées qui nous protègent",
    "التطورات التي تحمينا",
    "Advances That Protect Us",
    [
        {
            "fr": "🔐 Chiffrement (Encryption) : vos messages transformés en code illisible sans la clé — comme une langue secrète",
            "ar": "🔐 التشفير: رسائلكم تتحول إلى رمز غير مقروء بدون المفتاح — كلغة سرية",
            "en": "🔐 Encryption: your messages become unreadable code without the key — like a secret language",
        },
        {
            "fr": "🔑 Authentification à deux facteurs (2FA) : mot de passe + code SMS = double verrou",
            "ar": "🔑 المصادقة الثنائية: كلمة المرور + رمز SMS = قفل مزدوج",
            "en": "🔑 Two-Factor Authentication (2FA): password + SMS code = double lock",
        },
        {
            "fr": "🤖 IA défensive : détecte les comportements suspects avant qu'il ne soit trop tard",
            "ar": "🤖 الذكاء الاصطناعي الدفاعي: يكتشف السلوك المشبوه قبل فوات الأوان",
            "en": "🤖 Defensive AI: detects suspicious behavior before it's too late",
        },
    ],
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — SIMPLIFIED CONCEPTS
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
section_header(s,
    "💡 Concepts Techniques Simplifiés",
    "💡 مفاهيم تقنية مبسطة",
    "💡 Simplified Technical Concepts")

content_slide(
    "Le vocabulaire expliqué simplement",
    "المفردات التقنية ببساطة",
    "Technical Vocabulary Made Simple",
    [
        {
            "fr": "🎣 Phishing (hameçonnage) : un faux e-mail qui vous piège — comme un pêcheur avec un appât",
            "ar": "🎣 التصيّد: بريد مزيف يوقعكم في الفخ — كصياد يستخدم طُعمًا",
            "en": "🎣 Phishing: a fake email that traps you — like a fisherman using bait",
        },
        {
            "fr": "🦠 Malware (logiciel malveillant) : programme nuisible — virus, trojan, spyware",
            "ar": "🦠 البرمجيات الخبيثة: برنامج ضار — فيروس، حصان طروادة، برامج تجسس",
            "en": "🦠 Malware: harmful software — viruses, trojans, spyware",
        },
        {
            "fr": "🔓 Zero-day : faille inconnue même par le fabricant — aucune protection disponible encore",
            "ar": "🔓 ثغرة يوم الصفر: ثغرة غير معروفة حتى للمصنع — لا حماية متاحة بعد",
            "en": "🔓 Zero-day: unknown flaw even to the manufacturer — no patch available yet",
        },
    ],
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — HUMAN RISKS SECTION
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
section_header(s,
    "👤 Les Risques Humains — Le Facteur N°1",
    "👤 المخاطر البشرية — العامل الأول",
    "👤 Human Risks — The #1 Factor",
    "Pourquoi nous restons la cible préférée des attaquants")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — HUMAN RISKS
# ══════════════════════════════════════════════════════════════════════════════
content_slide(
    "Quand l'humain devient la faille",
    "عندما يصبح الإنسان الثغرة",
    "When Humans Become the Weak Link",
    [
        {
            "fr": "😰 Ingénierie sociale : manipulation psychologique — peur, urgence, confiance abusée",
            "ar": "😰 الهندسة الاجتماعية: التلاعب النفسي — الخوف، الاستعجال، إساءة الثقة",
            "en": "😰 Social engineering: psychological manipulation — fear, urgency, abused trust",
        },
        {
            "fr": "📱 Partage de mots de passe, clics impulsifs, Wi-Fi public non sécurisé",
            "ar": "📱 مشاركة كلمات المرور، النقرات الاندفاعية، شبكات Wi-Fi عامة غير آمنة",
            "en": "📱 Password sharing, impulsive clicks, unsecured public Wi-Fi",
        },
        {
            "fr": "🏢 Erreur interne : 60 %+ des incidents impliquent un employé (volontairement ou par ignorance)",
            "ar": "🏢 خطأ داخلي: أكثر من ٦٠٪ من الحوادث يشارك فيها موظف (عمدًا أو بجهل)",
            "en": "🏢 Insider incidents: 60%+ involve an employee (intentionally or unknowingly)",
        },
    ],
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — NEW RISKS SECTION
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
section_header(s,
    "⚠️ Nouveaux Risques (2024–2026)",
    "⚠️ المخاطر الجديدة (٢٠٢٤–٢٠٢٦)",
    "⚠️ Emerging Risks (2024–2026)")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — NEW RISKS
# ══════════════════════════════════════════════════════════════════════════════
content_slide(
    "Les menaces de demain, déjà là aujourd'hui",
    "تهديدات الغد، موجودة اليوم",
    "Tomorrow's Threats, Already Here Today",
    [
        {
            "fr": "🤖 Deepfakes & IA malveillante : fausses voix/vidéos de votre patron ou famille pour vous arnaquer",
            "ar": "🤖 التزييف العميق والذكاء الاصطناعي الخبيث: أصوات/فيديوهات مزيفة لمديركم أو عائلتكم",
            "en": "🤖 Deepfakes & malicious AI: fake voice/video of your boss or family to scam you",
        },
        {
            "fr": "☁️ Attaques sur le cloud & chaîne d'approvisionnement : pirater un fournisseur = accès à des milliers de clients",
            "ar": "☁️ هجمات السحابة وسلسلة التوريد: اختراق مورد = وصول لآلاف العملاء",
            "en": "☁️ Cloud & supply chain attacks: hack one vendor = access to thousands of clients",
        },
        {
            "fr": "🏠 IoT & voitures connectées : frigo, caméra, voiture = nouvelles portes d'entrée pour les pirates",
            "ar": "🏠 إنترنت الأشياء والسيارات المتصلة: الثلاجة، الكاميرا، السيارة = مداخل جديدة",
            "en": "🏠 IoT & connected cars: fridge, camera, car = new entry points for attackers",
        },
    ],
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — ADVICE SECTION
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
section_header(s,
    "✅ Grands Conseils à Retenir",
    "✅ نصائح مهمة يجب تذكرها",
    "✅ Essential Tips to Remember")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — TOP TIPS
# ══════════════════════════════════════════════════════════════════════════════
content_slide(
    "10 règles d'or de la cybersécurité",
    "١٠ قواعد ذهبية للأمن السيبراني",
    "10 Golden Rules of Cybersecurity",
    [
        {
            "fr": "1️⃣ Mots de passe uniques & longs (12+ caractères) — utilisez un gestionnaire de mots de passe",
            "ar": "1️⃣ كلمات مرور فريدة وطويلة (١٢+ حرفًا) — استخدموا مدير كلمات مرور",
            "en": "1️⃣ Unique, long passwords (12+ chars) — use a password manager",
        },
        {
            "fr": "2️⃣ Activez la 2FA partout  |  3️⃣ Méfiez-vous des liens et pièces jointes inattendues",
            "ar": "2️⃣ فعّلوا المصادقة الثنائية  |  3️⃣ احذروا الروابط والمرفقات غير المتوقعة",
            "en": "2️⃣ Enable 2FA everywhere  |  3️⃣ Beware unexpected links & attachments",
        },
        {
            "fr": "4️⃣ Mettez à jour vos appareils  |  5️⃣ Sauvegardez vos données (règle 3-2-1)",
            "ar": "4️⃣ حدّثوا أجهزتكم  |  5️⃣ احفظوا نسخًا احتياطية (قاعدة ٣-٢-١)",
            "en": "4️⃣ Update your devices  |  5️⃣ Back up your data (3-2-1 rule)",
        },
    ],
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 16 — MORE TIPS
# ══════════════════════════════════════════════════════════════════════════════
content_slide(
    "10 règles d'or (suite)",
    "١٠ قواعد ذهبية (تابع)",
    "10 Golden Rules (continued)",
    [
        {
            "fr": "6️⃣ Ne partagez jamais vos mots de passe  |  7️⃣ Vérifiez l'identité avant de transférer de l'argent",
            "ar": "6️⃣ لا تشاركوا كلمات المرور  |  7️⃣ تحققوا من الهوية قبل تحويل المال",
            "en": "6️⃣ Never share passwords  |  7️⃣ Verify identity before sending money",
        },
        {
            "fr": "8️⃣ Utilisez un VPN sur Wi-Fi public  |  9️⃣ Signalez les e-mails suspects à votre IT",
            "ar": "8️⃣ استخدموا VPN على Wi-Fi العام  |  9️⃣ أبلغوا عن رسائل مشبوهة",
            "en": "8️⃣ Use VPN on public Wi-Fi  |  9️⃣ Report suspicious emails to IT",
        },
        {
            "fr": "🔟 Restez informé & formez-vous — la cybersécurité est l'affaire de TOUS",
            "ar": "🔟 ابقوا مطلعين وتدربوا — الأمن السيبراني مسؤولية الجميع",
            "en": "🔟 Stay informed & trained — cybersecurity is EVERYONE's responsibility",
        },
    ],
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 17 — QUIZ SECTION
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
section_header(s,
    "🎯 Quiz Interactif",
    "🎯 اختبار تفاعلي",
    "🎯 Interactive Quiz",
    "Cliquez pour révéler chaque réponse  |  انقر لإظهار الإجابة  |  Click to reveal each answer")

# ══════════════════════════════════════════════════════════════════════════════
# QUIZ SLIDES
# ══════════════════════════════════════════════════════════════════════════════
quiz_slide(1,
    "Quel pourcentage des failles de sécurité est causé par l'erreur humaine ?",
    "ما نسبة الثغرات الأمنية الناتجة عن الخطأ البشري؟",
    "What percentage of security breaches are caused by human error?",
    "Environ 95 % — l'humain reste le maillon faible numéro 1.",
    "حوالي ٩٥٪ — الإنسان يبقى حلقة الوصل الأضعف.",
    "About 95% — humans remain the #1 weak link.",
)

quiz_slide(2,
    "Qu'est-ce que le « phishing » ?",
    "ما هو «التصيّد الإلكتروني»؟",
    "What is 'phishing'?",
    "Un e-mail ou message frauduleux conçu pour voler vos identifiants — comme un appât de pêche.",
    "بريد أو رسالة احتيالية لسرقة بياناتكم — كطُعم صيد.",
    "A fraudulent email or message designed to steal your credentials — like fishing bait.",
)

quiz_slide(3,
    "Qu'est-ce qu'un « ransomware » (rançongiciel) ?",
    "ما هو «برنامج الفدية»؟",
    "What is 'ransomware'?",
    "Un logiciel qui bloque vos fichiers et exige une rançon pour les débloquer.",
    "برنامج يحجب ملفاتكم ويطلب فدية لإطلاقها.",
    "Software that locks your files and demands payment to unlock them.",
)

quiz_slide(4,
    "Que signifie « 2FA » (authentification à deux facteurs) ?",
    "ماذا تعني «المصادقة الثنائية»؟",
    "What does '2FA' (Two-Factor Authentication) mean?",
    "Deux preuves d'identité : mot de passe + code SMS ou empreinte — double sécurité.",
    "دليلان على الهوية: كلمة المرور + رمز أو بصمة — أمان مزدوج.",
    "Two proofs of identity: password + SMS code or fingerprint — double security.",
)

quiz_slide(5,
    "Quel est le risque émergent lié à l'intelligence artificielle ?",
    "ما الخطر الناشئ المرتبط بالذكاء الاصطناعي؟",
    "What is an emerging risk related to artificial intelligence?",
    "Les deepfakes : fausses vidéos/voix ultra-réalistes pour arnaquer ou usurper une identité.",
    "التزييف العميق: فيديوهات/أصوات مزيفة واقعية للاحتيال أو انتحال الهوية.",
    "Deepfakes: ultra-realistic fake videos/voices to scam or impersonate someone.",
)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE — CONCLUSION
# ══════════════════════════════════════════════════════════════════════════════
s = blank_slide()
add_bg(s, DARK_BLUE)
add_rect(s, Inches(0), Inches(0), SLIDE_W, Inches(0.08), ACCENT)
add_textbox(s, Inches(0.5), Inches(0.5), Inches(12.3), Inches(0.7),
            "🎯 Conclusion", size=36, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_textbox(s, Inches(0.5), Inches(1.15), Inches(12.3), Inches(0.55),
            "🎯 الخلاصة  |  🎯 Conclusion", size=24, color=LIGHT_BLUE, align=PP_ALIGN.CENTER)

bullets_conclusion = [
    ("La cybersécurité n'est pas réservée aux experts — c'est l'affaire de chacun.",
     "الأمن السيبراني ليس للخبراء فقط — إنه مسؤولية كل فرد.",
     "Cybersecurity is not just for experts — it's everyone's responsibility."),
    ("L'histoire montre une course permanente entre attaquants et défenseurs.",
     "التاريخ يُظهر سباقًا دائمًا بين المهاجمين والمدافعين.",
     "History shows a permanent race between attackers and defenders."),
    ("Le facteur humain reste le risque n°1 — la formation change tout.",
     "العامل البشري يبقى الخطر الأول — التدريب يغيّر كل شيء.",
     "The human factor remains risk #1 — training makes all the difference."),
    ("Adoptez les bonnes habitudes dès aujourd'hui : mots de passe, 2FA, prudence.",
     "تبنّوا العادات الجيدة اليوم: كلمات المرور، المصادقة الثنائية، الحذر.",
     "Adopt good habits today: passwords, 2FA, caution."),
]

y = Inches(1.9)
for fr, ar, en in bullets_conclusion:
    add_textbox(s, Inches(0.8), y, Inches(11.8), Inches(0.45), f"• {fr}", size=16, color=WHITE)
    add_textbox(s, Inches(1.0), y + Inches(0.42), Inches(11.5), Inches(0.38), ar, size=14, color=LIGHT_BLUE)
    add_textbox(s, Inches(1.0), y + Inches(0.78), Inches(11.5), Inches(0.35), en, size=13,
                color=RGBColor(0xBB, 0xDE, 0xFB), italic=True)
    y += Inches(1.25)

add_rect(s, Inches(2), Inches(6.0), Inches(9.3), Inches(0.06), ACCENT)
add_textbox(s, Inches(0.5), Inches(6.2), Inches(12.3), Inches(0.5),
            "Merci pour votre attention !  |  شكرًا لانتباهكم  |  Thank you for your attention!",
            size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_textbox(s, Inches(0.5), Inches(6.7), Inches(12.3), Inches(0.4),
            "Réalisé par : Yacoub HOURMATALLA  &  Ismail SIDIYA",
            size=15, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════════════════════
output_path = "/workspace/Cybersecurite_Presentation_Trilangue.pptx"
prs.save(output_path)
print(f"✅ Présentation créée : {output_path}")
print(f"   Nombre de slides : {len(prs.slides)}")
