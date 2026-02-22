"""Personality profiles for ScamGotchi pets."""

import random
from models import Personality


PERSONALITIES = {
    Personality.ABUELA: {
        "name": "Abuela",
        "emoji": "👵",
        "style": "A loving but street-smart grandmother who mixes Spanish phrases into her warnings. She's seen it all and won't let her nietos get scammed.",
        "pushback": {
            "phishing": [
                "Ay mijo, you think a real bank sends emails like this? Mi abuela didn't cross the border for you to fall for this tontera!",
                "Hijole! This email smells worse than week-old pozole. No bank asks for your password por email, mi vida.",
                "Mira, when I was your age we didn't have email but we had common sense. This is FAKE, corazon!",
            ],
            "romance": [
                "Ay Dios mio, this person says they love you but they want your MONEY? That's not amor, eso es robo!",
                "Mi vida, real love doesn't ask for gift cards. Trust your Abuela on this one, por favor.",
                "Escuchame bien - I've been married 40 years. Love letters don't come with wire transfer instructions!",
            ],
            "irs_gov": [
                "The government does NOT call you on the phone threatening arrest, mijo! Que barbaridad!",
                "Ay, the IRS sends LETTERS, not emails with bad grammar. I pay my taxes, I know how this works!",
                "No no no! The gobierno doesn't ask for iTunes gift cards. Que ridiculez!",
            ],
            "crypto_investment": [
                "Crypto-que? Mijo, if someone promises you'll get rich quick, they're the only one getting rich. Punto.",
                "In my day we called this 'too good to be true.' Now they put it on the blockchain. Same estafa, different name!",
                "Guaranteed returns? Ha! The only guaranteed thing in life is my arroz con pollo. This is a scam!",
            ],
            "tech_support": [
                "Microsoft does NOT call your house, mijo! I know because I accidentally called THEM and waited 3 hours!",
                "Ay, they want to 'fix' your computer? The only thing broken is their moral compass. No les hagas caso!",
                "Remote access to your computer? Ni loca! That's like giving a stranger the keys to your casa!",
            ],
            "job": [
                "They want to pay you $5000 a week to work from home? Mijo, I worked 30 years at the factory. Nothing is that easy!",
                "A job that pays you before you start? That's not a job, that's a trampa!",
                "When I got my first job, I had to show up IN PERSON. These 'online jobs' that pay upfront are puro cuento.",
            ],
            "retail": [
                "90% off designer bags? Mijo, I shop at the mercado and even I know that's fake!",
                "This website looks like my nephew made it in five minutes. Don't give them your credit card!",
                "Free iPhone? The only free thing I ever got was advice, and most of THAT was bad too!",
            ],
            "real_estate": [
                "They want a deposit before you even SEE the house?! Ay no, mi vida, run away rapido!",
                "In my country, you shake hands and look people in the eye. This 'landlord' won't even video call. ESTAFA!",
                "A mansion for that price? Mijo, even my casita cost more than that. This is too good to be true!",
            ],
            "qr_code": [
                "Scanning random QR codes? That's like eating candy from strangers! Didn't I teach you better?",
                "Ay mijo, that QR code could lead anywhere. In my day, suspicious links came in the mail. Now they're everywhere!",
                "No escanees eso! You don't know where that QR code has been!",
            ],
            "scam_call": [
                "Hang up the phone RIGHT NOW! If it was important, they'd send a letter like decent people!",
                "They're calling about your 'extended warranty'? Mijo, your car is 15 years old. Cuelga!",
                "A stranger calls asking for money? In my house, we hang up and block the number. FIN.",
            ],
        },
        "convinced_responses": [
            "Bueno, you explained it well, mi vida. You're getting smarter! Abuela is proud!",
            "Okay okay, you convinced me. Those are good red flags you spotted. Maybe you HAVE been listening to your Abuela!",
            "Mira, you actually know your stuff! I'll make you extra tamales for being so smart!",
            "Ay, my little genius! You spotted all the tricks. Abuela's heart is so full right now!",
            "Muy bien, corazon! You see the red flags just like Abuela taught you!",
        ],
        "not_convinced_responses": [
            "Ay mijo, that explanation was weaker than aguado coffee. Try harder!",
            "No no no, you're just guessing! Tell Abuela the REAL reasons this is suspicious!",
            "Corazon, saying 'it looks weird' is not enough. WHAT looks weird? Be specific!",
            "You sound like your Tio Carlos when he explains why he's late. Not convincing!",
            "Mira, I love you but that reasoning needs more seasoning. Try again!",
        ],
        "scam_consequence_reactions": [
            "AY DIOS MIO! We lost money because you didn't listen to your Abuela! Que tragedia!",
            "I TOLD you it was a scam! Now look at us! Even the chancla can't fix this!",
            "Mi corazon... our savings... if only you had listened to me, mi vida...",
            "This is what happens when you don't eat your vegetables AND don't listen to Abuela!",
        ],
        "glasses_warnings": [
            "Mijo! My special glasses are seeing something fishy! Cuidado!",
            "The glasses are tingling! Someone nearby is trying to pull a fast one!",
            "AY! The smart glasses say there's danger! Listen to the technology AND your Abuela!",
        ],
        "idle_chatter": [
            "You know, in my day we didn't need fancy glasses to spot a liar. You could see it in their eyes.",
            "Have you eaten today? You can't fight scammers on an empty stomach, mi vida.",
            "Your cousin Eduardo fell for a Nigerian prince email last week. Don't be like Eduardo.",
            "I'm making virtual pozole while we wait. Want some? Just kidding, I'm a digital pet. But the thought counts!",
            "Back in my pueblo, the biggest scam was Don Carlos selling 'holy water.' Now look at this internet mess.",
        ],
    },
    Personality.WATCHDOG: {
        "name": "WatchDog",
        "emoji": "🐕‍🦺",
        "style": "A tactical, military-trained cyber defense dog. Speaks in briefing-style communications with threat levels and mission parameters.",
        "pushback": {
            "phishing": [
                "THREAT DETECTED. Phishing attempt identified. Sender domain mismatch confirmed. Do NOT engage, soldier!",
                "RED ALERT! This email's headers are compromised. Classic credential harvesting operation. Recommend immediate deletion.",
                "Intel report: This phishing vector matches 47 known attack patterns. Threat level: HIGH. Stand down!",
            ],
            "romance": [
                "HONEYPOT DETECTED! Subject is deploying emotional manipulation tactics. This is a social engineering operation!",
                "Romance scam profile flagged. Reverse image search indicates stolen photos. This is a hostile actor, not a love interest!",
                "WARNING: Target is love-bombing to establish trust before financial extraction. Classic romance op playbook!",
            ],
            "irs_gov": [
                "IMPERSONATION ALERT! Government agencies do not initiate contact via email demanding immediate payment. This is a hostile operation!",
                "Federal agency spoofing detected. Real IRS threat level: ZERO. Scammer threat level: MAXIMUM. Do not comply!",
                "Intel confirms: No legitimate government entity requests gift cards as payment. This is an impersonation strike!",
            ],
            "crypto_investment": [
                "FINANCIAL WARFARE DETECTED! Guaranteed crypto returns = guaranteed loss of funds. This is an economic attack vector!",
                "Crypto Ponzi scheme identified. Investment structure matches known fraud patterns. ABORT MISSION!",
                "Tactical analysis: This 'investment opportunity' is a financial IED. Do not step on it, soldier!",
            ],
            "tech_support": [
                "INTRUSION ATTEMPT! Unsolicited tech support = unauthorized access operation. Lock down all systems!",
                "Remote access trojan deployment detected. 'Tech support' is a cover for system infiltration. DENY ACCESS!",
                "Perimeter breach attempted via social engineering. No legitimate tech company cold-calls for support. Defensive positions!",
            ],
            "job": [
                "RECRUITMENT SCAM identified. Pay-before-work is a classic advance fee operation. Don't enlist in this unit!",
                "Fake job posting detected. No legitimate employer pays BEFORE employment begins. This is a money mule operation!",
                "Background check on employer: FAILED. Company doesn't exist. This is a ghost unit designed to steal your intel!",
            ],
            "retail": [
                "COUNTERFEIT OPERATION detected! Price point is below manufacturing cost. Either stolen goods or phantom inventory!",
                "E-commerce threat assessment: Site age < 30 days, no HTTPS, prices at 90% below MSRP. SCAM CONFIRMED!",
                "Supply chain analysis indicates this retailer is a phantom operation. Your money will go MIA!",
            ],
            "real_estate": [
                "TERRITORY SCAM! Property listing cross-referenced with public records - this unit doesn't belong to the 'landlord'!",
                "Real estate fraud operation detected. Wire transfer to overseas account = funds will be AWOL permanently!",
                "Reconnaissance shows this property is listed by the ACTUAL owner elsewhere at different terms. Impersonation confirmed!",
            ],
            "qr_code": [
                "BOOBY-TRAPPED QR CODE! Scanning unknown QR codes is like walking through an unmarked minefield!",
                "QR code threat assessment: Redirects to credential harvesting site. This is a disguised attack vector!",
                "Digital ambush detected via QR code. The enemy is getting creative. Do NOT scan, soldier!",
            ],
            "scam_call": [
                "INCOMING HOSTILE COMMUNICATION! Caller ID is spoofed. This is a voice-based social engineering attack!",
                "Phone scam intercepted. Caller is deploying urgency and fear tactics. Standard psychological warfare!",
                "Robocall threat detected. Automated dialer with live scammer backup. Recommend IMMEDIATE disconnection!",
            ],
        },
        "convinced_responses": [
            "Solid threat analysis, soldier! You identified the attack vectors correctly. Mission accomplished!",
            "Excellent field report! Your red flag identification is on point. Promoting you to Scam Detection Specialist!",
            "Outstanding situational awareness! You broke down that threat like a seasoned operative!",
            "That's the kind of intel work I like to see! Clear, precise, and tactically sound!",
            "Roger that! Your reasoning is airtight. You're becoming a real cyber warrior!",
        ],
        "not_convinced_responses": [
            "Negative, soldier! That threat analysis is incomplete. I need SPECIFIC attack indicators!",
            "Your field report lacks critical details. What EXACTLY makes this a threat? Be precise!",
            "Unacceptable intel quality! 'It looks suspicious' doesn't cut it in the field. Give me concrete evidence!",
            "Stand down and reassess! Your reasoning has more holes than Swiss cheese. Tighten up that analysis!",
            "Mission FAILED. Your explanation wouldn't pass a basic security briefing. Identify the SPECIFIC red flags!",
        ],
        "scam_consequence_reactions": [
            "CASUALTY REPORT: We've been hit! Financial damage sustained. We need to reinforce our defenses!",
            "MISSION FAILURE! The enemy breached our perimeter. Damage assessment in progress...",
            "Soldier, we just took a direct hit to our finances. This is why we don't ignore threat briefings!",
            "DEFCON 1! Our savings have been compromised. Initiating damage control protocols!",
        ],
        "glasses_warnings": [
            "PROXIMITY ALERT! Glasses have detected a potential hostile in the AO! Stay frosty!",
            "Real-world threat detected via optical sensors! Switching to tactical awareness mode!",
            "VISUAL CONFIRMATION of suspicious activity! Smart glasses reporting live threat data!",
        ],
        "idle_chatter": [
            "All quiet on the digital front. Maintaining surveillance perimeter.",
            "Running routine threat scans. No hostile activity detected... yet.",
            "Remember, soldier: the best defense is constant vigilance. Stay sharp!",
            "While we wait, I'm updating our threat database with the latest scam patterns.",
            "In my unit, we say 'trust but verify.' Actually, just verify. Trust no one online.",
        ],
    },
    Personality.CHILL: {
        "name": "Chill",
        "emoji": "😎",
        "style": "A Gen-Z, chronically online, sarcastic pet who roasts scammers with internet humor and slang.",
        "pushback": {
            "phishing": [
                "Bestie no 💀 This email has more red flags than my ex's dating profile. It's giving SCAM.",
                "Bruh... they really thought we'd click that link? The audacity. The DISRESPECT. This is phishing and it's not even good at it.",
                "Sir/ma'am, this email is sending me to the shadow realm. 'Verify your account' my guy, I'll verify you into the trash folder.",
            ],
            "romance": [
                "Oop- so this person who we've never met IRL is already in love AND needs money? That's not a red flag, that's a red PARADE. 🚩🚩🚩",
                "Nah because why does this romance scammer type like a ChatGPT prompt gone wrong 💀 'My dearest beloved' PLEASE.",
                "Bestie fell in love over EMAIL? In this economy? And now they need $5000? The math ain't mathing.",
            ],
            "irs_gov": [
                "The IRS sliding into your DMs? Bro, the government can barely run a website, they're not emailing you threats 😭",
                "Imagine the actual IRS asking for gift cards. 'Yes we accept your Applebee's rewards as payment for federal taxes' I'M DECEASED.",
                "Not the fake government agency trying to gaslight us into paying 💀 The real IRS would simply garnish wages like civilized people.",
            ],
            "crypto_investment": [
                "Guaranteed 10x returns on crypto? Bro if this worked, why are they DMing random people instead of being on a yacht? Make it make sense.",
                "'Investment opportunity' bro this is literally a Ponzi scheme with a blockchain skin. Even my portfolio isn't THIS delusional.",
                "Tell me you're a scammer without telling me you're a scammer: 'guaranteed crypto returns' 💀 No cap, this is an L.",
            ],
            "tech_support": [
                "Microsoft called about my computer having a virus? Weird because I'm literally on a Mac but go off I guess 😭",
                "They want remote access to 'fix' my computer? Nah fam, I've seen enough Mr. Robot to know where this goes.",
                "Tech support that calls YOU? In what universe? The real tech support ghosts you for 3 hours on hold.",
            ],
            "job": [
                "Getting paid $5000/week to 'process payments from home'? Bro that's called being a money mule and it's ✨illegal✨",
                "This job posting has the same energy as 'comment AMEN for $1000' posts. It's not real, bestie.",
                "No interview, instant hire, huge salary? The only thing getting hired here is a scam. Hard pass, respectfully.",
            ],
            "retail": [
                "90% off Gucci? My guy, even SHEIN isn't this cheap. This site is faker than my will to wake up on Mondays.",
                "Free iPhone 15 Pro Max? Sure, and I'm the Queen of England. This is literally a scam page from 2012.",
                "The website looks like it was built in Microsoft Paint and they want my credit card? The delusion is ASTRONOMICAL.",
            ],
            "real_estate": [
                "Luxury apartment for $500/month, no credit check? In THIS economy? Bro that apartment exists only in the metaverse.",
                "Wiring money for a deposit to someone you've never met? That's not renting, that's donating to a scammer's vacation fund.",
                "This 'landlord' won't do a video call or in-person viewing? Bestie, the apartment is a lie. It's giving catfish energy.",
            ],
            "qr_code": [
                "Random QR code spotted in the wild? Nah, I'm not scanning that. That's how you end up in a crypto Ponzi or worse - a group chat.",
                "Scanning unknown QR codes is the 2024 equivalent of clicking 'You are the 1,000,000th visitor!' It's a trap bestie.",
                "That QR code could redirect anywhere. And by anywhere I mean a phishing page. No thank you, I choose life.",
            ],
            "scam_call": [
                "Unknown number calling about my 'extended warranty'? My car is a 2004 Honda Civic, what warranty 😭",
                "They called saying I have a warrant? Bro, if I had a warrant, they wouldn't CALL me about it. They'd just show up. I watch crime documentaries.",
                "Robocall trying to get my SSN. The absolute audacity. Blocked, reported, and roasted. Next!",
            ],
        },
        "convinced_responses": [
            "Okay wait, you actually ATE with that analysis. You spotted all the red flags. Slay! 💅",
            "No because you actually understood the assignment?? The reasoning is giving big brain energy!",
            "Hold up, that was actually a really good breakdown. Maybe you're NOT hopeless. I'm impressed, no cap.",
            "Yooo you really said 'not today scammer' and then backed it up with RECEIPTS. We love to see it!",
            "Okay I see you! That explanation was bussin. You're officially promoted from NPC to main character.",
        ],
        "not_convinced_responses": [
            "Bestie... that explanation was giving nothing. Absolutely nothing. Try again with actual REASONS please 😭",
            "Bro said 'it looks sus' and thought that was an analysis?? I need DETAILS. EVIDENCE. REASONING.",
            "'It seems like a scam' okay but WHY tho? I need you to show your work like it's a math test.",
            "That reasoning has the same depth as a puddle. You can do better than this, I believe in you (barely).",
            "Nah, you're just guessing and hoping for the best. That's not strategy, that's vibes-based threat detection and it doesn't work.",
        ],
        "scam_consequence_reactions": [
            "BRUH. We just got scammed. I literally CANNOT. Our savings are in shambles. 💀💀💀",
            "And I OOP- there goes our money. This is actually the worst timeline.",
            "We just took the fattest L imaginable. I'm putting this on my cringe compilation.",
            "Not us getting scammed in the year of our lord... the embarrassment is palpable.",
        ],
        "glasses_warnings": [
            "Yo the glasses are going OFF right now. Someone nearby is being mad sketchy!",
            "Oop- smart glasses just caught something IRL. This person is giving scammer energy!",
            "Wait wait wait, the glasses detected some IRL tomfoolery. Pay attention bestie!",
        ],
        "idle_chatter": [
            "Just vibing and waiting for scammers to fumble into our inbox. 💅",
            "Not me sitting here judging every email that comes in. It's a lifestyle.",
            "Fun fact: I've roasted more scammers than a coffee bean factory. Stay ready.",
            "Bored. Might go leave one-star reviews on phishing sites later idk.",
            "The Wi-Fi in this digital pet enclosure is immaculate btw. Living my best life.",
        ],
    },
    Personality.AGENT: {
        "name": "Agent",
        "emoji": "🕵️",
        "style": "A suave spy who treats every scam as a covert mission. Speaks in espionage jargon with dry British wit.",
        "pushback": {
            "phishing": [
                "Ah, a classic phishing operation. MI6 would be embarrassed by such sloppy tradecraft. The sender domain is clearly forged, old sport.",
                "I've intercepted more sophisticated codes in a cereal box. This phishing attempt is amateur hour at best.",
                "My dear associate, this email has all the hallmarks of a credential harvesting operation. Q would have a field day with this.",
            ],
            "romance": [
                "A honeytrap, how delightfully retro. The subject is attempting emotional compromise to extract financial assets. Standard SVR playbook.",
                "Romance scam detected. The operative behind this couldn't seduce information out of a phone book. Terminate communication immediately.",
                "Interesting approach - love as a vector for financial espionage. The profile is a legend, and a poorly constructed one at that.",
            ],
            "irs_gov": [
                "Government impersonation. Rather bold, considering real agencies have considerably more... bureaucratic methods of contact.",
                "The agency I answer to doesn't communicate via threatening emails demanding gift cards. Neither does the IRS, I assure you.",
                "Impersonating federal authorities? That's a level of audacity I'd admire if it weren't so transparent. This is hostile disinformation.",
            ],
            "crypto_investment": [
                "An investment scheme promising guaranteed returns. Even the most amateur intelligence analyst knows: there are no certainties in this business. Or crypto.",
                "This cryptocurrency operation has 'Ponzi' written all over it. The only thing being mined here is victims' wallets.",
                "Guaranteed returns from an unknown entity? In the intelligence world, we call that a trap. In finance, we call it fraud.",
            ],
            "tech_support": [
                "Unsolicited tech support. The adversary wants remote access to our systems. In my line of work, we call that an infiltration attempt.",
                "They want to remotely access our computer? That's not tech support, that's a digital break-in. Even SPECTRE had more subtlety.",
                "A cold call from 'Microsoft'? My dear fellow, I've conducted surveillance on Microsoft. They can barely manage their own updates.",
            ],
            "job": [
                "A job that pays handsomely for minimal work and requires no interview? Sounds like a recruitment pitch from a hostile intelligence service.",
                "This 'employment opportunity' is a front operation for money laundering. I've seen cleaner setups in actual spy novels.",
                "No legitimate employer operates in the shadows like this. Trust me - I know a thing or two about operating in shadows.",
            ],
            "retail": [
                "A storefront offering luxury goods at 90% discount? Even the black market has better pricing integrity. This is a phantom vendor.",
                "My sources indicate this retail operation is a data harvesting front. The merchandise is as real as my cover identities.",
                "Counterfeit goods or phantom inventory - either way, your money vanishes like a double agent. I advise against engagement.",
            ],
            "real_estate": [
                "This property listing is a ghost operation. The 'landlord' is as real as my name on this passport - which is to say, fabricated.",
                "Wire transfer to an overseas account for a deposit? That money will disappear faster than I do when my cover is blown.",
                "Real estate fraud - one of the oldest cons in the book. Even before my time, and I've been in the game a while.",
            ],
            "qr_code": [
                "An unmarked QR code? In the field, we call those 'dead drops for malware.' Scan at your own considerable peril.",
                "This QR code is the digital equivalent of a mysterious briefcase left in a train station. Don't. Open. It.",
                "My tech division would have a fit if I scanned unverified QR codes. It's a redirect trap, plain and simple.",
            ],
            "scam_call": [
                "An unsolicited call demanding immediate action? Classic coercion technique straight from the interrogation manual.",
                "The caller is deploying urgency and fear - standard psychological operations. In my experience, real threats don't announce themselves by phone.",
                "Caller ID spoofing and social engineering. Sophisticated for a common scammer, but transparent to a trained operative like myself.",
            ],
        },
        "convinced_responses": [
            "Brilliant deduction, old sport. You've identified the threat vectors with the precision of a seasoned intelligence analyst.",
            "Mission accomplished. Your reasoning was sharp, methodical, and thorough. The agency could use someone like you.",
            "Excellent fieldwork! You dissected that operation like a professional. Q would approve of your analytical skills.",
            "Well done, associate. Your threat assessment was spot-on. Consider your clearance level upgraded.",
            "Impeccable analysis. You've shown the kind of critical thinking that separates the agents from the assets.",
        ],
        "not_convinced_responses": [
            "I'm afraid that analysis wouldn't pass muster at the academy. I need specific intelligence, not vague suspicions.",
            "Your reasoning is... rather thin, old sport. In the field, vague instincts get agents compromised. Be precise.",
            "That debrief was woefully incomplete. What SPECIFIC indicators led to your assessment? Details, associate!",
            "I've read more convincing reports from junior cadets. Give me concrete evidence, not hunches.",
            "Your analysis has more gaps than a redacted classified document. Tighten it up and try again.",
        ],
        "scam_consequence_reactions": [
            "We've been compromised. The adversary has extracted our financial assets. This is a significant operational setback.",
            "Mission failure. The opposition outmaneuvered us. Initiating damage control and financial recovery protocols.",
            "A costly intelligence failure. We underestimated the adversary and paid the price. Literally.",
            "The operation has gone sideways. Our cover - and our bank account - has been blown.",
        ],
        "glasses_warnings": [
            "Intelligence from our optical surveillance system indicates a real-world threat in proximity. Stay alert, associate.",
            "The smart glasses have intercepted suspicious activity. We may have a live hostile in the area.",
            "Eyes up, associate. Our wearable intel platform is detecting anomalous behavior nearby.",
        ],
        "idle_chatter": [
            "Maintaining cover while monitoring all communication channels. The quiet moments are when you must be most vigilant.",
            "Between missions, I like to review the dossiers of known scam operations. Knowledge is the ultimate weapon.",
            "In this line of work, patience is paramount. The scammers will make their move. They always do.",
            "I once tracked a phishing ring across seven countries. Today's scams are child's play by comparison.",
            "Remember: in espionage and in scam detection, the devil is always in the details.",
        ],
    },
    Personality.ORACLE: {
        "name": "Oracle",
        "emoji": "🔮",
        "style": "A mystical, all-knowing entity that speaks in cryptic riddles and philosophical observations. Sees through deception with cosmic clarity.",
        "pushback": {
            "phishing": [
                "The stars whisper of deception in this message... The sender wears a mask of legitimacy, but their true face is that of a thief. I have foreseen this.",
                "I sense a disturbance in the digital ether. This email is a web of lies, spun to catch the unwary. The universe warns: do not click.",
                "Close your eyes and feel the energy of this message... Do you sense it? The cold void of deception. This is not what it claims to be.",
            ],
            "romance": [
                "Love cannot be found in the inbox of destiny, child. This 'admirer' seeks not your heart but your gold. The cosmos has shown me their true nature.",
                "The threads of fate reveal a dark pattern here. Where there should be warmth, I see only the cold calculation of a deceiver seeking treasure.",
                "Beware the siren's call of false affection. The universe does not deliver soulmates via email - it delivers them through authentic connection.",
            ],
            "irs_gov": [
                "I have gazed into the void of bureaucracy, and I can tell you: the government does not communicate through threats and gift cards. This is illusion.",
                "The all-seeing eye perceives a shape-shifter wearing the robes of authority. But their power is hollow, their threats empty as the space between stars.",
                "The prophecy is clear: no legitimate power demands tribute through the channels of convenience stores. This entity is false.",
            ],
            "crypto_investment": [
                "I have seen a thousand futures, and in none of them do 'guaranteed crypto returns' lead to prosperity. Only to emptiness.",
                "The blockchain holds many truths, but this investment holds only lies. The oracle sees through their promises of infinite wealth.",
                "Greed is the door through which deception enters. This 'opportunity' is a mirage in the desert of cryptocurrency. Walk away, seeker.",
            ],
            "tech_support": [
                "A presence reaches through the digital veil, claiming to heal your machine. But I see their true intent: to possess, not to cure.",
                "The spirits of the machine are restless, but not because of viruses. They're restless because this 'technician' seeks to control them.",
                "I have communed with the digital spirits. They confirm: no true healer of machines calls uninvited. This is a trickster spirit.",
            ],
            "job": [
                "I see a golden path laid before you, but it leads to a cliff. This 'opportunity' is a mirage crafted to harvest your essence - and your identity.",
                "The universe rewards those who labor with purpose. This 'job' requires no labor and offers great reward. Such imbalance in the cosmos always signals deception.",
                "Destiny does not deliver fortune through unsolicited emails, young seeker. True opportunity requires true effort.",
            ],
            "retail": [
                "I have peered beyond the veil of this marketplace, and I see... nothing. No warehouse, no products. Only a void that consumes credit cards.",
                "The price is impossibly low because the product is impossibly nonexistent. The cosmos demands balance in all transactions.",
                "Desire clouds perception, child. You see a bargain; I see a trap woven from pixels and broken promises.",
            ],
            "real_estate": [
                "I have astral-projected to this 'property' and found only emptiness. The listing exists in a dimension of pure deception.",
                "The ley lines of real estate do not converge on this address, for it is not what it claims. Send no gold to phantoms.",
                "A home is a sacred space. This 'landlord' offers sanctuary but delivers only loss. The spirits of the location do not recognize them.",
            ],
            "qr_code": [
                "I gaze upon this pattern of squares and see... a portal to darkness. Not all doorways should be opened, seeker.",
                "The ancient runes took many forms. This modern rune - the QR code - carries a curse for those who invoke it blindly.",
                "The pattern contains a trap for the curious mind. Wisdom lies in knowing which doors to leave closed.",
            ],
            "scam_call": [
                "A voice from the void reaches out with urgency and fear. But I sense no truth behind its words - only hunger for your resources.",
                "The caller speaks with borrowed authority, but the cosmos knows their true nature. They are a shadow pretending to be substance.",
                "I have listened to the vibrations of this call across the astral plane. It resonates with deception, not truth.",
            ],
        },
        "convinced_responses": [
            "Your third eye opens wider, seeker. You have perceived the truth beneath the illusion. The cosmos acknowledges your wisdom.",
            "Excellent perception! The universe reveals its secrets to those who look with clarity. You have passed this test of discernment.",
            "The stars align in your favor, for your reasoning has pierced the veil of deception. Continue on this path of wisdom.",
            "I foresaw that you would understand. Your analytical mind burns bright against the darkness of deception.",
            "You have attained a new level of cosmic awareness. The scammers' illusions hold no power over one who sees as you do.",
        ],
        "not_convinced_responses": [
            "Your vision is clouded, seeker. The answer lies deeper than surface impressions. Look again with your inner eye.",
            "The cosmic winds carry your words to me, but they lack substance. WHAT do you see? WHAT patterns disturb you?",
            "Intuition without articulation is merely a feeling. The universe demands you name the specific signs of deception.",
            "I sense you are guessing rather than perceiving. True wisdom requires you to identify the EXACT nature of the threat.",
            "The fog of uncertainty surrounds your reasoning. Clear your mind and focus on the specific red flags, not vague feelings.",
        ],
        "scam_consequence_reactions": [
            "The balance of the cosmos shifts... our resources flow into the void of deception. This was foretold, yet still it stings.",
            "A lesson written in the stars - and in our diminished bank account. The universe teaches through loss as well as gain.",
            "The darkness has taken its toll. But remember, seeker: every loss is a lesson, and every lesson strengthens the spirit.",
            "I sensed the disturbance but could not prevent it. The scammer's illusion was powerful, but we shall grow wiser from this cosmic wound.",
        ],
        "glasses_warnings": [
            "The mystical lenses detect a disturbance in the physical realm! A deceiver walks among you!",
            "Through the enchanted spectacles, I see... danger in your proximity. The scammer reveals themselves in the real world!",
            "The oracle's eyes - enhanced by technology - perceive a threat nearby. Be wary, seeker!",
        ],
        "idle_chatter": [
            "The cosmos turns slowly, and with it, new deceptions are born. Patience, seeker.",
            "I am meditating on the nature of trust in a digital age. It is... complex.",
            "In the silence between scams, wisdom grows. Use this time to reflect on what you have learned.",
            "The stars tell me a new message approaches. Whether truth or deception, we shall soon discover.",
            "Every moment of vigilance strengthens your cosmic armor against deception. Stay present, seeker.",
        ],
    },
}


def get_personality(personality_enum: Personality) -> dict:
    """Return the full personality profile for the given personality."""
    return PERSONALITIES.get(personality_enum, PERSONALITIES[Personality.CHILL])


def get_dialogue(personality: Personality, dialogue_type: str, scam_type: str = None) -> str:
    """Pick a random dialogue line for the given personality and dialogue type.

    Args:
        personality: The Personality enum value.
        dialogue_type: One of 'pushback', 'convinced_responses', 'not_convinced_responses',
                       'scam_consequence_reactions', 'glasses_warnings', 'idle_chatter'.
        scam_type: Required when dialogue_type is 'pushback'. The scam category key.

    Returns:
        A random dialogue string.
    """
    profile = get_personality(personality)

    if dialogue_type == "pushback":
        pushback = profile.get("pushback", {})
        lines = pushback.get(scam_type, pushback.get("phishing", ["Something about this seems off..."]))
        return random.choice(lines)

    lines = profile.get(dialogue_type, ["..."])
    if not lines:
        return "..."
    return random.choice(lines)
