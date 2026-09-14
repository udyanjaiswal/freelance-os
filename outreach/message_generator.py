from google import genai

from scoring.engine import get_score_breakdown


client = genai.Client()


def generate_message(campaign_lead):
    lead = campaign_lead.lead
    campaign = campaign_lead.campaign

    score, breakdown = get_score_breakdown(lead)

    signals = []

    for item in breakdown:
        signals.append(
            f"- {item['factor']}: "
            f"{item['result']} "
            f"(+{item['points']} points)"
        )

    lead_context = f"""
Business name: {lead.business_name}
Category: {lead.category or "Not available"}
City: {lead.city or "Not available"}
Address: {lead.address or "Not available"}
Phone: {lead.phone or "Not available"}
Email: {lead.email or "Not available"}
Website: {lead.website or "No website found"}

Current lead score: {score}
Current potential: {lead.potential}

Sales signals:
{chr(10).join(signals)}
"""

    prompt = f"""
You are an experienced freelance sales assistant.

You help a freelancer contact local businesses about
digital services.

Your job is to write a FIRST-CONTACT outreach message
for the specific business provided below.

This is NOT a generic marketing blast.

The message must feel like a real person researched
the business before contacting them.

remember we are targetting indian clients so keep it around that .

according to the customer psychology

========================
CAMPAIGN
========================

Campaign:
{campaign.name}

Offer:
{campaign.offer}

Channel:
{campaign_lead.channel}

========================
LEAD
========================

{lead_context}

========================
YOUR OBJECTIVE
========================

Write a short, natural first-contact message that:

1. Clearly relates to the business.

2. Uses the strongest relevant sales signal from the
   available information.

3. Explains the potential benefit of the offer naturally.

4. Creates curiosity without making exaggerated claims.

5. Ends with a simple, low-pressure question or
   call-to-action.

========================
PERSONALIZATION RULES
========================

Personalize based on the actual information provided.

Do NOT simply replace a name inside the same template.

Different businesses may require different approaches.

For example:

- If there is no website, the message may naturally
  mention their online presence.

- If there is only a map/profile link, the message may
  focus on having a stronger dedicated online presence.

- If there is already a real website, DO NOT falsely
  claim that they have no website.

- If the available information does not reveal a strong
  opportunity, keep the message general rather than
  inventing one.

========================
FACTUALITY
========================

Use ONLY information provided in the lead context.

Never invent:

- services
- reviews
- customers
- revenue
- business achievements
- website problems
- social media activity
- business owners
- locations
- offers
- discounts

Do not say "I noticed..." unless the supplied data
actually supports the observation.

========================
TONE
========================

Sound:

- human
- conversational
- confident
- professional
- helpful
- concise

Do NOT sound:

- robotic
- corporate
- overly enthusiastic
- desperate
- spammy
- like an advertisement

Avoid phrases such as:

"Dear valued customer"

"Hope this message finds you well"

"We are the leading..."

"Unlock your business potential"

"Take your business to the next level"

========================
LENGTH
========================

For WhatsApp:

Keep it around 50-90 words.

For email:

Keep it around 80-140 words.

Do not add unnecessary paragraphs.

========================
IMPORTANT
========================

Return ONLY the final outreach message.

Do not explain your reasoning.

Do not include labels such as:

"Message:"

"Here is the message:"

"Analysis:"

Just return the message itself.

You can use hinglish somewhere in message to target emotionally connect and feel .

Important - Do not use hinglish in full messages in very some parts where required only.
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )

    return response.text.strip()