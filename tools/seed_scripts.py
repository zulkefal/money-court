"""One-time seeder: drop 60 hand-written scripts into scripts/.

Run:  ./venv/bin/python tools/seed_scripts.py

Each entry is compact (names, topic_slug, topic_title, 7 scenes of
(narration, scene_description)). The builder wraps them in the standard
style anchors and host canonical look so each file matches the schema in
scripts/README.md.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "scripts"

STYLE = (
    "kids graphic novel page panel, illustrated comic book art, "
    "bold flat colors clean black ink lines"
)
TAIL = "kids comic book illustration"

HOST_LOOKS = {
    "judge_vera": (
        "cartoon woman named judge vera, silver hair in a neat bun, "
        "sharp dark eyes, black judge robes with a gold gavel badge, "
        "holding wooden gavel"
    ),
    "detective_cash": (
        "cartoon man named detective cash, sharp blue eyes, gray fedora hat, "
        "beige trench coat, five o'clock shadow, holding magnifying glass "
        "and a manila file folder labeled with dollar signs"
    ),
    "coach_vault": (
        "cartoon man named coach vault, athletic build, buzzcut brown hair, "
        "red track jacket with gold dollar sign logo, silver whistle, "
        "clipboard covered in dollar sign stickers, fingerless training "
        "gloves, sweatband"
    ),
    "doctor_dollar": (
        "cartoon woman named doctor dollar, dark curly hair, round gold-rim "
        "glasses, kind smile, white doctor coat over teal scrubs, golden "
        "stethoscope shaped like a dollar sign, holding a clipboard with "
        "a credit-score chart"
    ),
}

PREFIX = {
    "judge_vera": "verdict",
    "detective_cash": "case-file",
    "coach_vault": "workout",
    "doctor_dollar": "checkup",
}

SAFE_PUNCT = re.compile(r"[^A-Za-z0-9 .,!?']")


def _clean(text: str) -> str:
    """Strip disallowed punctuation from narration; collapse spaces."""
    text = SAFE_PUNCT.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build(character: str, names: tuple[str, str], topic_slug: str,
          topic_title: str, scenes: list[tuple[str, str]]) -> dict:
    """Produce a script dict matching scripts/*.json schema."""
    name1, name2 = names
    video_id = (
        f"{PREFIX[character]}-{name1.lower()}-vs-{name2.lower()}-"
        f"{topic_slug}-001"
    )
    out_scenes = []
    for i, (narration, desc) in enumerate(scenes):
        idx = i + 1
        if idx == 1 or idx == 7:
            prompt = f"{STYLE}, {HOST_LOOKS[character]}, {desc}, {TAIL}"
        else:
            prompt = f"{STYLE}, {desc}, {TAIL}"
        out_scenes.append({
            "id": idx,
            "narration": _clean(narration),
            "image_prompt": prompt,
        })
    return {
        "video_id": video_id,
        "character": character,
        "topic": f"{topic_title} ({name1} vs {name2})",
        "scenes": out_scenes,
    }


# Each script: (character, (name1, name2), topic_slug, topic_title, scenes)
# scenes: list of 7 (narration, scene_description) tuples
SCRIPTS: list[tuple] = []


# ============================================================
# JUDGE VERA  (14 stories — dan vs zoe already exists)
# ============================================================

SCRIPTS.append((
    "judge_vera", ("Mike", "Lisa"),
    "co-signing-a-loan", "Co-signing a loan vs paying cash",
    [
        ("One signature can wreck your credit for seven years. I am Judge Vera and today two siblings asked the same favor with very different answers. Court is in session!",
         "judge vera standing behind a tall courtroom bench pointing her gavel forward, a giant comic burst banner reads SEVEN YEARS in bold letters, dramatic spotlight on the bench"),
        ("Mike and Lisa are both twenty eight years old. Each one gets a phone call from a younger sibling asking them to co-sign a twelve thousand dollar auto loan.",
         "split panel, left side man mike on the phone with worried expression, right side woman lisa on the phone with thoughtful expression, both in cozy living rooms"),
        ("Mike says yes without asking questions, signs the paperwork the next morning, and never reads the part about being equally responsible for the debt.",
         "man mike at a car dealership desk signing a thick loan contract while a salesman smiles, papers labeled CO SIGNER stacked beside him"),
        ("Lisa says no but offers a two thousand dollar cash gift instead. She tells her brother to build credit with a secured card before borrowing twelve thousand.",
         "woman lisa handing a small envelope of cash to a younger brother in a kitchen, a small chalkboard behind them reading SECURED CARD FIRST"),
        ("Eight months later Mike's brother loses his job and stops paying. The loan defaults and the bank comes after Mike for the remaining nine thousand dollars.",
         "shocked man mike opening a bank letter at a kitchen table, a giant red comic banner reading NINE THOUSAND OWED looms over his shoulder"),
        ("Mike's credit score crashes one hundred and twenty points and the debt sits on his report for seven years. Lisa's credit is untouched and her brother is still grateful.",
         "split scene, left side mike staring at a falling credit score meter on his phone, right side lisa hugging her brother in front of a small running used car"),
        ("Co-signing means the debt is your debt the moment they miss a payment. If you cannot afford to pay it yourself, do not sign it. Court dismissed!",
         "judge vera banging her gavel on the bench, holding up a checklist labeled CO SIGN RULES, comic burst banner reads COURT DISMISSED"),
    ],
))

SCRIPTS.append((
    "judge_vera", ("Sam", "Pat"),
    "reading-the-contract", "Reading a contract vs signing blind",
    [
        ("One page of fine print hid six extra fees worth six hundred dollars. I am Judge Vera and today two used car buyers learned the cost of a quick signature. Court is in session!",
         "judge vera at the bench pointing her gavel at a giant unrolled contract with six red dollar circles drawn on it, dramatic courtroom spotlight"),
        ("Sam and Pat both walk into the same dealership for the same three thousand dollar used sedan on the same Saturday afternoon.",
         "two adults sam and pat standing in a busy used car lot looking at the same blue sedan with a price tag reading THREE THOUSAND"),
        ("Sam glances at the first page, signs the rest without reading, and drives off feeling like he won the deal of the year.",
         "man sam at a salesman desk signing fast with one hand while waving keys in the other, salesman smirking behind the desk"),
        ("Pat reads every line out loud, spots a doc fee, a prep fee, a warranty bundle, and a paint protection charge, and asks for each one to be removed.",
         "woman pat sitting at the same desk with a finger on a contract line, red comic burst circles around hidden fees, salesman looking flustered"),
        ("Thirty days later the dealer mails Sam the final paperwork showing he actually paid three thousand eight hundred dollars instead of three thousand.",
         "shocked man sam staring at a final invoice in his driveway, a giant comic burst banner reading EIGHT HUNDRED EXTRA looms above him"),
        ("Pat drove off paying three thousand two hundred and saved six hundred dollars just by reading the page in front of her.",
         "split scene, left side sam holding a paper labeled THREE THOUSAND EIGHT HUNDRED, right side pat smiling with a paper labeled THREE THOUSAND TWO HUNDRED"),
        ("Ten minutes of reading saves you hundreds of dollars. Never sign a contract until you have read every line, every fee, every total. Court dismissed!",
         "judge vera banging her gavel, holding up a contract with a giant red CHECK every line stamp, comic banner reads READ FIRST"),
    ],
))

SCRIPTS.append((
    "judge_vera", ("Tom", "Rita"),
    "disputing-wrong-charges", "Disputing a wrong charge vs ignoring it",
    [
        ("Federal law gives you sixty days to dispute a wrong charge. After that the money is gone. I am Judge Vera and today two cardholders made very different choices. Court is in session!",
         "judge vera at the courtroom bench pointing her gavel at a wall calendar with sixty days circled in red, comic burst banner reads SIXTY DAYS"),
        ("Tom and Rita each open their statements and find the same mystery charge from a gym they never joined, four hundred dollars each.",
         "two adults tom and rita at separate kitchen tables holding paper statements with a red highlighted line reading FOUR HUNDRED MYSTERY GYM"),
        ("Tom assumes the charge will fall off on its own, tosses the statement on the counter, and forgets about it for three months.",
         "man tom shrugging and tossing a paper statement onto a messy kitchen counter, dust building on a stack of unopened envelopes"),
        ("Rita calls her bank that same afternoon, files a written dispute, and sends the bank a copy of her membership records to prove she never signed up.",
         "woman rita on the phone at a kitchen table with a notebook, a big written letter labeled WRITTEN DISPUTE in front of her"),
        ("Sixty days later Tom calls the bank to fight the charge but the dispute window is closed and he is now legally responsible for the four hundred dollars.",
         "shocked man tom on the phone with a bank rep, a giant red comic banner reading TOO LATE blocks the screen behind him"),
        ("Rita got her four hundred dollars credited back in ten days and the bank closed the merchant account for fraud.",
         "split scene, left side tom looking at a bill labeled FOUR HUNDRED OWED, right side rita celebrating a credit notice labeled REFUNDED"),
        ("Open every statement the day it arrives and dispute anything you do not recognize in writing. Sixty days is your only window. Court dismissed!",
         "judge vera banging her gavel, holding up a checklist labeled FILE WRITTEN DISPUTE, comic banner reads SIXTY DAY RULE"),
    ],
))

SCRIPTS.append((
    "judge_vera", ("Carl", "Beth"),
    "filing-taxes-on-time", "Filing taxes on time vs ignoring the IRS",
    [
        ("The IRS adds twenty five percent in penalties just for not filing on time. I am Judge Vera and today two freelancers walked very different roads. Court is in session!",
         "judge vera at the bench pointing her gavel at a giant comic burst banner reading TWENTY FIVE PERCENT PENALTY, courtroom spotlight"),
        ("Carl and Beth are both freelancers who owe four thousand dollars in taxes for the year and both miss the April fifteenth deadline by accident.",
         "two adults carl and beth at separate desks both staring at tax forms labeled FOUR THOUSAND OWED, calendar on the wall reads APRIL FIFTEEN"),
        ("Carl panics, hides every IRS letter in a drawer, and tells himself he will deal with it next year when he has the money.",
         "man carl shoving a stack of IRS envelopes into a drawer, a giant comic burst banner reading IGNORE looms above him"),
        ("Beth files her return three weeks late, includes a payment plan request, and sends the IRS one hundred and fifty dollars per month.",
         "woman beth at a kitchen table mailing a tax return envelope, a small notebook open to a payment plan with monthly checkmarks"),
        ("Eighteen months later Carl gets a final notice with five thousand five hundred dollars owed in tax, penalties, and interest, plus a wage garnishment warning.",
         "shocked man carl opening a final IRS notice at his front door, giant red comic banner reading FIVE THOUSAND FIVE HUNDRED looms above him"),
        ("Beth has paid off the four thousand owed plus a small amount of interest. Her credit and her paycheck are both safe.",
         "split scene, left side carl looking at a wage garnishment letter, right side beth marking a calendar PAID IN FULL with a smile"),
        ("File on time even if you cannot pay. The IRS will work with you on a plan, but only if you respond. Court dismissed!",
         "judge vera banging her gavel, holding up a tax form stamped FILED ON TIME, comic banner reads ALWAYS FILE"),
    ],
))

SCRIPTS.append((
    "judge_vera", ("Jake", "Ivy"),
    "settling-debt-in-writing", "Settling a debt in writing vs verbal deals",
    [
        ("A debt collector promised one buyer a sixty percent discount, then sold the debt to a new collector who demanded it all back. I am Judge Vera. Court is in session!",
         "judge vera at the courtroom bench holding up a contract stamped GET IT IN WRITING, comic burst banner reads SIXTY PERCENT BROKEN"),
        ("Jake and Ivy each owe six thousand dollars to the same debt collector and both negotiate a settlement of two thousand four hundred dollars over the phone.",
         "two adults jake and ivy on phones at separate kitchen tables, a comic banner above each reads SIX THOUSAND TO TWO FOUR HUNDRED"),
        ("Jake trusts the friendly voice on the phone, mails a cashier check the same week, and never asks for a written settlement letter.",
         "man jake at a mailbox dropping in a cashier check envelope, a verbal handshake icon hovering above him"),
        ("Ivy demands a written settlement letter on company letterhead first, signs it, scans a copy, and only then mails the money.",
         "woman ivy at a kitchen table holding a printed letter labeled SETTLEMENT IN WRITING with a signature line, scanner beside her"),
        ("Eight months later the original collector sells Jake's account to a new agency claiming there is no record of any deal and demanding the full six thousand.",
         "shocked man jake on the phone with a new collector, giant red comic banner reading FULL DEBT BACK looms behind him"),
        ("Ivy mails her signed settlement letter to the new collector and the case is closed in ten days. Same debt, same negotiation, very different outcomes.",
         "split scene, left side jake staring at a new collection notice for SIX THOUSAND, right side ivy filing a closed case folder labeled PAID IN FULL"),
        ("Never send a debt collector a single dollar without a signed settlement letter in your hand. Verbal promises evaporate. Court dismissed!",
         "judge vera banging her gavel, holding up a settlement letter stamped SIGNED, comic banner reads WRITTEN ONLY"),
    ],
))

SCRIPTS.append((
    "judge_vera", ("Ryan", "Nora"),
    "checking-credit-report", "Checking your credit report vs ignoring it",
    [
        ("One in five credit reports has a damaging error. I am Judge Vera and today two mortgage applicants discovered theirs at very different times. Court is in session!",
         "judge vera at the bench pointing her gavel at a giant credit report with red error circles, comic burst banner reads ONE IN FIVE"),
        ("Ryan and Nora both apply for a three hundred thousand dollar mortgage, both earn the same salary, and both have nearly identical credit histories.",
         "two adults ryan and nora at a bank loan officer desk holding identical mortgage application packets, a price tag reading THREE HUNDRED THOUSAND"),
        ("Ryan has never checked his credit report. He assumes everything is fine and submits the application without reviewing his three reports.",
         "man ryan handing a mortgage application to a loan officer with a confident shrug, a question mark hovering over his head"),
        ("Nora pulls all three free reports at annualcreditreport dot com, finds three errors including a closed account marked open, and disputes each one in writing.",
         "woman nora at a kitchen table with three credit reports spread out, a red pen circling errors, comic burst banner reads ANNUAL CREDIT REPORT"),
        ("Six weeks later Ryan is approved at seven and a half percent because old errors hurt his score. His monthly payment is two thousand one hundred dollars.",
         "shocked man ryan at a closing table with a paper labeled SEVEN POINT FIVE PERCENT looming over him, calculator showing TWO THOUSAND ONE HUNDRED"),
        ("Nora's clean report gets her approved at six point two percent. Over thirty years she pays forty thousand dollars less than Ryan for the same house.",
         "split scene, left side ryan with a giant payment number, right side nora with a paper labeled SIX POINT TWO PERCENT and a smile"),
        ("Pull your credit reports every year for free at annualcreditreport dot com. Errors cost you tens of thousands. Court dismissed!",
         "judge vera banging her gavel, holding up a credit report stamped CLEAN, comic banner reads CHECK YEARLY"),
    ],
))

SCRIPTS.append((
    "judge_vera", ("Greg", "Faye"),
    "responding-to-court-summons", "Responding to a summons vs missing the hearing",
    [
        ("A two thousand dollar default judgment grew into fourteen thousand in three years. I am Judge Vera and today two debtors faced the same envelope. Court is in session!",
         "judge vera at the bench holding a court summons in one hand and her gavel in the other, comic burst banner reads TWO TO FOURTEEN THOUSAND"),
        ("Greg and Faye each receive a court summons from a debt collector for an old credit card debt of two thousand dollars from seven years ago.",
         "two adults greg and faye at their front doors each accepting an official looking envelope from a process server, both stamped SUMMONS"),
        ("Greg tosses the summons in a drawer because he believes the debt is too old to enforce. He never shows up to the hearing.",
         "man greg shoving a folded summons into a kitchen drawer, a calendar on the wall with the hearing date crossed out and ignored"),
        ("Faye calls a free legal aid clinic, learns the debt is past the statute of limitations, and shows up to court with the dates printed out.",
         "woman faye in a small legal aid office with a friendly attorney, a printed timeline labeled STATUTE OF LIMITATIONS spread on the desk"),
        ("Three years later Greg's two thousand turned into fourteen thousand with default judgment, interest, fees, and twenty five percent of every paycheck garnished.",
         "shocked man greg opening a paycheck stub showing a giant red GARNISHED 25 PERCENT line, comic banner reads FOURTEEN THOUSAND OWED"),
        ("Faye's case was dismissed in a single hearing because the debt was too old to sue on. She paid zero dollars and lost zero hours of pay.",
         "split scene, left side greg with a thin paycheck, right side faye walking out of a courthouse holding a paper stamped DISMISSED"),
        ("Always respond to a summons. Free legal aid exists in every state. Silence becomes a default judgment. Court dismissed!",
         "judge vera banging her gavel, holding up a paper labeled RESPOND IN WRITING, comic banner reads NEVER IGNORE A SUMMONS"),
    ],
))

SCRIPTS.append((
    "judge_vera", ("Owen", "Hope"),
    "saving-receipts-for-taxes", "Saving receipts vs guessing at tax time",
    [
        ("One year of saved receipts can mean three thousand two hundred dollars more back from the IRS. I am Judge Vera and today two freelancers learned why. Court is in session!",
         "judge vera at the bench holding up a receipt printed THREE THOUSAND TWO HUNDRED REFUND, comic burst banner reads SAVE THE PAPER"),
        ("Owen and Hope are both freelance designers who earned fifty thousand dollars last year and both work from home most days.",
         "two adults owen and hope at home offices with sketch tablets and laptops, ledger sheets nearby labeled FIFTY THOUSAND"),
        ("Owen throws out receipts as soon as they arrive and tells himself he will remember every business expense at tax time.",
         "man owen tossing a pile of crumpled receipts into a trash can, a thought bubble over his head with a question mark"),
        ("Hope drops every receipt into a free phone app the moment she gets it, tracks her car mileage, and tags each expense by category.",
         "woman hope at a coffee shop scanning a receipt into a phone app, a small icon labeled MILEAGE LOG and a folder labeled HOME OFFICE on her desk"),
        ("At tax time Owen guesses he had about one thousand two hundred dollars of expenses and writes that on the return to be safe.",
         "shocked man owen at a desk with a tax form, scribbling guessed numbers, a giant comic banner reading GUESSING above his head"),
        ("Hope's app printed a clean four thousand four hundred dollars in real expenses, all backed by paperwork. She got eight hundred dollars more in her refund than Owen.",
         "split scene, left side owen with a thin refund check, right side hope with a thicker check labeled EIGHT HUNDRED MORE"),
        ("Save every receipt as it happens. Use a free app. The IRS only honors what you can prove. Court dismissed!",
         "judge vera banging her gavel, holding up a phone with a receipt scanner app open, comic banner reads SCAN AS YOU GO"),
    ],
))

SCRIPTS.append((
    "judge_vera", ("Hank", "Joy"),
    "payday-loan-fine-print", "Reading payday loan terms vs signing fast",
    [
        ("A four hundred dollar payday loan can balloon into one thousand nine hundred dollars in six months. I am Judge Vera and today two borrowers needed cash fast. Court is in session!",
         "judge vera at the bench holding up a small loan paper stamped THREE HUNDRED NINETY ONE PERCENT APR, comic burst banner reads FOUR TO NINETEEN HUNDRED"),
        ("Hank and Joy both face a four hundred dollar car repair on a Friday and both walk into the same payday loan storefront after work.",
         "two adults hank and joy walking past a neon storefront sign reading FAST CASH PAYDAY LOANS, both holding a car repair bill labeled FOUR HUNDRED"),
        ("Hank signs the contract in two minutes, takes the cash, and never reads the page that lists the three hundred ninety one percent annual percentage rate.",
         "man hank at a counter signing a single page contract, a small printed line reading APR THREE HUNDRED NINETY ONE PERCENT highlighted in red"),
        ("Joy reads the contract, sees the rate, walks out, and instead asks her employer for a two week paycheck advance with zero interest.",
         "woman joy at her workplace human resources desk filling out a paycheck advance form, a friendly HR person handing her cash, comic banner reads ZERO INTEREST"),
        ("Six months later Hank has rolled the loan over four times, paid back nineteen hundred dollars, and still owes one hundred more.",
         "shocked man hank at a payday loan counter, comic banner above him reads NINETEEN HUNDRED PAID, his wallet small and empty"),
        ("Joy paid back four hundred dollars over two paychecks and zero in fees. Same emergency, two very different prices.",
         "split scene, left side hank with a thin wallet, right side joy with a calendar marked PAID IN FULL after two paychecks"),
        ("Payday loans are three hundred ninety one percent APR by law. Ask your employer, your credit union, or a friend first. Walk away from the storefront. Court dismissed!",
         "judge vera banging her gavel, holding up a paper stamped APR WARNING, comic banner reads ASK ELSEWHERE FIRST"),
    ],
))

SCRIPTS.append((
    "judge_vera", ("Kyle", "Ruby"),
    "small-claims-court", "Small claims court vs giving up",
    [
        ("Small claims court costs eighty dollars to file and can win you back five thousand dollars. I am Judge Vera and today two homeowners chose differently. Court is in session!",
         "judge vera at the bench holding up a small claims court filing form stamped EIGHTY DOLLARS, comic burst banner reads FIVE THOUSAND BACK"),
        ("Kyle and Ruby both hire the same handyman to renovate a kitchen, both pay a five thousand dollar deposit, and both wake up to find he has vanished.",
         "two adults kyle and ruby standing in matching empty kitchens, identical receipts in hand reading FIVE THOUSAND DEPOSIT"),
        ("Kyle posts angry one star reviews online, vents to his neighbors, and decides the money is gone forever.",
         "man kyle on a couch typing on a laptop with angry face, comic burst above the laptop reading ONE STAR REVIEW"),
        ("Ruby files a small claims case for eighty dollars, brings the signed contract, payment receipt, and photos of the unfinished kitchen as evidence.",
         "woman ruby in a courtroom holding a folder labeled CONTRACT and a stack of photos, calmly explaining to a judge"),
        ("Ninety days later Kyle still has nothing to show for his money and his negative reviews disappeared when the handyman closed his page.",
         "shocked man kyle staring at his laptop showing a deleted business profile, comic banner reads STILL OUT FIVE THOUSAND"),
        ("Ruby won a five thousand dollar judgment, garnished the handyman's bank account, and got her deposit back in full.",
         "split scene, left side kyle holding a blank refund line, right side ruby holding a check stamped FIVE THOUSAND RECOVERED"),
        ("Small claims court is cheap, fast, and self service. Bring your contract, your receipts, and your photos. Court dismissed!",
         "judge vera banging her gavel, holding up a small claims filing checklist, comic banner reads FILE THE CASE"),
    ],
))

SCRIPTS.append((
    "judge_vera", ("Luis", "Tara"),
    "security-deposit-back", "Getting your security deposit back vs losing it",
    [
        ("Landlords keep an estimated twenty seven billion dollars in security deposits every year. I am Judge Vera and today two renters fought back differently. Court is in session!",
         "judge vera at the bench holding a giant comic banner reading TWENTY SEVEN BILLION, courtroom spotlight on a stack of envelopes labeled DEPOSITS"),
        ("Luis and Tara both move out of one thousand five hundred dollar apartments in the same city on the same Saturday.",
         "two adults luis and tara moving boxes out of similar apartment doorways, both apartments numbered with rent flyers reading FIFTEEN HUNDRED"),
        ("Luis hands in the keys, takes no photos, and never sends a forwarding address or a written demand for his deposit back.",
         "man luis dropping keys into a landlord's hand, an empty kitchen behind him with no photos taken, dust in the corners"),
        ("Tara photographs every wall, every appliance, and every floor before handing in the keys, then mails a written demand letter with her forwarding address.",
         "woman tara in an empty apartment holding a phone with photo gallery open, an envelope labeled WRITTEN DEMAND LETTER on the counter"),
        ("Thirty days later Luis gets a tiny check for one hundred dollars with vague deductions for cleaning, paint, and a missing curtain rod.",
         "shocked man luis at a mailbox holding a check for ONE HUNDRED, a tiny paper labeled DEDUCTIONS LIST that lists eight items"),
        ("Tara gets one thousand four hundred and fifty dollars back because her photos proved every wall was clean. Same apartments, same landlord, very different results.",
         "split scene, left side luis with a small check, right side tara holding a check stamped FOURTEEN FIFTY"),
        ("Photograph every room before you hand in the keys. Send a written demand within thirty days. The law is on your side. Court dismissed!",
         "judge vera banging her gavel, holding a phone with a move out photo gallery, comic banner reads PHOTOS AND LETTERS"),
    ],
))

SCRIPTS.append((
    "judge_vera", ("Mark", "Iris"),
    "power-of-attorney", "Power of attorney done early vs done never",
    [
        ("A bank can freeze your parent's eighty thousand dollar account for six months without a power of attorney. I am Judge Vera. Court is in session!",
         "judge vera at the bench holding up a frozen bank account icon, comic burst banner reads EIGHTY THOUSAND FROZEN"),
        ("Mark and Iris each have a healthy parent in their late seventies. Each parent has eighty thousand dollars in checking and a stack of monthly bills.",
         "two adults mark and iris each visiting an aging parent in a tidy living room, a small banking statement on the coffee table reading EIGHTY THOUSAND"),
        ("Mark says they will set up a power of attorney later. He thinks his dad is healthy and there is no rush.",
         "man mark waving off a brochure labeled DURABLE POWER OF ATTORNEY in his father's living room, calendar on the wall with no plans"),
        ("Iris drives her mother to an attorney that month, pays two hundred dollars, and signs a durable power of attorney while her mom is sharp and healthy.",
         "woman iris and her mother in an attorney's office both signing a printed power of attorney form, a small fee paper reads TWO HUNDRED"),
        ("Six months later Mark's father has a stroke. The bank freezes the account and Mark spends six months in court paying lawyers to gain access.",
         "shocked man mark at a bank counter being told the account is frozen, a court stamped paper labeled GUARDIANSHIP CASE in the background"),
        ("Iris pays her mom's bills the same day she gets sick, manages her medical decisions, and never sees the inside of a probate court.",
         "split scene, left side mark in a courthouse hallway with a lawyer, right side iris paying bills online from her mother's bedside"),
        ("Set up a durable power of attorney while your parents are healthy. Two hundred dollars now beats six months of court later. Court dismissed!",
         "judge vera banging her gavel, holding up a power of attorney form stamped SIGNED, comic banner reads DO IT EARLY"),
    ],
))

SCRIPTS.append((
    "judge_vera", ("Neil", "Wren"),
    "workplace-documentation", "Documenting workplace harassment vs verbal complaints",
    [
        ("One employee won a thirty five thousand dollar settlement just because she had screenshots. I am Judge Vera and today two coworkers chose what to save. Court is in session!",
         "judge vera at the bench holding up a phone showing screenshots, comic burst banner reads THIRTY FIVE THOUSAND SETTLEMENT"),
        ("Neil and Wren both work at the same company under the same manager and both face the same string of inappropriate emails and meetings.",
         "two adults neil and wren in a shared office cubicle setting with the same boss visible behind a glass wall, mirror image"),
        ("Neil complains verbally to human resources, trusts the system, and keeps no copies of any of the messages on his work laptop.",
         "man neil in a human resources office with a tearful face, an HR rep nodding politely, a notepad with no notes"),
        ("Wren saves every email to a personal account, dates each incident, screenshots inappropriate chats, and stores everything in a private cloud folder.",
         "woman wren at a coffee shop laptop logging incidents into a personal email folder labeled EVIDENCE LOG, screenshots stacked beside her"),
        ("Three months later both file lawsuits. Neil's case is dismissed because the company wiped his work laptop and there are no records of his complaints.",
         "shocked man neil at a courtroom table with empty hands, a wiped laptop screen showing NO DATA"),
        ("Wren's lawsuit ends in a thirty five thousand dollar settlement and a written apology because her timeline and screenshots proved every single claim.",
         "split scene, left side neil walking out of court empty handed, right side wren holding a settlement check labeled THIRTY FIVE THOUSAND"),
        ("Document everything in writing. Save copies on a personal account. Verbal complaints disappear. Court dismissed!",
         "judge vera banging her gavel, holding a phone with a labeled folder reading EVIDENCE LOG, comic banner reads SAVE EVERYTHING"),
    ],
))

SCRIPTS.append((
    "judge_vera", ("Paul", "Rose"),
    "estate-planning", "Simple will vs dying without one",
    [
        ("Dying without a will can cost your family forty percent of your estate and fourteen months in court. I am Judge Vera. Court is in session!",
         "judge vera at the bench holding a will document stamped SIMPLE WILL, comic burst banner reads FORTY PERCENT LOST"),
        ("Paul and Rose are both fifty five years old, both have two hundred thousand dollars in assets, and both have a spouse and two adult children.",
         "two adults paul and rose at separate kitchen tables with house photos and bank statements, both papers reading TWO HUNDRED THOUSAND"),
        ("Paul says he will write a will eventually. He puts it off for a decade and never updates the beneficiaries on his retirement accounts.",
         "man paul shrugging at a brochure labeled SIMPLE WILL FOR THREE HUNDRED, calendar pages flipping by behind him"),
        ("Rose pays three hundred dollars for a basic will, names beneficiaries on every account, and stores copies with her family attorney.",
         "woman rose at a small attorney's desk signing a printed will, a small fee paper labeled THREE HUNDRED beside her"),
        ("Tragedy strikes both families. Paul's estate is stuck in probate court for fourteen months and his family pays eighty thousand dollars in fees and taxes.",
         "shocked family of paul standing outside a courthouse holding a paper stamped PROBATE OPEN, comic banner reads EIGHTY THOUSAND IN FEES"),
        ("Rose's family inherits the full two hundred thousand in three weeks because every account had a beneficiary and the will named one executor.",
         "split scene, left side paul's family in a long courthouse hallway, right side rose's family at a kitchen table with a check stamped FULL INHERITANCE"),
        ("A simple will and named beneficiaries cost three hundred dollars once and save your family eighty thousand. Do it this month. Court dismissed!",
         "judge vera banging her gavel, holding up a will stamped SIGNED with a checklist labeled BENEFICIARIES, comic banner reads PROTECT YOUR FAMILY"),
    ],
))


# ============================================================
# DETECTIVE CASH  (15 stories)
# ============================================================

SCRIPTS.append((
    "detective_cash", ("Marco", "Eva"),
    "romance-scam", "Romance scam — verifying vs falling for it",
    [
        ("Twenty thousand dollars vanishes the moment a stranger online says I love you. Case file 0042. Time of incident, eight pm on a Tuesday. Let me open the evidence.",
         "detective cash in a dim noir office holding a magnifying glass over a phone screen with a heart icon and a dollar sign, desk lamp casting long shadows"),
        ("Marco and Eva each match online with a charming overseas stranger who calls them every night for two months without ever video calling.",
         "split panel, left side man marco on a couch on the phone smiling, right side woman eva in a kitchen on the phone smiling, both with heart bubbles above"),
        ("Marco believes the love story, sends ten thousand dollars in gift cards for an emergency surgery, and then twenty thousand more for a fake plane ticket.",
         "man marco at a checkout counter buying stacks of gift cards, a comic banner above reads EMERGENCY SURGERY, register total reading TEN THOUSAND"),
        ("Eva refuses to send a single dollar without a video call. She runs his profile photo through a free reverse image search and finds it on a model's website.",
         "woman eva at a laptop with a reverse image search showing the same photo on a stock model website, a magnifying glass icon hovering"),
        ("Six weeks later Marco's overseas love disappears entirely. The bank cannot recover any gift card money and the FBI files a case file.",
         "shocked man marco at his kitchen table with a phone showing a blocked contact, comic banner reads NEVER REAL, FBI badge in the corner"),
        ("Eva blocks the scammer, reports the profile to the dating app, and never loses a cent. Same script, two very different endings.",
         "split scene, left side marco with an empty wallet, right side eva at her laptop with a button labeled REPORT AND BLOCK"),
        ("Reverse image search every photo. Refuse a video call equals a refused dollar. Gift card requests are always a scam. Case closed.",
         "detective cash holding up a magnifying glass over an evidence board labeled REVERSE IMAGE SEARCH, comic banner reads CASE CLOSED"),
    ],
))

SCRIPTS.append((
    "detective_cash", ("Bruno", "Diana"),
    "phishing-email", "Phishing email — verifying vs clicking",
    [
        ("Eight thousand dollars left a checking account in fifteen minutes after one wrong click. Case file 0043. Time of incident, six pm on a Friday. Let me open the evidence.",
         "detective cash in a dim noir office shining a desk lamp on a printed email with a red URGENT banner, magnifying glass in hand"),
        ("Bruno and Diana each receive the same urgent email from what looks like their bank with a subject line warning of suspicious account activity.",
         "split panel, left side man bruno on a phone reading the email, right side woman diana on a laptop reading the same email, both with worried faces"),
        ("Bruno taps the link, types in his username, password, and one time code, then watches eight thousand dollars wire out to an unknown account.",
         "man bruno tapping a phone screen at a kitchen table, a comic burst banner reading EIGHT THOUSAND WIRED with arrows leaving the bank"),
        ("Diana ignores the email link, opens her banking app directly, and sees no real alert at all. She forwards the email to her bank's fraud line.",
         "woman diana at a kitchen table opening her bank app from the home screen, a forwarding arrow pointing to an email labeled FRAUD AT BANK NAME"),
        ("By Monday morning Bruno is on the phone with the fraud department and his bank can only recover one thousand five hundred of the eight thousand dollars.",
         "shocked man bruno on the phone with a bank rep, comic banner reads SIX FIVE HUNDRED LOST, the wire trail leading off screen"),
        ("Diana never lost a cent and her bank flagged the phishing campaign for thousands of other customers because she reported it.",
         "split scene, left side bruno staring at a near empty bank balance, right side diana on a laptop with a thank you note from her bank"),
        ("Never click links in urgent emails. Always open the bank app yourself. Forward suspicious mail to fraud at the bank dot com. Case closed.",
         "detective cash holding up a magnifying glass over a phishing email crossed out with a red comic burst, banner reads CASE CLOSED"),
    ],
))

SCRIPTS.append((
    "detective_cash", ("Hugo", "Nina"),
    "crypto-rugpull", "Crypto rugpull — researching vs ape buying",
    [
        ("Fifty thousand dollars in crypto vanished in twenty four hours when the developers walked away. Case file 0044. Time of incident, midnight on launch day. Let me open the evidence.",
         "detective cash in a dim noir office holding a magnifying glass over a phone screen with a crashing crypto chart, candle bars red"),
        ("Hugo and Nina each see the same hyped meme coin trending on social media with promises of a one hundred times return in a single week.",
         "split panel, left side man hugo on a phone screen with a green meme coin chart, right side woman nina on the same phone, both with rocket icons"),
        ("Hugo apes in with twelve thousand dollars within minutes, never reads the contract, and never checks if the developers are anonymous.",
         "man hugo at a laptop typing fast with sweat drops, comic banner above reads TWELVE THOUSAND IN, a rocket icon flying up"),
        ("Nina opens a free contract scanner, sees the developers can mint unlimited tokens and have anonymous wallets, and walks away from the buy.",
         "woman nina at a laptop with a contract scanner showing red warnings labeled UNLIMITED MINT, ANON DEVS, magnifying glass icon"),
        ("Twenty four hours later the developers drain the liquidity pool. Hugo's twelve thousand dollar bag is now worth fourteen dollars total.",
         "shocked man hugo staring at his phone with a chart that crashed to zero, comic banner reads TWELVE THOUSAND TO FOURTEEN BUCKS"),
        ("Nina kept her twelve thousand dollars in an index fund and earned a modest two hundred dollars while Hugo lost almost everything.",
         "split scene, left side hugo with a destroyed crypto wallet, right side nina with a calm index fund chart trending up gently"),
        ("Always read the smart contract. Anonymous developers equal anonymous theft. If a coin promises one hundred times in a week, it is a trap. Case closed.",
         "detective cash with a magnifying glass over a contract paper stamped UNLIMITED MINT WARNING, comic banner reads CASE CLOSED"),
    ],
))

SCRIPTS.append((
    "detective_cash", ("Frank", "Lucy"),
    "fake-check-overpayment", "Fake check overpayment — stopping the wire vs sending it",
    [
        ("A four thousand dollar fake check left one seller in the hole for three thousand five hundred dollars. Case file 0045. Time of incident, noon on a Wednesday. Let me open the evidence.",
         "detective cash in a noir office holding a magnifying glass over a paper check stamped FAKE, dollar bills floating away from a shocked face"),
        ("Frank and Lucy each list the same five hundred dollar piece of furniture online and both receive the same buyer offering to overpay by mistake.",
         "split panel, left side man frank with a couch photo on a phone, right side woman lucy with the same couch photo, both with overpayment messages on screen"),
        ("Frank deposits a four thousand dollar cashier check from the buyer and wires the extra three thousand five hundred dollars to a fake mover the buyer recommends.",
         "man frank at a bank ATM depositing a check, then at a wire desk sending three thousand five hundred dollars, comic banner reads FAST WIRE"),
        ("Lucy notices the overpayment trick, refuses the deal, and reports the scammer's profile to the marketplace within minutes.",
         "woman lucy at a kitchen table on a laptop closing the chat and pressing a button labeled REPORT, magnifying glass icon hovering"),
        ("Eight days later Frank's bank discovers the cashier check is forged. The four thousand is reversed but his three thousand five hundred dollar wire is gone forever.",
         "shocked man frank at a bank counter with a paper stamped CHECK BOUNCED, comic banner reads THREE FIVE HUNDRED GONE"),
        ("Lucy still has her couch and zero loss. The same scam played out twice with two very different endings.",
         "split scene, left side frank holding an empty wallet beside an empty space where the couch was, right side lucy in her living room with the couch"),
        ("Cashier checks can take ten days to bounce. Never wire the difference back. If a buyer overpays, the deal is the trap. Case closed.",
         "detective cash with a magnifying glass over a forged check stamped FAKE, comic banner reads CASE CLOSED"),
    ],
))

SCRIPTS.append((
    "detective_cash", ("Walt", "Anna"),
    "identity-theft", "Identity theft — freezing your credit vs ignoring the breach",
    [
        ("A single data breach drained one victim for fifteen thousand dollars in new loans she never opened. Case file 0046. Time of incident, breach day. Let me open the evidence.",
         "detective cash in a noir office holding a magnifying glass over a stack of stolen ID cards, a red banner reads DATA BREACH"),
        ("Walt and Anna both get notified that their social security number leaked in a major retailer breach last month.",
         "split panel, left side man walt holding a paper labeled BREACH NOTICE, right side woman anna holding the same notice, both at home mailboxes"),
        ("Walt assumes the free credit monitoring is enough, never freezes his credit, and skips the password change reminders.",
         "man walt tossing a breach notice on a kitchen counter, a comic banner reading IT WONT HAPPEN TO ME above his head"),
        ("Anna places a free credit freeze at all three bureaus that same evening, sets up two factor authentication, and changes every password.",
         "woman anna at a laptop on three bureau websites placing freezes, a small lock icon stamped on each page, a comic banner reads CREDIT FROZEN"),
        ("Six months later Walt finds two new auto loans and a credit card opened in his name totaling fifteen thousand dollars in fraudulent debt.",
         "shocked man walt opening a stack of credit notices, a giant red comic banner reading FIFTEEN THOUSAND IN FRAUD looms behind him"),
        ("Every fraud attempt against Anna was rejected at the bureau because her file was frozen. She lost zero dollars and zero hours.",
         "split scene, left side walt buried in fraud notices, right side anna with a phone showing a freeze status labeled PROTECTED"),
        ("Place a free credit freeze at all three bureaus today. Use a unique password and two factor authentication. Breaches will keep happening. Case closed.",
         "detective cash with a magnifying glass over a credit report stamped FROZEN, comic banner reads CASE CLOSED"),
    ],
))

SCRIPTS.append((
    "detective_cash", ("Vince", "Maya"),
    "irs-impersonation", "IRS impersonation call — hanging up vs paying",
    [
        ("The IRS will never ask for gift cards, but one caller still walked off with three thousand dollars in Apple cards. Case file 0047. Time of incident, noon. Let me open the evidence.",
         "detective cash in a noir office holding a phone receiver with a red caller ID labeled FAKE IRS, magnifying glass over an Apple card stack"),
        ("Vince and Maya each get the same call from a man claiming to be an IRS agent demanding three thousand dollars or police arrive in one hour.",
         "split panel, left side man vince on a landline with a worried face, right side woman maya on a cell phone with a calm face"),
        ("Vince panics, drives to a store, buys three thousand dollars in Apple gift cards, and reads the codes back to the caller over the phone.",
         "man vince at a register buying stacks of Apple gift cards, comic banner reads THREE THOUSAND IN CARDS, sweat drops on his face"),
        ("Maya laughs, hangs up, and calls the real IRS number from the back of her last tax return to confirm there is no balance due.",
         "woman maya at a kitchen table calling the official IRS number printed on a tax form, a magnifying glass over the printed line"),
        ("Two hours later Vince realizes he has been scammed. The cards are drained and the caller's number is disconnected.",
         "shocked man vince staring at empty gift card receipts on a kitchen table, comic banner reads ALL DRAINED"),
        ("Maya never lost a cent and reported the call to the Treasury fraud line so other people would be warned.",
         "split scene, left side vince surrounded by empty gift card wrappers, right side maya at a laptop on the Treasury website filling a report"),
        ("The IRS sends letters first, never calls demanding gift cards, and never threatens immediate arrest. Hang up and call them yourself. Case closed.",
         "detective cash with a magnifying glass over a printed IRS letter stamped LEGITIMATE, comic banner reads CASE CLOSED"),
    ],
))

SCRIPTS.append((
    "detective_cash", ("Rex", "Stella"),
    "job-offer-scam", "Job offer scam — verifying vs paying upfront",
    [
        ("A fake remote job demanded eight hundred dollars for equipment and disappeared the next day. Case file 0048. Time of incident, hiring day. Let me open the evidence.",
         "detective cash in a noir office holding a magnifying glass over a printed job offer letter with a red FAKE stamp, dollar bills flying away"),
        ("Rex and Stella each get the same too good to be true remote work offer paying ninety thousand dollars with no interview required.",
         "split panel, left side man rex on a laptop with a job offer email, right side woman stella on the same email, both with raised eyebrows"),
        ("Rex sends the recruiter eight hundred dollars in Zelle for the home office equipment they promise to ship, then never hears from them again.",
         "man rex at a laptop sending Zelle for EIGHT HUNDRED DOLLARS, a comic burst above reads PAY FOR LAPTOP"),
        ("Stella searches the company name plus scam, finds three Reddit warnings, and ignores the offer.",
         "woman stella at a laptop with a search bar reading COMPANY NAME SCAM showing red warning posts, magnifying glass icon over the screen"),
        ("Three days later Rex has no laptop, no recruiter, and no job. The Zelle payment is irreversible and the email account is closed.",
         "shocked man rex staring at his laptop with a bounced email and a deleted recruiter contact, comic banner reads EIGHT HUNDRED GONE"),
        ("Stella keeps applying through real company websites and signs a real job offer two weeks later with no upfront fee.",
         "split scene, left side rex with empty hands, right side stella at a laptop signing a real digital job offer, comic banner reads HIRED"),
        ("Real employers never ask new hires to pay for equipment. Search the company plus the word scam. If they push Zelle, walk away. Case closed.",
         "detective cash with a magnifying glass over a job offer stamped LEGIT, comic banner reads CASE CLOSED"),
    ],
))

SCRIPTS.append((
    "detective_cash", ("Otto", "Cleo"),
    "investment-too-good", "Too-good investment vs real diversified investing",
    [
        ("A guaranteed ten percent monthly return turned out to be a Ponzi scheme that took twenty five thousand dollars. Case file 0049. Time of incident, pitch day. Let me open the evidence.",
         "detective cash in a noir office holding a magnifying glass over a glossy brochure stamped GUARANTEED TEN PERCENT, dollar bills crumbling"),
        ("Otto and Cleo each get pitched by a smooth talking acquaintance promising guaranteed ten percent monthly returns from a private fund.",
         "split panel, left side man otto at a coffee shop with a salesman, right side woman cleo at the same coffee shop with the same salesman, brochure on the table"),
        ("Otto invests twenty five thousand dollars from his savings, gets two months of small deposits, and feels like a financial genius.",
         "man otto at a laptop typing a transfer for TWENTY FIVE THOUSAND, a comic burst banner reads MONTHLY RETURNS GUARANTEED"),
        ("Cleo asks for an SEC registration number, calls a real fee only financial advisor, and learns there is no such thing as a guaranteed ten percent monthly return.",
         "woman cleo at a kitchen table with a phone calling a real advisor, a paper labeled SEC REGISTRATION CHECK with no result on it"),
        ("Six months later Otto's smooth talking acquaintance is arrested. His twenty five thousand dollars vanished into a Ponzi scheme paying old investors with new money.",
         "shocked man otto on a couch reading a news article about a Ponzi arrest, comic banner reads TWENTY FIVE THOUSAND GONE"),
        ("Cleo's same money sits in a low cost index fund earning a steady eight percent a year and is fully insured by the brokerage.",
         "split scene, left side otto staring at a frozen account, right side cleo with a brokerage app showing a steady upward index fund chart"),
        ("Guaranteed returns are always a scam. Real investing is boring, regulated, and slow. Check SEC dot gov before sending a dime. Case closed.",
         "detective cash with a magnifying glass over a brokerage statement stamped INSURED, comic banner reads CASE CLOSED"),
    ],
))

SCRIPTS.append((
    "detective_cash", ("Saul", "Pam"),
    "tech-support-popup", "Tech support pop-up scam — closing the tab vs calling",
    [
        ("A pop up promising to clean a virus drained two thousand dollars from a senior's checking account. Case file 0050. Time of incident, six pm. Let me open the evidence.",
         "detective cash in a noir office holding a magnifying glass over a laptop screen with a flashing red VIRUS ALERT pop up window"),
        ("Saul and Pam are both seventy two years old. Both visit a news site and both see the same flashing pop up warning of a virus on their computer.",
         "split panel, left side senior man saul at a desktop, right side senior woman pam at a laptop, both screens showing the same red warning pop up"),
        ("Saul calls the toll free number on the pop up, gives a stranger remote access, and watches two thousand dollars wire out of his checking account.",
         "shocked senior man saul on a phone with a fake tech rep, comic banner above reads REMOTE ACCESS, money symbols leaving the screen"),
        ("Pam closes the browser tab, restarts her computer, and the warning never returns. She tells her grandson about it that evening.",
         "senior woman pam at a kitchen table closing a laptop lid with a smile, a small note labeled CLOSE THE TAB on the fridge behind her"),
        ("By bedtime Saul has lost two thousand dollars and a stranger has copies of his banking passwords because he typed them while remote sharing.",
         "shocked senior man saul at a kitchen table staring at a near empty bank statement, comic banner reads TWO THOUSAND GONE"),
        ("Pam never lost a cent. Her grandson helped her install a free pop up blocker so it would not happen again.",
         "split scene, left side saul on the phone with the bank, right side pam and a grandson installing a pop up blocker on a laptop"),
        ("Real tech support never calls or pops up to warn you. Close the tab. Restart the computer. Never give anyone remote access. Case closed.",
         "detective cash with a magnifying glass over a closed pop up window crossed out with a red comic burst, banner reads CASE CLOSED"),
    ],
))

SCRIPTS.append((
    "detective_cash", ("Reese", "Holly"),
    "marketplace-overpayment", "Marketplace buyer overpayment trap",
    [
        ("A marketplace buyer sent fake money screenshots and made off with a one thousand dollar phone. Case file 0051. Time of incident, parking lot. Let me open the evidence.",
         "detective cash in a noir office holding a magnifying glass over a phone screen showing a fake Zelle confirmation with red FAKE stamp"),
        ("Reese and Holly each list the same one thousand dollar used phone on Marketplace and both arrange to meet a buyer in a busy parking lot.",
         "split panel, left side man reese with a phone in hand at a coffee shop lot, right side woman holly with the same phone at the same lot"),
        ("Reese hands over the phone after a buyer shows him a Zelle pending screenshot. The screenshot is fake and the money never arrives.",
         "man reese in a parking lot handing a boxed phone to a stranger, the stranger holding a phone screen labeled PENDING with a red FAKE stamp"),
        ("Holly refuses to release the phone until the money is fully cleared in her bank app, not just a screenshot. The buyer leaves without it.",
         "woman holly in a parking lot holding a boxed phone close, looking at her real bank app on a phone, comic banner reads MUST CLEAR FIRST"),
        ("By dinner time Reese realizes the money never arrived. The buyer is unreachable and Marketplace cannot recover the phone.",
         "shocked man reese at a kitchen table refreshing his bank app showing zero new deposits, comic banner reads PHONE GONE"),
        ("Holly relisted and sold the phone two days later to a real buyer. Her bank app showed the funds clear before she handed anything over.",
         "split scene, left side reese with empty hands, right side holly handing a boxed phone to a verified buyer with a green CLEARED notice"),
        ("Pending screenshots are not money. Wait until your bank app shows funds available before you hand over anything. Case closed.",
         "detective cash with a magnifying glass over a bank app screen labeled CLEARED, comic banner reads CASE CLOSED"),
    ],
))

SCRIPTS.append((
    "detective_cash", ("Bo", "Sage"),
    "grandparent-scam", "Grandparent emergency phone scam — verifying vs panicking",
    [
        ("A frantic phone call from a fake grandson convinced one grandparent to wire six thousand dollars in twenty minutes. Case file 0052. Time of incident, ten pm. Let me open the evidence.",
         "detective cash in a noir office holding a magnifying glass over a phone receiver with a fake voice icon, dollar bills flying out"),
        ("Bo and Sage each get a late night phone call from a young man crying that he is in jail and needs six thousand dollars in bail money tonight.",
         "split panel, left side senior man bo on a landline at night, right side senior woman sage on a landline, both with worried frowns"),
        ("Bo recognizes the voice as his grandson, drives to a money transfer counter, and wires six thousand dollars to a stranger's name within twenty minutes.",
         "senior man bo at a money transfer counter, a clerk processing a wire labeled SIX THOUSAND, comic banner reads PANIC SEND"),
        ("Sage hangs up, calls her real grandson directly on his cell phone, and learns he is asleep in his own bed with no jail story at all.",
         "senior woman sage at a kitchen phone calling her grandson, a phone screen showing her grandson safely asleep at home"),
        ("By morning Bo has lost six thousand dollars and the wire transfer cannot be reversed. The fake grandson story has been used on dozens of seniors.",
         "shocked senior man bo at a kitchen table with a wire receipt, comic banner reads SIX THOUSAND GONE, news clipping about a scam ring"),
        ("Sage spent zero dollars and called the local sheriff to warn other seniors in the neighborhood about the same scam.",
         "split scene, left side bo with empty hands at the kitchen table, right side sage at a coffee shop chatting with friends and a sheriff"),
        ("Always hang up and call the family member directly. Never wire money based on a phone call. Set a family code word. Case closed.",
         "detective cash with a magnifying glass over a sticky note labeled FAMILY CODE WORD, comic banner reads CASE CLOSED"),
    ],
))

SCRIPTS.append((
    "detective_cash", ("Cole", "Sasha"),
    "qr-code-skimmer", "QR code skimmer scam — typing the URL vs scanning blind",
    [
        ("A fake parking meter QR sticker stole one driver's full credit card details in twenty seconds. Case file 0053. Time of incident, lunch hour. Let me open the evidence.",
         "detective cash in a noir office holding a magnifying glass over a parking meter with a fake QR sticker, red SCAM stamp on the sticker"),
        ("Cole and Sasha both park downtown for lunch, see a parking meter with a QR code, and both pull out their phones to pay for parking.",
         "split panel, left side man cole at a parking meter with a phone scanning, right side woman sasha at the same meter with a phone in hand"),
        ("Cole scans the QR code, lands on a fake page that perfectly mimics the city site, and types in his full credit card number to pay five dollars.",
         "man cole at a parking meter typing a credit card on a phone, a fake URL bar reading CITY DASH PARKING DOT TOP visible"),
        ("Sasha types the city's real parking URL by hand into her browser, pays the five dollars on the official site, and never scans the sticker.",
         "woman sasha at the same meter typing a real URL into a phone browser, a small green lock icon over the address bar"),
        ("By the next morning Cole's credit card has eleven hundred dollars in fraudulent online charges from three different countries.",
         "shocked man cole at a kitchen table reading a credit card statement with three red foreign charges, comic banner reads ELEVEN HUNDRED IN FRAUD"),
        ("Sasha disputed nothing, paid five dollars for parking, and lost zero hours of her life calling the bank.",
         "split scene, left side cole on the phone with bank fraud, right side sasha walking away from the parking meter with a coffee"),
        ("Always type parking and government URLs by hand. Stickers can be peeled and replaced. The lock icon is your friend. Case closed.",
         "detective cash with a magnifying glass over a phone browser with a green padlock and a typed URL, comic banner reads CASE CLOSED"),
    ],
))

SCRIPTS.append((
    "detective_cash", ("Jett", "Kira"),
    "fake-zelle-screen", "Fake Zelle screenshot — confirming in app vs trusting screens",
    [
        ("A photoshopped Zelle screen cost one rideshare driver four hundred dollars in cash for nothing. Case file 0054. Time of incident, late night. Let me open the evidence.",
         "detective cash in a noir office holding a magnifying glass over a phone screen showing a fake Zelle confirmation with a PHOTOSHOPPED red stamp"),
        ("Jett and Kira each agree to sell a four hundred dollar concert ticket to a stranger who insists on paying through Zelle right at the meet up.",
         "split panel, left side man jett with a paper concert ticket, right side woman kira with the same ticket, both meeting buyers at a venue"),
        ("Jett glances at the buyer's phone showing a green sent screen, hands over the ticket, and walks off feeling good about the sale.",
         "man jett at a venue glancing at a stranger's phone showing a green SENT screen, the ticket changing hands"),
        ("Kira opens her own Zelle app first, refreshes until the funds actually appear in her balance, and only then hands over the ticket.",
         "woman kira at the same venue opening her own Zelle app, the screen reading FUNDS RECEIVED, then handing over the ticket"),
        ("By the time Jett checks his own app the next morning, no Zelle payment ever arrived and the buyer's profile is deleted.",
         "shocked man jett on a couch refreshing his Zelle app at zero, comic banner reads NEVER ARRIVED"),
        ("Kira's payment cleared in real time and her ticket sale was clean. Same buyer trick, two very different choices.",
         "split scene, left side jett with empty hands, right side kira with a phone showing a green RECEIVED status and a smile"),
        ("Never trust the buyer's screen. Open your own app. Wait for the funds to clear. Screenshots are easy to fake. Case closed.",
         "detective cash with a magnifying glass over a real Zelle confirmation labeled CLEARED, comic banner reads CASE CLOSED"),
    ],
))

SCRIPTS.append((
    "detective_cash", ("Tony", "Lila"),
    "lottery-winner-scam", "Lottery winner scam — never paying to claim",
    [
        ("A fake lottery winner letter demanded twenty five hundred dollars in fees and paid out nothing. Case file 0055. Time of incident, opening the mail. Let me open the evidence.",
         "detective cash in a noir office holding a magnifying glass over a glossy fake lottery letter stamped CONGRATULATIONS WINNER, dollar bills crumbling"),
        ("Tony and Lila each open the same glossy letter telling them they have won eight hundred thousand dollars in a foreign lottery they never entered.",
         "split panel, left side man tony at a mailbox with a glossy letter, right side woman lila with the same letter, both at home"),
        ("Tony wires twenty five hundred dollars in processing fees as the letter instructs, expecting his winnings to arrive within a week.",
         "man tony at a money transfer counter wiring TWENTY FIVE HUNDRED DOLLARS to claim a lottery, comic banner reads PROCESSING FEE"),
        ("Lila tosses the letter in the recycling bin, knowing real lotteries do not need entrants to pay fees and do not contact winners by mail out of the blue.",
         "woman lila at home dropping the letter into a recycling bin, a small note on the wall reading NEVER PAY TO CLAIM"),
        ("Eight weeks later Tony has lost twenty five hundred dollars in wire fees and the next letter demands eight thousand more for tax clearance.",
         "shocked man tony at a mailbox holding a second letter labeled MORE FEES, comic banner reads TWO FIVE HUNDRED LOST"),
        ("Lila lost zero dollars and reported the letter to the postal inspection service so they could investigate the scam ring.",
         "split scene, left side tony with empty hands, right side lila at a laptop on the postal inspection website filing a report"),
        ("If you have to pay to collect a prize, it is not a prize. Real lotteries deduct taxes from winnings, not the other way around. Case closed.",
         "detective cash with a magnifying glass over a fake lottery letter crossed out, comic banner reads CASE CLOSED"),
    ],
))

SCRIPTS.append((
    "detective_cash", ("Carla", "Jed"),
    "fake-rental-listing", "Fake rental listing — viewing in person vs wiring blind",
    [
        ("A fake rental listing took two thousand dollars in deposits before anyone realized the apartment did not exist. Case file 0056. Time of incident, move in week. Let me open the evidence.",
         "detective cash in a noir office holding a magnifying glass over a glossy fake rental listing photo with a red FAKE LISTING stamp"),
        ("Carla and Jed each find the same gorgeous one bedroom apartment online priced four hundred dollars below the market in a great neighborhood.",
         "split panel, left side woman carla at a laptop with the listing photo, right side man jed at the same listing, both with hopeful faces"),
        ("Carla wires a two thousand dollar deposit and first month rent without seeing the apartment because the so called owner is overseas.",
         "woman carla at a laptop sending a wire labeled TWO THOUSAND DEPOSIT, comic banner reads NEVER SAW IT"),
        ("Jed insists on visiting the apartment in person, drives over, and discovers the real tenants who have been living there for six years.",
         "man jed at the apartment door talking to a confused real tenant, a small banner reads REAL TENANT, key icon crossed out"),
        ("By move in day Carla learns the listing was fake. Her two thousand dollars is gone forever and the so called owner is unreachable.",
         "shocked woman carla outside an apartment building with moving boxes, comic banner reads TWO THOUSAND GONE, no key in hand"),
        ("Jed kept renting his current place and avoided a wire scam that has hit dozens of renters in the same city this year.",
         "split scene, left side carla with no apartment, right side jed in his current cozy apartment with coffee, comic banner reads SAVED"),
        ("Never wire a deposit on a rental you have not toured. Verify the owner with the county records office. Case closed.",
         "detective cash with a magnifying glass over a county records page labeled VERIFIED OWNER, comic banner reads CASE CLOSED"),
    ],
))


# ============================================================
# COACH VAULT  (15 stories)
# ============================================================

SCRIPTS.append((
    "coach_vault", ("Brad", "Tess"),
    "emergency-fund-1000", "Building a 1000 dollar emergency fund",
    [
        ("Seventy eight percent of Americans cannot cover a one thousand dollar emergency. I am Coach Vault and these two trainees are about to do it the easy way and the hard way. Today's training session begins now!",
         "coach vault in a bright gym blowing a whistle, holding a clipboard, comic burst banner reads ONE THOUSAND DOLLAR EMERGENCY FUND, dumbbells in the background"),
        ("Brad and Tess are both twenty four years old, both make three thousand dollars a month, and both have exactly zero dollars saved.",
         "split panel, left side man brad in workout gear with a wallet showing zero, right side woman tess in workout gear with the same wallet"),
        ("Brad keeps spending every paycheck. He swears he will start saving once he gets a raise next year.",
         "man brad on a couch with takeout boxes and shopping bags, a comic banner above reads SAVE LATER, calendar pages flipping"),
        ("Tess sets up a thirty dollar weekly auto transfer to a high yield savings account every Friday morning, no excuses.",
         "woman tess at a phone screen tapping AUTO TRANSFER THIRTY DOLLARS, a small piggy bank with a green up arrow"),
        ("Eight months later Brad's car battery dies, he puts a two hundred dollar repair on a credit card, and starts paying twenty nine percent interest.",
         "shocked man brad at an auto repair counter swiping a credit card, comic banner reads TWENTY NINE PERCENT INTEREST"),
        ("Tess saves one thousand and forty dollars without missing a single transfer. She pays a future repair in cash and her savings keep growing.",
         "split scene, left side brad with a credit card statement, right side tess with a savings app showing ONE THOUSAND FORTY in green"),
        ("Thirty dollars a week beats willpower every time. Automate the transfer the day your paycheck lands. Drop and give me twenty bucks!",
         "coach vault blowing a whistle on a gym floor, holding a clipboard reading AUTOMATE TODAY, comic burst banner reads TWENTY BUCKS"),
    ],
))

SCRIPTS.append((
    "coach_vault", ("Drew", "Cara"),
    "save-twenty-percent", "Saving 20 percent vs spending every dollar",
    [
        ("Save twenty percent of every paycheck and you can retire ten years earlier. I am Coach Vault and today these two new hires take very different routes. Today's training session begins now!",
         "coach vault in a gym holding up a giant pie chart with a twenty percent slice highlighted in green, comic burst banner reads TWENTY PERCENT RULE"),
        ("Drew and Cara both land their first jobs at age twenty two earning four thousand dollars a month after taxes.",
         "split panel, left side man drew in workout gear with a paycheck slip, right side woman cara in workout gear with an identical paycheck"),
        ("Drew lives on every single dollar of his paycheck and tells himself he will save once he makes more money in a few years.",
         "man drew on a treadmill exhausted with shopping bags piling up beside him, a comic banner reads SPEND IT ALL"),
        ("Cara automates eight hundred dollars per paycheck into a brokerage account before she ever sees the money in checking.",
         "woman cara at a phone screen tapping AUTO INVEST EIGHT HUNDRED, a brokerage app showing a steady upward chart"),
        ("Five years later Drew's salary doubled but he still saves nothing. His lifestyle grew with every raise.",
         "shocked man drew on a couch surrounded by big purchases, comic banner reads ZERO SAVED FIVE YEARS, calendar with five ticked years"),
        ("Cara has saved sixty thousand dollars in five years even before any market gains. She is on track to retire at fifty one.",
         "split scene, left side drew on the treadmill still going, right side cara with a brokerage app showing SIXTY THOUSAND and a finish line"),
        ("Pay yourself first. Twenty percent off the top before any spending. The number on your check matters less than the number you save. Drop and give me twenty bucks!",
         "coach vault blowing a whistle, holding a clipboard reading PAY YOURSELF FIRST, comic burst banner reads TWENTY BUCKS"),
    ],
))

SCRIPTS.append((
    "coach_vault", ("Chase", "Lana"),
    "cut-daily-expense", "Cutting one daily coffee vs keeping every habit",
    [
        ("One daily coffee equals one thousand eight hundred dollars a year. I am Coach Vault and today two coworkers see what one habit costs. Today's training session begins now!",
         "coach vault in a gym holding a coffee cup with a price tag reading FIVE DOLLARS, comic burst banner reads EIGHTEEN HUNDRED A YEAR"),
        ("Chase and Lana both work at the same office and both buy a five dollar coffee on the way to work every single weekday.",
         "split panel, left side man chase walking out of a coffee shop with a cup, right side woman lana doing the same on the same street"),
        ("Chase keeps his daily coffee habit, says it is harmless, and never tracks the total cost over the year.",
         "man chase at his desk with a coffee cup, comic banner reads HARMLESS HABIT, a calendar marked with coffee cups every day"),
        ("Lana switches to a home brewer for two hundred dollars and brings coffee in a thermos. She redirects the savings into investing.",
         "woman lana in a kitchen with a small coffee brewer and a thermos, an arrow pointing to an investing app on a phone"),
        ("Twelve months later Chase has spent one thousand eight hundred dollars on coffee and has nothing to show for it.",
         "shocked man chase at a desk surrounded by paper coffee cups, comic banner reads EIGHTEEN HUNDRED IN CUPS"),
        ("Lana spent two hundred dollars on a brewer and one hundred on beans, then invested fifteen hundred. With market growth she ends the year up over sixteen hundred dollars.",
         "split scene, left side chase with empty cups, right side lana with a brewer at home and an investing app reading SIXTEEN HUNDRED"),
        ("One small daily expense times twenty years equals a real fortune. Pick the cheapest one and kill it. Drop and give me twenty bucks!",
         "coach vault blowing a whistle, holding a clipboard reading KILL ONE DAILY EXPENSE, comic burst banner reads TWENTY BUCKS"),
    ],
))

SCRIPTS.append((
    "coach_vault", ("Bryce", "Skye"),
    "thirty-day-no-spend", "30-day no-spend challenge vs business as usual",
    [
        ("A thirty day no spend challenge can put one thousand two hundred dollars back in your pocket. I am Coach Vault and today two friends try it. Today's training session begins now!",
         "coach vault in a gym holding a clipboard with a thirty day calendar grid, comic burst banner reads NO SPEND CHALLENGE"),
        ("Bryce and Skye both spend about three hundred dollars a week on takeout, online shopping, and impulse buys outside of bills.",
         "split panel, left side man bryce on a couch with delivery bags, right side woman skye with the same delivery bags, both at home"),
        ("Bryce laughs at the no spend challenge, keeps ordering takeout, and shops every weekend on his favorite app.",
         "man bryce on a couch swiping a phone with a CART icon glowing, comic banner reads BUSINESS AS USUAL"),
        ("Skye writes a list of approved spending categories on her fridge, deletes shopping apps, and freezes her credit card in a block of ice.",
         "woman skye in a kitchen with a freezer block of ice with a credit card frozen inside, a fridge list labeled APPROVED SPENDING"),
        ("Thirty days later Bryce checks his bank statement and realizes he spent twelve hundred dollars on small things and is back to broke.",
         "shocked man bryce at a kitchen table with a printed bank statement, comic banner reads TWELVE HUNDRED VAPORIZED"),
        ("Skye finishes the month with eleven hundred dollars saved, transfers it straight into her emergency fund, and feels in control again.",
         "split scene, left side bryce with empty hands, right side skye holding a phone with a savings app reading ELEVEN HUNDRED"),
        ("Try one thirty day no spend month a year. The savings buy you a real emergency fund. Drop and give me twenty bucks!",
         "coach vault blowing a whistle, holding a clipboard reading NO SPEND THIRTY DAYS, comic burst banner reads TWENTY BUCKS"),
    ],
))

SCRIPTS.append((
    "coach_vault", ("Trey", "Quinn"),
    "debt-snowball", "Debt snowball workout vs minimum payments",
    [
        ("Two trainees with the same fifteen thousand dollar debt finished four years apart. I am Coach Vault and today the snowball beats the minimums. Today's training session begins now!",
         "coach vault in a gym holding two clipboards labeled SNOWBALL and MINIMUMS, comic burst banner reads FOUR YEARS APART"),
        ("Trey and Quinn each owe fifteen thousand dollars across four credit cards and each have an extra five hundred dollars a month to throw at debt.",
         "split panel, left side man trey at a table with four credit card statements, right side woman quinn with the same four statements"),
        ("Trey pays the minimum on all four cards and uses the extra five hundred for new clothes and concerts because he feels stretched.",
         "man trey on a couch swiping a card for concert tickets, comic banner reads MINIMUMS ONLY, four credit card statements stack with no progress"),
        ("Quinn pays the minimum on three, throws the entire extra five hundred at the smallest balance, then rolls each payment forward as she clears each card.",
         "woman quinn at a kitchen table crossing off a small credit card balance, an arrow rolling the payment to the next card"),
        ("Five years later Trey still owes thirteen thousand dollars and is paying nineteen percent interest with no end in sight.",
         "shocked man trey at a couch staring at a stack of statements still labeled THIRTEEN THOUSAND, comic banner reads STILL STUCK"),
        ("Quinn paid every card off in twenty seven months and then redirected the same five hundred per month into investing for retirement.",
         "split scene, left side trey buried in card statements, right side quinn with all four cards stamped PAID and an investing app showing growth"),
        ("List your debts smallest to largest. Pay minimums on all but the smallest. Hit the smallest with everything. Drop and give me twenty bucks!",
         "coach vault blowing a whistle, holding a clipboard reading SNOWBALL ORDER, comic burst banner reads TWENTY BUCKS"),
    ],
))

SCRIPTS.append((
    "coach_vault", ("Jay", "Robin"),
    "automate-savings", "Automating savings vs relying on willpower",
    [
        ("People who automate save three times more than people who rely on willpower. I am Coach Vault and these two athletes prove it. Today's training session begins now!",
         "coach vault in a gym holding two trophies, one labeled AUTO and one labeled WILLPOWER, comic burst banner reads THREE TIMES MORE"),
        ("Jay and Robin both want to save four hundred dollars a month from their paychecks for a future house down payment.",
         "split panel, left side man jay in workout gear with a paycheck slip and a tiny house photo, right side woman robin with the same"),
        ("Jay plans to manually move four hundred dollars to savings on the last day of every month after he sees what is left in checking.",
         "man jay at a laptop on payday checking a bank balance, comic banner reads MANUAL TRANSFER LATER, calendar circles around payday"),
        ("Robin sets up an automatic transfer for four hundred dollars one day after every payday. The money disappears into savings before she sees it.",
         "woman robin at a phone screen tapping AUTO TRANSFER FOUR HUNDRED, a small calendar with two paydays a month and arrows to a savings vault"),
        ("Two years later Jay actually transferred only nine hundred dollars total because something always came up in checking by month end.",
         "shocked man jay at a kitchen table looking at a savings balance reading NINE HUNDRED, comic banner reads WILLPOWER FAILED"),
        ("Robin's automation moved nine thousand six hundred dollars into her down payment fund. Same goal, same paycheck, ten times the result.",
         "split scene, left side jay with thin savings, right side robin with a savings app reading NINE THOUSAND SIX HUNDRED"),
        ("Automate every savings goal the day after payday. Willpower runs out. Direct deposit does not. Drop and give me twenty bucks!",
         "coach vault blowing a whistle, holding a clipboard reading AUTOMATE EVERYTHING, comic burst banner reads TWENTY BUCKS"),
    ],
))

SCRIPTS.append((
    "coach_vault", ("Cody", "Brooke"),
    "track-every-expense", "Tracking expenses vs eyeballing it",
    [
        ("People who track expenses cut twenty three percent of their spending in the first month. I am Coach Vault and today two trainees check the score. Today's training session begins now!",
         "coach vault in a gym holding a giant scoreboard labeled SPENDING SCORE, comic burst banner reads TWENTY THREE PERCENT CUT"),
        ("Cody and Brooke both bring home four thousand dollars a month and both have no idea where their money goes by the end of each month.",
         "split panel, left side man cody at a table shrugging at empty bank app, right side woman brooke at the same table, both with question marks"),
        ("Cody eyeballs his spending. He swears he eats out about three times a week and shops only when he really needs something.",
         "man cody on a couch waving a hand at a phone screen, comic banner reads I THINK I SPEND ABOUT, question marks floating around"),
        ("Brooke logs every single expense for a month in a free budget app and reviews her categories every Sunday morning over coffee.",
         "woman brooke at a kitchen table with a phone budget app open, weekly review notes labeled SUNDAY REVIEW pinned to the fridge"),
        ("Cody is shocked to learn his bank cleared eight hundred dollars in restaurants and four hundred in random delivery fees that month.",
         "shocked man cody at a kitchen table reading a bank statement, comic banner reads TWELVE HUNDRED IN FOOD, his eyes wide"),
        ("Brooke's tracking exposed three hundred dollars in subscriptions and two hundred in impulse buys. She cut both and saved five hundred dollars in month one.",
         "split scene, left side cody with a giant restaurant bill, right side brooke with a savings app showing FIVE HUNDRED IN ONE MONTH"),
        ("Track every expense for thirty days. The score makes the changes obvious. You cannot fix what you do not measure. Drop and give me twenty bucks!",
         "coach vault blowing a whistle, holding a clipboard reading TRACK EVERY DOLLAR, comic burst banner reads TWENTY BUCKS"),
    ],
))

SCRIPTS.append((
    "coach_vault", ("Wade", "Piper"),
    "cash-envelope-budget", "Cash envelope budget vs swiping every card",
    [
        ("Cash spenders save eighteen percent more than card swipers on the same income. I am Coach Vault and today the envelopes win the round. Today's training session begins now!",
         "coach vault in a gym holding three envelopes labeled GROCERIES, GAS, FUN, comic burst banner reads CASH WINS"),
        ("Wade and Piper both budget two thousand dollars a month for variable spending like groceries, gas, and entertainment.",
         "split panel, left side man wade with a credit card, right side woman piper with three labeled envelopes of cash, both in kitchens"),
        ("Wade swipes a credit card for everything. He tells himself he will pay it off at month end without checking the running total.",
         "man wade at a grocery checkout swiping a credit card, comic banner reads SWIPE AND FORGET, receipt curling out of the register"),
        ("Piper pulls cash on payday into three envelopes labeled groceries, gas, and fun. When an envelope is empty, that category is closed for the month.",
         "woman piper at a kitchen counter splitting cash into three envelopes, a small chalkboard reads ENVELOPE EMPTY EQUALS NO MORE"),
        ("Wade's credit card statement shows two thousand four hundred dollars of variable spending, four hundred dollars over budget, again.",
         "shocked man wade at a kitchen table with a card statement reading FOUR HUNDRED OVER, comic banner reads OVER AGAIN"),
        ("Piper finished the month with thirty dollars left in the fun envelope and zero credit card balance. The visible cash made the limits real.",
         "split scene, left side wade with a high card statement, right side piper with envelopes showing leftover cash and a clean card statement"),
        ("Try cash envelopes for the categories you overspend. Swiping numbs the brain. Cash makes the cost visible. Drop and give me twenty bucks!",
         "coach vault blowing a whistle, holding three envelopes labeled GROCERIES GAS FUN, comic burst banner reads TWENTY BUCKS"),
    ],
))

SCRIPTS.append((
    "coach_vault", ("Tate", "Sienna"),
    "cooking-at-home", "Cooking at home five nights vs eating out",
    [
        ("Eating out five nights a week costs three thousand six hundred dollars more a year than cooking at home. I am Coach Vault. Today's training session begins now!",
         "coach vault in a gym holding a frying pan in one hand and a takeout bag in the other, comic burst banner reads THREE THOUSAND SIX HUNDRED A YEAR"),
        ("Tate and Sienna are both single, both work nine hours a day, and both think cooking is too much effort after work.",
         "split panel, left side man tate flopped on a couch with a delivery bag, right side woman sienna in a kitchen with groceries on the counter"),
        ("Tate orders delivery five nights a week. Each meal averages eighteen dollars after fees, tips, and surge pricing.",
         "man tate on a couch unpacking a delivery bag with a receipt labeled EIGHTEEN DOLLARS, comic banner reads FIVE NIGHTS A WEEK"),
        ("Sienna does Sunday meal prep for sixty dollars in groceries that covers five dinners, two lunches, and three breakfasts.",
         "woman sienna at a kitchen counter with five meal prep containers and a grocery receipt labeled SIXTY DOLLARS"),
        ("Twelve months later Tate has spent four thousand six hundred dollars on delivery dinners and gained ten pounds.",
         "shocked man tate at a couch with takeout boxes piled up, comic banner reads FORTY SIX HUNDRED IN DELIVERY"),
        ("Sienna spent one thousand dollars on home groceries for the same five dinners a week and put thirty six hundred dollars into her savings account.",
         "split scene, left side tate with delivery boxes, right side sienna with a meal prep calendar and a savings app reading THIRTY SIX HUNDRED SAVED"),
        ("Sunday meal prep beats Friday night delivery every time. Cook once, eat all week, save thousands. Drop and give me twenty bucks!",
         "coach vault blowing a whistle, holding a clipboard with a meal prep schedule, comic burst banner reads TWENTY BUCKS"),
    ],
))

SCRIPTS.append((
    "coach_vault", ("Brock", "Layla"),
    "cancel-subscriptions", "Canceling unused subscriptions vs autopilot",
    [
        ("The average person pays for two hundred and twenty dollars a month in subscriptions and uses about half of them. I am Coach Vault. Today's training session begins now!",
         "coach vault in a gym holding a giant phone screen with a long list of subscription icons, comic burst banner reads TWO HUNDRED TWENTY A MONTH"),
        ("Brock and Layla both have a streaming bundle, two music apps, three fitness apps, a meditation app, and four random app trials they forgot.",
         "split panel, left side man brock at a phone screen full of subscription icons, right side woman layla at the same phone, both wide eyed"),
        ("Brock leaves all subscriptions on autopay because he might use them again someday and does not want to lose his old logins.",
         "man brock on a couch shrugging at a phone with a long subscription list, comic banner reads MIGHT USE LATER"),
        ("Layla audits her bank statement, finds eleven subscriptions, cancels seven she has not opened in three months, and downgrades two more.",
         "woman layla at a kitchen table with a printed bank statement, a red pen circling and crossing off seven subscription line items"),
        ("Twelve months later Brock has paid two thousand six hundred and forty dollars in subscription fees and uses only four of them regularly.",
         "shocked man brock staring at a credit card statement, comic banner reads TWO THOUSAND SIX HUNDRED FORTY GONE"),
        ("Layla cut her subscription bill from two hundred twenty to fifty five dollars a month and put one hundred sixty five back in her budget.",
         "split scene, left side brock with a heavy bill, right side layla with a phone showing FIFTY FIVE A MONTH and a savings increase"),
        ("Audit subscriptions every six months. Cancel anything you have not used in ninety days. They are silent budget killers. Drop and give me twenty bucks!",
         "coach vault blowing a whistle, holding a clipboard with a CANCEL list, comic burst banner reads TWENTY BUCKS"),
    ],
))

SCRIPTS.append((
    "coach_vault", ("Reid", "Harper"),
    "side-hustle-weekends", "Side hustle weekends vs Netflix weekends",
    [
        ("Two hours every Saturday turned into ten thousand dollars in one year. I am Coach Vault and today the side hustle pays. Today's training session begins now!",
         "coach vault in a gym holding a stopwatch in one hand and a stack of cash in the other, comic burst banner reads TEN THOUSAND IN A YEAR"),
        ("Reid and Harper are both salaried employees making fifty five thousand a year and both have free Saturdays and Sundays.",
         "split panel, left side man reid on a couch, right side woman harper at a laptop, both in workout gear with weekends marked on a calendar"),
        ("Reid spends every weekend on the couch streaming and ordering takeout. He says he is too tired from his day job to do anything else.",
         "man reid sprawled on a couch with takeout and a remote, comic banner reads TIRED, weekend calendar marked NETFLIX"),
        ("Harper does freelance graphic design for two hours every Saturday and another two on Sunday morning, charging forty dollars an hour.",
         "woman harper at a desk with a sketch tablet and a laptop, a small clock reading FOUR HOURS, dollar bills stacked beside the keyboard"),
        ("After twelve months Reid has the same checking balance he started with and his streaming bill went up.",
         "shocked man reid at a kitchen table with a flat bank statement, comic banner reads SAME BALANCE, takeout boxes around him"),
        ("Harper banked nine thousand six hundred dollars in side income, paid off her car, and started building a real emergency fund.",
         "split scene, left side reid on the couch, right side harper with a brokerage app showing NINE THOUSAND SIX HUNDRED"),
        ("Trade four weekend hours for an income stream you control. The money is not the only win, the skill is yours forever. Drop and give me twenty bucks!",
         "coach vault blowing a whistle, holding a clipboard reading FOUR HOURS A WEEKEND, comic burst banner reads TWENTY BUCKS"),
    ],
))

SCRIPTS.append((
    "coach_vault", ("Beck", "Olive"),
    "negotiate-bills", "Negotiating bills vs accepting them",
    [
        ("Twenty minutes on the phone can knock six hundred dollars off your annual bills. I am Coach Vault and today two friends call their providers. Today's training session begins now!",
         "coach vault in a gym holding a phone in one hand and a calculator in the other, comic burst banner reads SIX HUNDRED A YEAR"),
        ("Beck and Olive both pay one hundred forty dollars for internet and one hundred ten for a cell phone plan that has not changed in three years.",
         "split panel, left side man beck holding two bills, right side woman olive holding the same two bills, both at home"),
        ("Beck assumes the prices are fixed and pays whatever the bill says every single month without ever calling.",
         "man beck on a couch tossing bills onto a table, comic banner reads JUST PAY IT, autopay icons spinning"),
        ("Olive calls each provider, says she is comparing plans with a competitor, and politely asks for the loyalty or retention department.",
         "woman olive at a kitchen table on a phone with a calm smile, a notepad reading RETENTION DEPARTMENT and competitor logos beside her"),
        ("Twelve months later Beck has paid three thousand dollars on bills he never questioned and his autopay quietly raised both bills last winter.",
         "shocked man beck at a kitchen table with a credit card statement, comic banner reads THREE THOUSAND ON BILLS"),
        ("Olive cut both bills by twenty five dollars a month each. She saved six hundred dollars in a year for one twenty minute phone call.",
         "split scene, left side beck staring at a heavy bill, right side olive at a phone with a new bill labeled FIFTY DOLLARS LESS PER MONTH"),
        ("Call every provider once a year. Ask for retention. Mention a competitor. They will not lower the bill unless you ask. Drop and give me twenty bucks!",
         "coach vault blowing a whistle, holding a clipboard reading CALL ONCE A YEAR, comic burst banner reads TWENTY BUCKS"),
    ],
))

SCRIPTS.append((
    "coach_vault", ("Kit", "Aspen"),
    "buy-used-vs-new", "Buying used vs new — depreciation drill",
    [
        ("A new car loses thirty percent of its value the moment you drive it off the lot. I am Coach Vault and today these two car shoppers learn the lesson. Today's training session begins now!",
         "coach vault in a gym pointing at a giant comic burst banner reading THIRTY PERCENT GONE, a model car beside him"),
        ("Kit and Aspen both have eight thousand dollars saved and both need a reliable car for their forty mile daily commute.",
         "split panel, left side man kit in a dealership lot looking at new cars, right side woman aspen at a private seller's driveway looking at a used sedan"),
        ("Kit puts eight thousand dollars down on a new thirty thousand dollar SUV and finances the rest at seven percent over six years.",
         "man kit at a dealership signing papers under a new SUV, comic banner reads TWENTY TWO THOUSAND FINANCED"),
        ("Aspen buys a four year old reliable sedan for nine thousand dollars cash plus a one thousand dollar trade in. Zero monthly payment.",
         "woman aspen handing cash to a private seller in a driveway, a small price tag reading NINE THOUSAND, no loan papers"),
        ("Three years later Kit's SUV is worth fourteen thousand dollars but he still owes seventeen thousand. He is upside down on the loan.",
         "shocked man kit at a kitchen table with a loan statement reading SEVENTEEN THOUSAND OWED next to a car valuation reading FOURTEEN THOUSAND"),
        ("Aspen's used sedan is worth six thousand and she owes nothing. She has saved eighteen thousand dollars in skipped car payments and invested it.",
         "split scene, left side kit with a heavy loan statement, right side aspen with a brokerage app reading EIGHTEEN THOUSAND INVESTED"),
        ("Buy three to five year old reliable cars in cash or short term loans. New cars are bad workouts for your wallet. Drop and give me twenty bucks!",
         "coach vault blowing a whistle, holding a clipboard reading USED RELIABLE SEDAN, comic burst banner reads TWENTY BUCKS"),
    ],
))

SCRIPTS.append((
    "coach_vault", ("Finn", "June"),
    "annual-fitness-test", "Annual financial fitness test vs autopilot",
    [
        ("People who run an annual money checkup save forty percent more over a decade. I am Coach Vault and today these two trainees take the test. Today's training session begins now!",
         "coach vault in a gym holding a clipboard labeled ANNUAL FITNESS TEST, comic burst banner reads FORTY PERCENT MORE"),
        ("Finn and June both opened savings, retirement, and credit accounts five years ago and both have not reviewed any of them since.",
         "split panel, left side man finn at a desk shrugging, right side woman june at a desk with a fresh notepad, both surrounded by old bank papers"),
        ("Finn never logs in to check fees, rates, or asset allocations. He assumes everything is still fine and his old setup is good enough.",
         "man finn on a couch ignoring a stack of statements, comic banner reads SET AND FORGET, dust on the papers"),
        ("June books one Saturday morning every January to log into every account, list balances, fees, and rates, and rebalance her retirement.",
         "woman june at a kitchen table with a checklist labeled JANUARY MONEY DAY and laptops open to brokerage and bank tabs"),
        ("Five years later Finn discovers his savings is at zero point zero one percent and his retirement fund is in a fund with one point five percent fees.",
         "shocked man finn at a laptop staring at a fee disclosure, comic banner reads ONE POINT FIVE PERCENT FEES"),
        ("June moved her savings to a four point five percent high yield account and switched to a low cost index fund. Same money, eighteen thousand more dollars over five years.",
         "split scene, left side finn with a thin balance, right side june with a brokerage chart showing EIGHTEEN THOUSAND MORE in five years"),
        ("Block one Saturday a year. Log into every account. Compare rates and fees. The annual money day is the cheapest workout you will ever do. Drop and give me twenty bucks!",
         "coach vault blowing a whistle, holding a clipboard labeled MONEY DAY JANUARY, comic burst banner reads TWENTY BUCKS"),
    ],
))

SCRIPTS.append((
    "coach_vault", ("Heath", "Willa"),
    "pay-yourself-first", "Pay yourself first vs pay yourself last",
    [
        ("People who pay themselves first save four times more than people who save what is left. I am Coach Vault and today the order matters. Today's training session begins now!",
         "coach vault in a gym holding a giant arrow pointing at SAVINGS FIRST then BILLS, comic burst banner reads FOUR TIMES MORE"),
        ("Heath and Willa each take home five thousand dollars a month and both want to save one thousand dollars per month for the future.",
         "split panel, left side man heath at a desk with a paycheck, right side woman willa at a desk with the same paycheck, both with goal notes"),
        ("Heath pays his rent, food, gas, and fun first, then tries to save what is left. By the twenty fifth there is rarely anything to move.",
         "man heath at a kitchen table with bills paid and an empty checking screen, comic banner reads NOTHING LEFT TO SAVE"),
        ("Willa transfers one thousand dollars to savings the morning after every paycheck, before she pays a single bill or buys a single coffee.",
         "woman willa at a phone screen tapping AUTO TRANSFER ONE THOUSAND right after a payday icon"),
        ("Twelve months later Heath has saved nine hundred dollars total because life always filled the budget before savings did.",
         "shocked man heath at a savings app reading NINE HUNDRED, calendar pages flipping past with no transfers"),
        ("Willa saved twelve thousand dollars in twelve months. Same income, same bills, just a different transfer order.",
         "split scene, left side heath with thin savings, right side willa with a savings app reading TWELVE THOUSAND in big green numbers"),
        ("Move your savings the morning after every paycheck, before any bill is paid. Future you is the only paycheck that compounds. Drop and give me twenty bucks!",
         "coach vault blowing a whistle, holding a clipboard reading SAVINGS FIRST, comic burst banner reads TWENTY BUCKS"),
    ],
))


# ============================================================
# DOCTOR DOLLAR  (15 stories)
# ============================================================

SCRIPTS.append((
    "doctor_dollar", ("Lily", "Eve"),
    "credit-score-580-vs-780", "Credit score 580 vs 780 — five year financial health",
    [
        ("A two hundred point credit score difference can cost you eighty thousand dollars on a single mortgage. I am Doctor Dollar. Today's patient checkup starts here.",
         "doctor dollar in a doctor's office holding a clipboard with a credit score chart, a patient room behind her, comic burst banner reads EIGHTY THOUSAND DOLLAR DIFFERENCE"),
        ("Lily and Eve are both thirty two, both buying their first three hundred thousand dollar home, but Lily's score is five hundred eighty and Eve's is seven hundred eighty.",
         "split panel, left side woman lily at a clinic desk with a credit chart reading FIVE EIGHTY, right side woman eve with a chart reading SEVEN EIGHTY"),
        ("Lily missed payments two years ago, has high credit utilization, and never disputed two errors on her credit report.",
         "woman lily at a desk with a credit report covered in red flags labeled MISSED PAYMENT and HIGH UTILIZATION, errors uncircled"),
        ("Eve pays every bill on auto, keeps her balances under ten percent of her limits, and disputes every error within thirty days.",
         "woman eve at a kitchen table with a clean credit report stamped GREEN, autopay icons next to every bill, a low utilization gauge"),
        ("Lily's mortgage rate is eight point one percent. Her monthly payment is two thousand two hundred and twenty dollars and she is house poor.",
         "shocked woman lily at a closing table holding a paper labeled EIGHT POINT ONE PERCENT and a calculator reading TWENTY TWO TWENTY A MONTH"),
        ("Eve's mortgage rate is six point one percent. Same loan, eighty two thousand dollars less paid over thirty years and a comfortable budget every month.",
         "split scene, left side lily with a heavy mortgage statement, right side eve with a paper labeled SIX POINT ONE PERCENT and a smile"),
        ("Pay every bill on time, keep utilization under ten percent, and dispute every error. A clean score is the cheapest medicine in personal finance. See you next visit. Stay financially healthy!",
         "doctor dollar holding a clipboard with a credit score chart climbing to seven hundred eighty, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))

SCRIPTS.append((
    "doctor_dollar", ("Grace", "Caleb"),
    "debt-to-income", "Debt to income 50 vs 20 percent — long term prognosis",
    [
        ("A debt to income ratio of fifty percent denies you for almost every mortgage. I am Doctor Dollar and these two patients have very different vital signs. Today's patient checkup starts here.",
         "doctor dollar holding a clipboard labeled DEBT TO INCOME, a giant gauge showing fifty percent in red and twenty percent in green"),
        ("Grace and Caleb both bring home seventy thousand dollars a year. Grace owes thirty five thousand a year in debt payments. Caleb owes only fourteen thousand.",
         "split panel, left side woman grace with a stack of debt statements, right side man caleb with a single small loan paper, both at the doctor's desk"),
        ("Grace has two car loans, three credit cards near the limit, and a personal loan she took out for a vacation last year.",
         "woman grace at a desk surrounded by car payment papers, credit card statements, and a vacation receipt, vital signs gauge in red"),
        ("Caleb drives a paid off used car, keeps one credit card under ten percent, and has only a small federal student loan on auto pay.",
         "man caleb at the same desk with a single small loan statement labeled STUDENT LOAN, autopay icon, calm vital signs gauge in green"),
        ("Both apply for a three hundred thousand dollar mortgage. Grace is denied for a debt to income ratio of fifty percent.",
         "shocked woman grace at a loan officer's desk holding a denial letter, comic banner reads DENIED FIFTY PERCENT DTI"),
        ("Caleb is approved at six point one percent and his debt to income is twenty percent. Same income, very different prognosis.",
         "split scene, left side grace with a denial letter, right side caleb at a closing table with a paper labeled APPROVED"),
        ("Lower your monthly debt before you apply for any new loan. The lender does not care what you make, they care what is left. See you next visit. Stay financially healthy!",
         "doctor dollar holding a clipboard with a green DTI gauge under twenty percent, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))

SCRIPTS.append((
    "doctor_dollar", ("Nate", "Daisy"),
    "audit-net-worth", "Auditing net worth yearly vs never tracking",
    [
        ("Patients who track net worth yearly grow it six times faster. I am Doctor Dollar and today these two get on the scale. Today's patient checkup starts here.",
         "doctor dollar in a doctor's office holding a clipboard labeled NET WORTH SCALE, comic burst banner reads SIX TIMES FASTER"),
        ("Nate and Daisy are both thirty five, both bring home eighty thousand dollars a year, and both have been working for a decade with no real plan.",
         "split panel, left side man nate at the doctor's desk shrugging, right side woman daisy at the desk with a notebook, both with paychecks reading EIGHTY THOUSAND"),
        ("Nate has never added up his assets and debts. He has no idea if he is moving forward or sliding backward.",
         "man nate at a couch with bills scattered around, comic banner reads NO IDEA, a question mark over a piggy bank icon"),
        ("Daisy fills out a one page net worth sheet every January, listing every account, every debt, and every asset she owns.",
         "woman daisy at a kitchen table with a printed sheet labeled NET WORTH JANUARY, columns for ASSETS and DEBTS clearly listed"),
        ("Nate's checkup reveals he owes twenty thousand dollars more than he owns and has been losing ground every year for five years.",
         "shocked man nate looking at a calculator showing NEGATIVE TWENTY THOUSAND, comic banner reads UNDERWATER FOR FIVE YEARS"),
        ("Daisy's net worth has grown sixty thousand dollars over the same five years just by paying attention and adjusting course every January.",
         "split scene, left side nate with a negative balance sheet, right side daisy with a chart labeled SIXTY THOUSAND POSITIVE GROWTH"),
        ("Track net worth once a year on one page. The score makes the next move obvious. You cannot grow what you do not measure. See you next visit. Stay financially healthy!",
         "doctor dollar holding up a chart with a rising net worth line, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))

SCRIPTS.append((
    "doctor_dollar", ("Eli", "Hannah"),
    "401k-match", "Maxing the 401k match vs leaving it on the table",
    [
        ("Skipping a four percent employer match is leaving twenty thousand dollars on the table over five years. I am Doctor Dollar. Today's patient checkup starts here.",
         "doctor dollar holding a clipboard labeled FREE MONEY MATCH, comic burst banner reads TWENTY THOUSAND ON THE TABLE"),
        ("Eli and Hannah both work for the same company that matches four percent into the 401k and both make seventy five thousand dollars a year.",
         "split panel, left side man eli at the doctor's desk with a benefits packet, right side woman hannah at the desk with the same packet"),
        ("Eli skipped the 401k enrollment form because he wanted every dollar in his paycheck right now and felt overwhelmed by the choices.",
         "man eli on a couch tossing a benefits packet aside, comic banner reads SKIPPED THE FORM, an empty 401k icon"),
        ("Hannah signed up the first day, contributed four percent, captured the full employer match, and chose a low cost target date fund.",
         "woman hannah at a kitchen table signing a 401k form, a small icon labeled MATCH FOUR PERCENT highlighted in green"),
        ("Five years later Eli still has zero in his 401k. He missed twenty thousand dollars in employer money and any growth on top.",
         "shocked man eli staring at an empty 401k balance on a phone, comic banner reads ZERO MATCH ZERO GROWTH"),
        ("Hannah's 401k has forty thousand dollars and growing. Half came from her, half came from her employer and the market.",
         "split scene, left side eli with empty hands, right side hannah with a brokerage app reading FORTY THOUSAND with a target date fund label"),
        ("Always capture the full employer match before any other investing. It is a one hundred percent return on day one. See you next visit. Stay financially healthy!",
         "doctor dollar holding a clipboard with a four percent match arrow pointing up, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))

SCRIPTS.append((
    "doctor_dollar", ("Aaron", "Naomi"),
    "roth-ira-25-vs-45", "Roth IRA at 25 vs starting at 45",
    [
        ("Twenty extra years of compound growth turned six thousand a year into one million dollars. I am Doctor Dollar. Today's patient checkup starts here.",
         "doctor dollar holding a clipboard with a giant compound growth chart, comic burst banner reads TWENTY YEARS EQUALS A MILLION"),
        ("Aaron and Naomi each plan to retire at sixty five and each can afford to put six thousand dollars a year into a Roth IRA.",
         "split panel, left side man aaron at the doctor's desk with a retirement plan, right side woman naomi at the desk with the same plan"),
        ("Aaron waits until age forty five to open his Roth IRA. He thinks he is too young to bother with retirement at twenty five.",
         "man aaron at twenty five on a couch waving off a retirement brochure, calendar pages flipping forward to age forty five"),
        ("Naomi opens her Roth IRA at age twenty five, sets a one hundred fifteen dollar weekly auto contribution, and forgets it for forty years.",
         "woman naomi at a laptop at age twenty five clicking AUTO INVEST, a target date fund chart labeled ROTH IRA"),
        ("By sixty five Aaron contributed one hundred twenty thousand dollars but his Roth is only worth two hundred eighty thousand because he started so late.",
         "shocked older man aaron at a kitchen table with a balance reading TWO HUNDRED EIGHTY THOUSAND, comic banner reads LATE START"),
        ("Naomi contributed two hundred forty thousand and her Roth is worth one million two hundred thousand dollars because compounding had forty years to work.",
         "split scene, left side aaron with a smaller balance, right side older woman naomi with a brokerage app reading ONE POINT TWO MILLION"),
        ("Open the Roth at twenty five even with twenty dollars a week. Time in the market beats timing the market. See you next visit. Stay financially healthy!",
         "doctor dollar holding a clipboard labeled START EARLY, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))

SCRIPTS.append((
    "doctor_dollar", ("Levi", "Clara"),
    "high-interest-vs-index", "High-interest debt vs the same money in an index fund",
    [
        ("Investing while carrying twenty four percent credit card debt is like exercising on a broken leg. I am Doctor Dollar. Today's patient checkup starts here.",
         "doctor dollar holding a clipboard labeled DEBT VS INDEX, comic burst banner reads CREDIT CARDS BURN FAST"),
        ("Levi and Clara each have ten thousand dollars in credit card debt at twenty four percent and ten thousand dollars in cash to deploy.",
         "split panel, left side man levi at a desk with credit card statements and ten thousand cash, right side woman clara at the desk with the same"),
        ("Levi puts the ten thousand into an index fund hoping for ten percent returns and pays only the minimum on his credit cards.",
         "man levi at a laptop investing TEN THOUSAND in an index fund, comic banner reads MINIMUM PAYMENT ONLY, credit card statements glowing red"),
        ("Clara pays off the ten thousand dollar credit card balance in one shot and only after that starts dollar cost averaging into her index fund.",
         "woman clara at a kitchen table writing a check labeled PAY OFF CARDS, then setting up an auto invest of two hundred a week"),
        ("After three years Levi's index fund is up roughly three thousand dollars but his credit card debt grew to twelve thousand. He is down a thousand dollars overall.",
         "shocked man levi at a desk with a chart showing index fund up three thousand and a card balance reading TWELVE THOUSAND"),
        ("Clara is debt free and has invested seven thousand dollars over the same three years. Her net wealth grew by ten thousand dollars instead of shrinking.",
         "split scene, left side levi with mixed numbers, right side clara with a clean credit card statement and a brokerage app reading TEN THOUSAND UP"),
        ("Always pay off any debt over eight percent before investing. The market cannot beat a guaranteed twenty four percent loss. See you next visit. Stay financially healthy!",
         "doctor dollar holding a clipboard labeled PAY OFF FIRST, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))

SCRIPTS.append((
    "doctor_dollar", ("Jonah", "Mara"),
    "term-life-insurance", "Term life insurance at 30 vs trying to buy at 50",
    [
        ("A twenty year term life policy at age thirty costs five times less than the same policy at age fifty. I am Doctor Dollar. Today's patient checkup starts here.",
         "doctor dollar holding a clipboard with a term life premium chart, comic burst banner reads FIVE TIMES MORE LATER"),
        ("Jonah and Mara are both thirty years old, both have one young child, and both want a five hundred thousand dollar term life policy.",
         "split panel, left side man jonah at a desk with a baby photo, right side woman mara at the desk with the same baby photo, both healthy"),
        ("Jonah waits to buy a policy because life insurance feels like something for older people. He plans to get it in his fifties.",
         "man jonah on a couch waving off an insurance brochure, calendar pages flipping toward age fifty"),
        ("Mara locks in a thirty dollar a month twenty year term policy at age thirty while she is still healthy and the rate is low.",
         "woman mara at a kitchen table signing a small policy labeled TERM LIFE THIRTY DOLLARS A MONTH, a child photo on the wall"),
        ("By age fifty Jonah is diagnosed with high blood pressure and high cholesterol. The same policy now costs one hundred sixty five dollars a month.",
         "shocked older man jonah at a doctor's office reading a quote labeled ONE HUNDRED SIXTY FIVE, comic banner reads HEALTH ADDED COST"),
        ("Mara's premium has been thirty dollars a month for two decades and her family has been protected the entire time.",
         "split scene, left side jonah with a pricey new quote, right side mara with a paid up policy and a happy family photo"),
        ("Buy term life insurance the year you have anyone who depends on your income. Healthy and young is the cheapest you will ever be. See you next visit. Stay financially healthy!",
         "doctor dollar holding a clipboard labeled TERM LIFE THIRTY, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))

SCRIPTS.append((
    "doctor_dollar", ("Ezra", "Wendy"),
    "review-insurance-yearly", "Reviewing insurance yearly vs autopilot",
    [
        ("Reviewing your insurance once a year saves the average household six hundred dollars. I am Doctor Dollar. Today's patient checkup starts here.",
         "doctor dollar holding a clipboard labeled INSURANCE REVIEW, comic burst banner reads SIX HUNDRED A YEAR"),
        ("Ezra and Wendy each pay for auto, home, and umbrella insurance and each have not looked at their policies in five full years.",
         "split panel, left side man ezra with three insurance papers, right side woman wendy with the same three papers, both at home"),
        ("Ezra leaves all three on autopay and assumes the rates are the same as they always were and the coverage still fits.",
         "man ezra on a couch tossing insurance bills onto a side table, comic banner reads SAME OLD RATES"),
        ("Wendy schedules one hour every July to compare quotes from three insurers and to make sure her coverage limits still match her current life.",
         "woman wendy at a kitchen table with three quote sheets labeled QUOTE A QUOTE B QUOTE C, a calendar marked JULY REVIEW"),
        ("Ezra discovers he has been paying for renters insurance on a home he bought three years ago and his auto coverage is only state minimum.",
         "shocked man ezra holding three policy papers with red error stamps, comic banner reads WRONG COVERAGE"),
        ("Wendy's review knocked four hundred dollars off her auto bill and added an umbrella policy that covers her at one million dollars for ten dollars a month.",
         "split scene, left side ezra with bad coverage, right side wendy with three updated policies labeled OPTIMIZED"),
        ("Set a yearly insurance day. Compare three quotes. Match coverage to your real life. The wrong policy is worse than no policy. See you next visit. Stay financially healthy!",
         "doctor dollar holding a clipboard labeled YEARLY REVIEW, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))

SCRIPTS.append((
    "doctor_dollar", ("Asher", "Greta"),
    "three-month-emergency-fund", "Three-month emergency fund vs paycheck to paycheck",
    [
        ("A three month emergency fund cuts the chance of a debt spiral by eighty percent. I am Doctor Dollar. Today's patient checkup starts here.",
         "doctor dollar holding a clipboard labeled THREE MONTHS, comic burst banner reads EIGHTY PERCENT FEWER DEBT SPIRALS"),
        ("Asher and Greta each spend three thousand dollars a month on rent, food, and bills and each have a steady job paycheck to paycheck.",
         "split panel, left side man asher at a desk with a budget reading THREE THOUSAND A MONTH, right side woman greta with the same budget"),
        ("Asher keeps zero dollars in savings. He puts every leftover dollar into hobbies and trusts that nothing will ever go wrong.",
         "man asher on a couch with hobby gear and concert tickets, comic banner reads NOTHING WILL GO WRONG, empty piggy bank"),
        ("Greta builds a nine thousand dollar emergency fund over eighteen months by saving five hundred dollars a month into a high yield account.",
         "woman greta at a kitchen table with a savings app reading NINE THOUSAND, a small piggy bank with a checkmark"),
        ("Asher loses his job for two months. He puts rent and groceries on credit cards and ends the layoff with seven thousand dollars in new debt at twenty four percent.",
         "shocked man asher at a kitchen table with credit card statements piling up, comic banner reads SEVEN THOUSAND IN DEBT"),
        ("Greta uses her emergency fund to cover those same two months, never touches a credit card, and rebuilds the fund within a year.",
         "split scene, left side asher buried in card debt, right side greta with a calmer face and an emergency fund app rebuilding"),
        ("Stack three months of bare bones expenses in a high yield savings account. It buys you time, and time is the rarest medicine. See you next visit. Stay financially healthy!",
         "doctor dollar holding a clipboard with a calendar showing three months of saved bills, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))

SCRIPTS.append((
    "doctor_dollar", ("Silas", "Rosa"),
    "annual-financial-physical", "Annual financial physical vs ignoring your money",
    [
        ("Just like a yearly physical, a yearly money checkup catches problems early and adds years of healthy growth. I am Doctor Dollar. Today's patient checkup starts here.",
         "doctor dollar holding a clipboard labeled ANNUAL FINANCIAL PHYSICAL, a stethoscope around her neck, comic burst banner reads CATCH IT EARLY"),
        ("Silas and Rosa each have a job, a checking account, a 401k, and a credit card. Both have not reviewed any of these accounts in seven years.",
         "split panel, left side man silas with old statements, right side woman rosa with a fresh checklist, both at home"),
        ("Silas trusts the system and never checks fees, allocations, or interest rates because everything still seems to work.",
         "man silas on a couch ignoring a stack of statements, comic banner reads NEVER CHECK, dust on the papers"),
        ("Rosa books one Saturday morning every June and reviews fees, beneficiaries, allocations, and interest rates on every account.",
         "woman rosa at a kitchen table with a checklist reading FEES BENEFICIARIES ALLOCATIONS RATES, a calendar marked JUNE PHYSICAL"),
        ("Silas's checkup reveals he is paying one point three percent in 401k fees and his savings is at zero point zero one percent. He has lost twenty thousand dollars in growth.",
         "shocked man silas at a kitchen table looking at fee disclosures, comic banner reads TWENTY THOUSAND LOST"),
        ("Rosa rebalanced her 401k, switched to a high yield savings account, and updated outdated beneficiaries. She gained an extra fifteen thousand over five years.",
         "split scene, left side silas with old papers, right side rosa with an updated brokerage app reading FIFTEEN THOUSAND MORE"),
        ("Schedule one Saturday a year as your money physical. Five hours can fix a decade of financial drift. See you next visit. Stay financially healthy!",
         "doctor dollar holding a clipboard labeled YEARLY MONEY DAY, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))

SCRIPTS.append((
    "doctor_dollar", ("Miles", "Ada"),
    "hsa-maxed", "HSA maxed vs ignored",
    [
        ("A maxed health savings account can grow into one hundred fifty thousand dollars of triple tax free retirement money. I am Doctor Dollar. Today's patient checkup starts here.",
         "doctor dollar holding a clipboard labeled HSA TRIPLE TAX FREE, comic burst banner reads ONE HUNDRED FIFTY THOUSAND"),
        ("Miles and Ada both have a high deductible health plan at work and both qualify to contribute to a health savings account.",
         "split panel, left side man miles with a benefits sheet labeled HSA ELIGIBLE, right side woman ada with the same sheet, both at the doctor's desk"),
        ("Miles never opened the HSA. He thinks of it as just a medical bill account and never knew it could be invested in index funds.",
         "man miles on a couch with a benefits booklet unopened, comic banner reads NEVER OPENED IT, a closed HSA icon"),
        ("Ada contributes the full four thousand dollar yearly maximum, pays small medical bills out of pocket, and invests the HSA in a low cost index fund.",
         "woman ada at a laptop tapping AUTO INVEST FOUR THOUSAND in an HSA, a low cost fund chart on the screen"),
        ("After twenty years Miles has zero dollars in an HSA and has paid over thirty thousand dollars in medical bills out of taxed checking.",
         "shocked man miles staring at a kitchen table with old medical bills, comic banner reads ZERO HSA"),
        ("Ada's HSA holds one hundred forty thousand dollars in tax free retirement money and a folder of every medical receipt she can reimburse herself for any time.",
         "split scene, left side miles with empty hands, right side ada with a brokerage app reading ONE HUNDRED FORTY THOUSAND HSA"),
        ("If you qualify for an HSA, max it and invest it. Pay small medical bills with cash. The triple tax free win is the strongest in the IRS code. See you next visit. Stay financially healthy!",
         "doctor dollar holding a clipboard labeled MAX AND INVEST, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))

SCRIPTS.append((
    "doctor_dollar", ("Theo", "Selma"),
    "index-vs-whole-life", "Index funds vs whole life insurance",
    [
        ("Whole life insurance disguised as investing can cost you four hundred thousand dollars over a lifetime. I am Doctor Dollar. Today's patient checkup starts here.",
         "doctor dollar holding a clipboard with two charts, one labeled INDEX FUND and one labeled WHOLE LIFE, comic burst banner reads FOUR HUNDRED THOUSAND DIFFERENCE"),
        ("Theo and Selma each can afford five hundred dollars a month for long term wealth building and both meet with financial product salespeople.",
         "split panel, left side man theo at a desk with a glossy whole life brochure, right side woman selma at the desk with a low cost index fund printout"),
        ("Theo signs up for a five hundred dollar a month whole life policy after a polished agent calls it a guaranteed safe investment.",
         "man theo at a kitchen table signing a glossy WHOLE LIFE POLICY contract, an agent in a suit smiling beside him"),
        ("Selma buys a thirty dollar a month term life policy and invests the remaining four hundred seventy dollars a month into a low cost index fund.",
         "woman selma at a kitchen table with a small term life paper and a brokerage app set to AUTO INVEST FOUR SEVENTY"),
        ("After thirty years Theo's whole life policy has built a cash value of seventy thousand dollars after paying in one hundred eighty thousand.",
         "shocked older man theo holding a policy statement reading CASH VALUE SEVENTY THOUSAND, comic banner reads ONE EIGHTY PAID IN"),
        ("Selma has the same life coverage and her index fund is worth six hundred and ten thousand dollars. Same monthly cost, very different result.",
         "split scene, left side theo with a thin policy, right side older woman selma with a brokerage app reading SIX HUNDRED TEN THOUSAND"),
        ("Buy term life insurance and invest the rest in low cost index funds. Insurance and investing are two different jobs. See you next visit. Stay financially healthy!",
         "doctor dollar holding a clipboard labeled BUY TERM INVEST THE REST, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))

SCRIPTS.append((
    "doctor_dollar", ("Felix", "Dora"),
    "dca-vs-market-timing", "Dollar cost averaging vs market timing",
    [
        ("Trying to time the market loses to dollar cost averaging eighty percent of the time. I am Doctor Dollar. Today's patient checkup starts here.",
         "doctor dollar holding a clipboard with two stock charts, one calm labeled DCA and one jagged labeled TIMING, comic burst banner reads EIGHTY PERCENT WIN RATE"),
        ("Felix and Dora each have one thousand dollars a month they can invest into the same total market index fund for the next ten years.",
         "split panel, left side man felix at a laptop with stock charts, right side woman dora at a laptop with a steady auto invest icon"),
        ("Felix tries to time every dip, sells every spike, and lets cash sit on the sidelines waiting for the perfect moment.",
         "man felix at a desk with multiple stock charts, comic banner reads WAITING FOR THE BOTTOM, cash piling on the sidelines"),
        ("Dora sets a fixed one thousand dollar auto invest on the first of every month and never looks at a single chart in between.",
         "woman dora at a phone screen tapping AUTO INVEST FIRST OF MONTH, a small chart slowly trending up in the background"),
        ("Ten years later Felix missed three of the best market days while waiting for crashes. His portfolio is worth one hundred twenty thousand dollars.",
         "shocked man felix at a desk with a chart showing missed peaks, comic banner reads ONE HUNDRED TWENTY THOUSAND"),
        ("Dora's automated investing turned the same one hundred twenty thousand dollars contributed into one hundred ninety five thousand dollars.",
         "split scene, left side felix with a smaller balance, right side dora with a brokerage app reading ONE NINETY FIVE THOUSAND"),
        ("Set automatic monthly investments and ignore the headlines. Time in the market beats timing the market. See you next visit. Stay financially healthy!",
         "doctor dollar holding a clipboard labeled AUTO INVEST MONTHLY, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))

SCRIPTS.append((
    "doctor_dollar", ("Oscar", "Petra"),
    "minimum-vs-full-balance", "Paying minimum vs full credit card balance",
    [
        ("Paying only the minimum on a five thousand dollar card stretches the bill out to twenty seven years. I am Doctor Dollar. Today's patient checkup starts here.",
         "doctor dollar holding a clipboard with a credit card statement marked MINIMUM PAYMENT, comic burst banner reads TWENTY SEVEN YEARS"),
        ("Oscar and Petra each charged five thousand dollars on a credit card with twenty four percent interest after a home repair.",
         "split panel, left side man oscar with a card statement reading FIVE THOUSAND, right side woman petra with the same statement, both at home"),
        ("Oscar pays only the minimum payment of one hundred dollars each month, telling himself it is fine because it does not feel painful.",
         "man oscar on a couch swiping a card while a statement reading MINIMUM ONE HUNDRED appears, comic banner reads PAINLESS"),
        ("Petra cuts her grocery and entertainment spending and pays the full five thousand dollar balance off in eight months.",
         "woman petra at a kitchen table writing aggressive payments labeled FIVE HUNDRED A MONTH, a small grocery list cut down"),
        ("Twenty seven years later Oscar will have paid the bank over fifteen thousand dollars in interest on his original five thousand dollar charge.",
         "shocked older man oscar at a kitchen table holding a final statement, comic banner reads FIFTEEN THOUSAND IN INTEREST"),
        ("Petra paid less than four hundred dollars in total interest and had a clean card eight months later. Same charge, very different prognosis.",
         "split scene, left side oscar with a long timeline of payments, right side petra with a clean card statement and a smile"),
        ("Always pay the full statement balance on credit cards. Minimum payments are how the bank gets rich. See you next visit. Stay financially healthy!",
         "doctor dollar holding a clipboard labeled PAY IN FULL, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))

SCRIPTS.append((
    "doctor_dollar", ("Adam", "Mira"),
    "refinance-high-rate-debt", "Refinancing high-rate debt vs ignoring it",
    [
        ("Refinancing a fifteen thousand dollar credit card debt can save you five thousand dollars in interest. I am Doctor Dollar. Today's patient checkup starts here.",
         "doctor dollar holding a clipboard labeled REFINANCE, comic burst banner reads FIVE THOUSAND IN SAVED INTEREST"),
        ("Adam and Mira each carry fifteen thousand dollars in credit card debt at twenty four percent and each have a credit score above seven hundred.",
         "split panel, left side man adam with three credit card statements, right side woman mira with the same three statements, both at desks"),
        ("Adam keeps paying the high rate cards because he is too busy to research a personal loan or balance transfer offer.",
         "man adam on a couch tossing a stack of card statements aside, comic banner reads TOO BUSY"),
        ("Mira applies for a credit union personal loan at nine percent, pays off all three credit cards in one shot, and now has a single fixed monthly payment.",
         "woman mira at a kitchen table with a credit union loan paper labeled NINE PERCENT, three card statements stamped PAID OFF"),
        ("Three years later Adam has paid eight thousand dollars in interest on the same fifteen thousand and still owes ten thousand on the cards.",
         "shocked man adam at a kitchen table with a card statement reading TEN THOUSAND OWED, comic banner reads EIGHT THOUSAND IN INTEREST"),
        ("Mira paid off the entire fifteen thousand in three years and only paid three thousand dollars in interest. The refinance saved her five thousand dollars.",
         "split scene, left side adam still in card debt, right side mira with a clean balance sheet and a savings app reading FIVE THOUSAND SAVED"),
        ("If your credit score is above seven hundred, refinance any debt over ten percent. The phone call that lowers your rate is the cheapest visit you will ever make. See you next visit. Stay financially healthy!",
         "doctor dollar holding a clipboard labeled CALL THE CREDIT UNION, comic burst banner reads SEE YOU NEXT VISIT"),
    ],
))


# ============================================================
# RUNNER
# ============================================================


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    written = 0
    skipped = 0
    for character, names, topic_slug, topic_title, scenes in SCRIPTS:
        script = build(character, names, topic_slug, topic_title, scenes)
        path = OUT / f"{script['video_id']}.json"
        if path.exists():
            print(f"skip (exists): {path.name}")
            skipped += 1
            continue
        path.write_text(json.dumps(script, indent=2))
        print(f"wrote: {path.name}")
        written += 1
    print(f"\nDone. Wrote {written}, skipped {skipped}, total in scripts/: "
          f"{len(list(OUT.glob('*.json')))}")


if __name__ == "__main__":
    main()
