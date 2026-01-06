"""Trial template library for common legal scenarios."""
from typing import Dict, List


TRIAL_TEMPLATES: Dict[str, Dict[str, str]] = {
    "contract_breach": {
        "name": "Contract Breach",
        "category": "Contract Law",
        "description": "Breach of contract dispute",
        "case_facts": """The plaintiff, ABC Corporation, entered into a written contract with the defendant, XYZ Services, on June 1, 2025, for the provision of consulting services. The contract specified that XYZ would deliver a comprehensive market analysis report by September 1, 2025, for a fee of $50,000. The plaintiff paid $25,000 upfront as agreed.

However, XYZ failed to deliver the report by the deadline. When ABC requested an update, XYZ claimed they needed more time due to "unforeseen circumstances" but provided no specific details or revised timeline. As of October 15, 2025, no report has been delivered.

ABC claims breach of contract and seeks: (1) return of the $25,000 upfront payment, (2) $30,000 in consequential damages from lost business opportunities due to the missing analysis, and (3) attorney fees.

Defendant's potential defense: XYZ may argue that market conditions changed dramatically, making the original analysis impossible or meaningless, constituting impossibility of performance or frustration of purpose. They may also argue the contract had an implied "reasonable efforts" clause rather than a guaranteed delivery obligation."""
    },
    
    "personal_injury": {
        "name": "Personal Injury - Slip and Fall",
        "category": "Tort Law",
        "description": "Premises liability case",
        "case_facts": """The plaintiff, Jane Doe, slipped and fell at the defendant's grocery store, SafeMart, on November 10, 2025. She claims the store was negligent in maintaining safe premises. At approximately 2:00 PM, Jane entered the produce section where she slipped on what appeared to be water or liquid from melted ice, falling backward and striking her head on the floor.

Jane suffered: (1) a concussion requiring emergency room treatment, (2) a fractured wrist requiring surgery and physical therapy, and (3) ongoing back pain. Medical expenses total $45,000 to date. Jane also missed 6 weeks of work, losing $12,000 in wages. She seeks $57,000 in economic damages, $100,000 in pain and suffering, and $50,000 in future medical expenses.

Defendant's evidence: SafeMart has surveillance footage and cleaning logs. Store policy requires produce area inspection every 30 minutes. The last recorded inspection was 1:45 PM, just 15 minutes before the incident. The footage shows the spill occurred at approximately 1:55 PM when another customer dropped a bag of ice. Store staff was notified at 1:58 PM and were en route when Jane fell at 2:00 PM.

SafeMart argues: (1) the spill was too recent for them to have discovered it, (2) they had reasonable inspection procedures in place, (3) contributory negligence - Jane was looking at her phone, not watching where she walked, and (4) her injuries are exaggerated based on medical records."""
    },
    
    "employment_discrimination": {
        "name": "Employment Discrimination",
        "category": "Employment Law",
        "description": "Wrongful termination and discrimination claim",
        "case_facts": """The plaintiff, Marcus Johnson, age 58, was employed by TechStart Inc. as a senior software engineer for 12 years. On August 15, 2025, Marcus was terminated, allegedly for "performance issues." Marcus claims age discrimination and wrongful termination.

Marcus's evidence: (1) He consistently received positive performance reviews until age 55, when a new 35-year-old manager was hired. (2) His performance reviews then became increasingly critical despite his work quality remaining constant. (3) During his termination meeting, the manager allegedly said, "We need fresh perspectives from people who understand modern technology." (4) Three months before his termination, Marcus was passed over for promotion in favor of a 32-year-old with less experience. (5) Within two weeks of his termination, a 29-year-old was hired for a similar position at a lower salary.

Marcus seeks: (1) $200,000 in lost wages (estimated 2 years to find comparable employment), (2) restoration of benefits, (3) emotional distress damages of $150,000, and (4) punitive damages of $500,000.

Defendant's position: TechStart claims: (1) Marcus's termination was based solely on documented performance issues, including missed deadlines on three projects. (2) The comment about "fresh perspectives" was taken out of context and referred to new ideas, not age. (3) The promotion decision was based on the other candidate's specialized AI/ML skills. (4) The new hire has different responsibilities and wasn't a direct replacement. (5) The company has a diverse workforce with several employees over 55 in senior positions. (6) Marcus was offered a severance package which he refused."""
    },
    
    "property_dispute": {
        "name": "Property Boundary Dispute",
        "category": "Property Law",
        "description": "Neighbor dispute over property line",
        "case_facts": """The plaintiff, Sarah Miller, and defendant, Robert Chen, own adjacent residential properties. A dispute arose over the location of the property boundary line and ownership of a strip of land approximately 3 feet wide and 80 feet long between their properties.

Background: Sarah purchased her property in 2020. Robert bought his in 2023. For the past year, Sarah has maintained the disputed strip as part of her yard - mowing, planting flowers, and installing a decorative border. In October 2025, Robert hired a surveyor who claimed the strip is actually on Robert's property. Robert then erected a fence along what he claims is the true property line, cutting through Sarah's flower beds.

Sarah's claims: (1) She has a survey from 2020 showing the strip is on her property. (2) She has maintained it openly and exclusively for years, establishing adverse possession rights in some jurisdictions. (3) The previous owner of Robert's property acknowledged Sarah's use of the strip. (4) Robert's new fence is a nuisance and was built without notice. She seeks: (a) court declaration of the true boundary, (b) removal of the fence, (c) $5,000 for destroyed landscaping, and (d) attorney fees.

Robert's defense: (1) His 2025 survey used modern GPS technology and is more accurate than Sarah's 2020 survey. (2) The disputed strip is clearly on his deed. (3) One year of maintenance doesn't establish adverse possession (typically requires 10-20 years). (4) He has the right to use his own property. (5) He offered to split the disputed area, but Sarah refused to negotiate. (6) He notified Sarah by text message before building the fence."""
    },
    
    "small_business_dispute": {
        "name": "Partnership Dissolution",
        "category": "Business Law",
        "description": "Business partnership dispute",
        "case_facts": """The plaintiff, Anna Rodriguez, and defendant, Michael Lee, were equal partners in "Fusion Cafe," a restaurant they opened together in January 2024. The business was structured as a general partnership with an oral agreement to split profits and responsibilities equally.

Current dispute: The restaurant has been successful, generating approximately $400,000 in annual revenue. However, tensions arose over business decisions. Anna wants to expand to catering services, while Michael prefers maintaining focus on the restaurant. The relationship deteriorated to the point where they can no longer work together.

Anna's claims: (1) She has been managing day-to-day operations and working 60+ hours per week while Michael only works 30-40 hours. (2) Michael withdrew $15,000 more in draws than Anna over the past year without justification. (3) Michael made a $20,000 equipment purchase without consulting her. (4) She seeks dissolution of the partnership with: (a) 60% of the business value ($180,000 of an appraised $300,000), reflecting her greater contribution, (b) return of the $15,000 excess draws, or (c) buyout of Michael's interest for $120,000 (40% of appraised value less the disputed amounts).

Michael's position: (1) While Anna spends more hours at the restaurant, he handles crucial tasks like supplier negotiations, accounting, and maintenance that aren't as visible but equally valuable. (2) His additional draws were compensation for covering business expenses personally when cash flow was tight. (3) The equipment purchase was necessary and urgent - a broken refrigerator - and he couldn't reach Anna at the time. (4) If dissolution is necessary, he wants: (a) 50/50 split as originally agreed, (b) right to purchase the business himself for fair market value, or (c) force sale of the business with equal distribution after debts."""
    }
}


def get_template(template_id: str) -> Dict[str, str]:
    """
    Get a trial template by ID.
    
    Args:
        template_id: Template identifier
        
    Returns:
        Template dictionary or empty dict if not found
    """
    return TRIAL_TEMPLATES.get(template_id, {})


def list_templates() -> List[Dict[str, str]]:
    """
    Get list of all available templates.
    
    Returns:
        List of template metadata
    """
    return [
        {
            'id': tid,
            'name': template['name'],
            'category': template['category'],
            'description': template['description']
        }
        for tid, template in TRIAL_TEMPLATES.items()
    ]


def get_categories() -> List[str]:
    """
    Get list of all template categories.
    
    Returns:
        List of unique categories
    """
    return list(set(t['category'] for t in TRIAL_TEMPLATES.values()))
