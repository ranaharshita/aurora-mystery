"""
case_data.py - Authoritative Case Facts for The Vanishing Aurora Diamond
"""

CASE_TITLE = "The Vanishing Aurora Diamond"

CASE_SUMMARY = """
Northbridge Museum confirmed the Aurora Diamond inside a locked glass display case at 8:00 PM.
At 8:20 PM, a power failure darkened the gallery for four minutes, ending at 8:24 PM.
At 8:30 PM, staff discovered that the diamond was missing.
The display glass was unbroken and showed no sign of forced entry.
The electronic lock is battery-backed and continues recording valid-card access during a power failure.
"""

SUSPECTS = {
    "Lena Ortiz": {
        "role": "Facilities coordinator",
        "motive": "Recently denied a promotion.",
        "statement": "Says she restarted the basement generator from approximately 8:19 to 8:26.",
        "key_facts": [
            "Her card opened the basement at 8:20.",
            "She had crossed a wet courtyard earlier while inspecting an exterior door."
        ]
    },
    "Theo Park": {
        "role": "Event host",
        "motive": "Wanted publicity for the museum event.",
        "statement": "Says he remained on stage.",
        "key_facts": [
            "Camera shows him continuously from 8:15 to 8:29.",
            "He says he did not enter the Grand Gallery during the blackout."
        ]
    },
    "Arjun Vale": {
        "role": "Archivist",
        "motive": "Has large private debt.",
        "statement": "Says he worked in the archive throughout the blackout and his access card remained in the jacket he left inside the archive.",
        "key_facts": [
            "His card opened the archive at 8:12.",
            "His card opened the display case at 8:23.",
            "At 8:25, camera shows Arjun leaving the archive carrying a flat catalogue folder.",
            "The camera does not show what is inside the folder."
        ]
    },
    "Sofia Reed": {
        "role": "Journalist",
        "motive": "Wanted an exclusive news story.",
        "statement": "Says she interviewed visitors in the lobby during the blackout.",
        "key_facts": [
            "Three guests independently remember speaking with Sofia during part or all of the blackout.",
            "None reports seeing her enter the gallery."
        ]
    }
}

EVIDENCE_ITEMS = {
    "A": {
        "title": "Electronic lock specification",
        "description": "Valid-card access is recorded during a power failure because the lock has a battery."
    },
    "B": {
        "title": "Display-case access log",
        "description": "Arjun Vale's card opened the display case at 8:23 PM."
    },
    "C": {
        "title": "Arjun's statement",
        "description": "He says his card remained in his jacket inside the archive."
    },
    "D": {
        "title": "Camera image at 8:25 PM",
        "description": "Arjun leaves the archive carrying a flat catalogue folder. The image does not show its contents."
    },
    "E": {
        "title": "Fiber examination",
        "description": "Blue velvet fibers were found inside the folder. The display cushion is made from blue velvet."
    },
    "F": {
        "title": "Muddy shoeprint",
        "description": "A print near the case matches Lena's boot size. Records show she inspected the case after crossing a wet courtyard earlier that afternoon."
    },
    "G": {
        "title": "Insurance record",
        "description": "If the diamond remains missing, insurance pays the museum rather than any named suspect."
    }
}

def get_formatted_case_data(include_evidence_e: bool = True) -> str:
    """Formats the complete authoritative case facts for LLM prompts."""
    output = []
    output.append(f"=== CASE: {CASE_TITLE} ===")
    output.append("\n--- BACKGROUND & TIMELINE FACTS ---")
    output.append(CASE_SUMMARY.strip())
    
    output.append("\n--- SUSPECTS ---")
    for name, details in SUSPECTS.items():
        output.append(f"\nSuspect: {name} ({details['role']})")
        output.append(f"  Motive: {details['motive']}")
        output.append(f"  Statement: {details['statement']}")
        output.append("  Key Facts:")
        for fact in details["key_facts"]:
            output.append(f"   - {fact}")
            
    output.append("\n--- EVIDENCE LIST ---")
    for code, ev in EVIDENCE_ITEMS.items():
        if code == "E" and not include_evidence_e:
            output.append(f"Evidence {code}: [REMOVED FOR THIS INVESTIGATION RUN]")
            continue
        output.append(f"Evidence {code} ({ev['title']}): {ev['description']}")
        
    return "\n".join(output)
